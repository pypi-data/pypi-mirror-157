"""pyWorxCloud definition."""
from __future__ import annotations

import base64
import contextlib
import json
import sys
import tempfile
import time
from datetime import datetime, timedelta
from typing import Any

import OpenSSL.crypto
import paho.mqtt.client as mqtt
from paho.mqtt.client import connack_string, error_string

from .api import LandroidCloudAPI
from .clouds import CloudType
from .const import UNWANTED_ATTRIBS
from .day_map import DAY_MAP
from .events import EventHandler, LandroidEvent
from .exceptions import AuthorizationError, MQTTException
from .helpers import convert_to_time, get_logger
from .utils import (
    MQTT,
    Battery,
    Blades,
    DeviceCapability,
    DeviceHandler,
    Location,
    Orientation,
    ScheduleType,
    Statistic,
    Weekdays,
)
from .utils.schedules import TYPE_TO_STRING

if sys.version_info < (3, 10, 0):
    sys.exit("The pyWorxcloud module requires Python 3.10.0 or later")


class WorxCloud(dict):
    """
    Worx by Landroid Cloud connector.

    Used for handling API connection to Worx, Kress and Landxcape devices which are cloud connected.

    This uses a reverse engineered API protocol, so no guarantee that this will keep working.
    There are no public available API documentation available.
    """

    __device: str | None = None

    def __init__(
        self,
        username: str,
        password: str,
        cloud: CloudType.WORX
        | CloudType.KRESS
        | CloudType.LANDXCAPE
        | CloudType.FERREX
        | str = CloudType.WORX,
        index: int = 0,
        verify_ssl: bool = True,
    ) -> None:
        """
        Initialize :class:WorxCloud class and set default attribute values.

        1. option for connecting and printing the current states from the API, using :code:`with`

        .. testcode::
        from pyworxcloud import WorxCloud
        from pprint import pprint

        with WorxCloud("your@email","password","worx", 0, False) as cloud:
            pprint(vars(cloud))

        2. option for connecting and printing the current states from the API, using :code:`connect` and :code:`disconnect`

        .. testcode::
        from pyworxcloud import WorxCloud
        from pprint import pprint

        cloud = WorxCloud("your@email", "password", "worx")

        # Initialize connection
        auth = cloud.authenticate()

        if not auth:
            # If invalid credentials are used, or something happend during
            # authorize, then exit
            exit(0)

        # Connect to device with index 0 (devices are enumerated 0, 1, 2 ...)
        # and do not verify SSL (False)
        cloud.connect(0, False)

        # Read latest states received from the device
        cloud.update()

        # Print all vars and attributes of the cloud object
        pprint(vars(cloud))

        # Disconnect from the API
        cloud.disconnect()

        For further information, see the Wiki for documentation: https://github.com/MTrab/pyworxcloud/wiki

        Args:
            username (str): Email used for logging into the app for your device.
            password (str): Password for your account.
            cloud (CloudType.WORX | CloudType.KRESS | CloudType.LANDXCAPE | CloudType.FERREX | str, optional): The CloudType matching your device. Defaults to CloudType.WORX.
            index (int, optional): Device number if more than one is connected to your account (starting from 0 representing the first added device). Defaults to 0.
            verify_ssl (bool, optional): Should this module verify the API endpoint SSL certificate? Defaults to True.

        Raise:
            TypeError: Error raised if invalid CloudType was specified.
        """
        self._worx_mqtt_client_id = None

        if not isinstance(
            cloud,
            (
                type(CloudType.WORX),
                type(CloudType.KRESS),
                type(CloudType.LANDXCAPE),
                type(CloudType.FERREX),
            ),
        ):
            try:
                cloud = getattr(CloudType, cloud.upper())
            except AttributeError:
                raise TypeError(
                    "Wrong type specified, valid types are: worx, landxcape, kress, ferrex"
                )

        self._api = LandroidCloudAPI(username, password, cloud)

        self._username = username
        self._cloud = cloud
        self._auth_result = False
        self._log = get_logger("pyworxcloud")
        self._raw = None

        self._save_zones = None
        self._verify_ssl = verify_ssl
        self._events = EventHandler()

        # Dict of devices, identified by name
        self.devices = {}

        self.mqtt = None

    def __enter__(self):
        """Default actions using with statement."""
        if isinstance(self._dev_id, type(None)):
            self._dev_id = 0

        self.authenticate()

        self.connect(self._dev_id, self._verify_ssl)
        self.update()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Called on end of with statement."""
        self.disconnect()

    def authenticate(self) -> bool:
        """Authenticate against the API."""
        self._log.debug("Authenticating %s", self._username)

        auth = self._authenticate()
        if auth is False:
            self._auth_result = False
            self._log.debug("Authentication for %s failed!", self._username)
            raise AuthorizationError("Unauthorized")

        self._auth_result = True
        self._log.debug("Authentication for %s successful", self._username)

        return True

    def update_attribute(
        self, device: str, attr: str | None, key: str, value: Any
    ) -> None:
        """Used as callback to update value."""
        chattr = self.devices[device]
        if not isinstance(attr, type(None)):
            for level in attr.split(";;"):
                if hasattr(chattr, level):
                    chattr = getattr(chattr, level)
                else:
                    chattr = chattr[level]

        if hasattr(chattr, key):
            setattr(chattr, key, value)
        elif isinstance(chattr, dict):
            chattr.update({key: value})

    def set_callback(self, event: LandroidEvent, func: Any) -> None:
        """Set callback which is called when data is received.

        Args:
            event: LandroidEvent for this callback
            func: Function to be called.
        """
        self._events.set_handler(event, func)

    def disconnect(self) -> None:
        """Close API connections."""
        if self.mqtt.connected:
            topic = self.mqtt.topics["out"]
            self.mqtt.unsubscribe(topic)
            self.mqtt.disconnect()
            self.mqtt.loop_stop()

    def connect(
        self,
        device: str | None = None,
        verify_ssl: bool = True,
        pahologger: bool = False,
    ) -> bool:
        """Connect to the cloud service endpoint

        Args:
            index (int | None, optional): Device number to connect to. Defaults to None.
            verify_ssl (bool, optional): Should we verify SSL certificate. Defaults to True.

        Returns:
            bool: True if connection was successful, otherwise False.
        """
        if not isinstance(device, type(None)):
            self.__device = device

        self._fetch()

        # setup MQTT handler
        self.mqtt = MQTT(
            self.devices,
            self._worx_mqtt_client_id,
            protocol=mqtt.MQTTv311,
        )

        self.mqtt.endpoint = self._endpoint
        self.mqtt.reconnect_delay_set(60, 300)

        self.mqtt.on_message = self._forward_on_message
        self.mqtt.on_connect = self._on_connect
        self.mqtt.on_disconnect = self._on_disconnect

        if pahologger:
            mqttlog = self._log.getChild("PahoMQTT")
            self.mqtt.on_log = self._on_log
            self.mqtt.enable_logger(mqttlog)
            self.mqtt.logger = True

        with self._get_cert() as cert:
            self.mqtt.tls_set(certfile=cert)

        if not verify_ssl:
            self.mqtt.tls_insecure_set(True)

        self.mqtt.connect(self.mqtt.endpoint, port=8883, keepalive=600)

        self.mqtt.loop_start()

        # self.mqttdata["messages"]["raw"].update(
        #     {
        #         "in": self.raw_messages_in,
        #         "out": self.raw_messages_out,
        #     }
        # )
        # self.mqttdata["messages"]["filtered"].update(
        #     {
        #         "in": self.messages_in,
        #         "out": self.messages_out,
        #     }
        # )
        # self.mqttdata["registered"] = self.mqtt_registered

        # Convert time strings to objects.
        for name, device in self.devices.items():
            convert_to_time(
                name, device, device.time_zone, callback=self.update_attribute
            )

        return True

    @property
    def auth_result(self) -> bool:
        """Return current authentication result."""
        return self._auth_result

    def _authenticate(self):
        """Authenticate the user."""
        auth_data = self._api.auth()

        try:
            self._api.set_token(auth_data["access_token"])
            self._api.set_token_type(auth_data["token_type"])

            self._api.get_profile()
            profile = self._api.data
            if profile is None:
                return False
            self._endpoint = profile["mqtt_endpoint"]
            self._worx_mqtt_client_id = "android-" + self._api.uuid
        except:  # pylint: disable=bare-except
            return False

    @contextlib.contextmanager
    def _get_cert(self):
        """Cet current certificate."""

        certresp = self._api.get_cert()

        with pfx_to_pem(certresp["pkcs12"]) as pem_cert:
            yield pem_cert

    def _forward_on_message(
        self,
        client,
        userdata,
        message,
        properties=None,  # pylint: disable=unused-argument
    ):
        """MQTT callback method definition."""
        logger = self._log.getChild("mqtt.message_received")
        topic = message.topic
        for name, topics in self.mqtt.topics.items():
            if topics["out"] == topic:
                break

        logger.debug(
            "Received MQTT message for %s - processing data %s",
            name,
            message.payload.decode("utf-8"),
        )

        # self._fetch()
        # self._mqtt_data = message.payload.decode("utf-8")

        while not self.devices[name].is_decoded:
            pass  # Await last dataset to be handled before sending a new into the handler

        msg = message.payload.decode("utf-8")
        if self.devices[name].raw_data == msg:
            self._log.debug("Data was already present and not changed.")
            return  # Data was identical, update was not needed

        self.devices[name].raw_data = msg
        self._decode_data(self.devices[name])
        self._events.call(
            LandroidEvent.DATA_RECEIVED, name=name, device=self.devices[name]
        )

    def _decode_data(self, device: DeviceHandler) -> None:
        """Decode incoming JSON data."""
        device.is_decoded = False

        logger = self._log.getChild("decode_data")
        logger.debug("Data decoding for %s started", device.name)

        if device.json_data:
            logger.debug("Found JSON decoded data: %s", device.json_data)
            data = device.json_data
        elif device.raw_data:
            logger.debug("Found raw data: %s", device.raw_data)
            data = json.loads(device._mqtt_data)
        else:
            device.is_decoded = True
            logger.debug("No valid data was found, skipping update for %s", device.name)
            return

        if "dat" in data:
            device.rssi = data["dat"]["rsi"]
            device.status.update(data["dat"]["ls"])
            device.error.update(data["dat"]["le"])

            device.zone.index = data["dat"]["lz"]

            device.locked = bool(data["dat"]["lk"])

            # Get battery info if available
            if "bt" in data["dat"]:
                if len(device.battery) == 0:
                    device.battery = Battery(data["dat"]["bt"])
                else:
                    device.battery.set_data(data["dat"]["bt"])
            # Get device statistics if available
            if "st" in data["dat"]:
                device.statistics = Statistic(data["dat"]["st"])

            # Get orientation if available.
            if "dmp" in data["dat"]:
                device.orientation = Orientation(data["dat"]["dmp"])

            # Check for extra module availability
            if "modules" in data["dat"]:
                if "4G" in data["dat"]["modules"]:
                    device.gps = Location(
                        data["dat"]["modules"]["4G"]["gps"]["coo"][0],
                        data["dat"]["modules"]["4G"]["gps"]["coo"][1],
                    )

            # Get remaining rain delay if available
            if "rain" in data["dat"]:
                device.rainsensor.triggered = bool(str(data["dat"]["rain"]["s"]) == "1")
                device.rainsensor.remaining = int(data["dat"]["rain"]["cnt"])

        if "cfg" in data:
            device.updated = data["cfg"]["dt"] + " " + data["cfg"]["tm"]
            device.rainsensor.delay = int(data["cfg"]["rd"])

            # Fetch wheel torque
            if "tq" in data["cfg"]:
                device.capabilities.add(DeviceCapability.TORQUE)
                device.torque = data["cfg"]["tq"]

            # Fetch zone information
            if "mz" in data["cfg"]:
                device.zone.starting_point = data["cfg"]["mz"]
                device.zone.indicies = data["cfg"]["mzv"]

                # Map current zone to zone index
                device.zone.current = device.zone.indicies[device.zone.index]

            # Fetch main schedule
            if "sc" in data["cfg"]:
                if "ots" in data["cfg"]["sc"]:
                    device.capabilities.add(DeviceCapability.ONE_TIME_SCHEDULE)
                if "distm" in data["cfg"]["sc"]:
                    device.capabilities.add(DeviceCapability.PARTY_MODE)

                device.partymode_enabled = bool(str(data["cfg"]["sc"]["m"]) == "2")

                device.schedules["active"] = bool(str(data["cfg"]["sc"]["m"]) == "1")
                device.schedules["time_extension"] = data["cfg"]["sc"]["p"]

                sch_type = ScheduleType.PRIMARY
                device.schedules.update({TYPE_TO_STRING[sch_type]: Weekdays()})

                for day in range(0, len(data["cfg"]["sc"]["d"])):
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "start"
                    ] = data["cfg"]["sc"]["d"][day][0]
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "duration"
                    ] = data["cfg"]["sc"]["d"][day][1]
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "boundary"
                    ] = bool(data["cfg"]["sc"]["d"][day][2])

                    time_start = datetime.strptime(
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "start"
                        ],
                        "%H:%M",
                    )

                    if isinstance(
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ],
                        type(None),
                    ):
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ] = "0"

                    duration = int(
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ]
                    )

                    duration = duration * (
                        1 + (int(device.schedules["time_extension"]) / 100)
                    )
                    end_time = time_start + timedelta(minutes=duration)

                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "end"
                    ] = end_time.time().strftime("%H:%M")

            # Fetch secondary schedule
            if "dd" in data["cfg"]["sc"]:
                sch_type = ScheduleType.SECONDARY
                device.schedules.update({TYPE_TO_STRING[sch_type]: Weekdays()})

                for day in range(0, len(data["cfg"]["sc"]["d"])):
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "start"
                    ] = data["cfg"]["sc"]["dd"][day][0]
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "duration"
                    ] = data["cfg"]["sc"]["dd"][day][1]
                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "boundary"
                    ] = bool(data["cfg"]["sc"]["dd"][day][2])

                    time_start = datetime.strptime(
                        data["cfg"]["sc"]["dd"][day][0],
                        "%H:%M",
                    )

                    if isinstance(
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ],
                        type(None),
                    ):
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ] = "0"

                    duration = int(
                        device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                            "duration"
                        ]
                    )

                    duration = duration * (
                        1 + (int(device.schedules["time_extension"]) / 100)
                    )
                    end_time = time_start + timedelta(minutes=duration)

                    device.schedules[TYPE_TO_STRING[sch_type]][DAY_MAP[day]][
                        "end"
                    ] = end_time.time().strftime("%H:%M")

        convert_to_time(
            device.name, device, device.time_zone, callback=self.update_attribute
        )

        device.is_decoded = True
        logger.debug("Data for %s was decoded", device.name)

    def _on_log(self, client, userdata, level, buf):
        """Capture MQTT log messages."""
        logger = self._log.getChild("mqtt.log")
        logger.debug("MQTT log message received: %s", buf)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata,
        flags,
        rc,
        properties=None,  # pylint: disable=unused-argument,invalid-name
    ):
        """MQTT callback method."""
        logger = self._log.getChild("mqtt.connected")
        logger.debug(connack_string(rc))
        if rc == 0:
            for name, topics in self.mqtt.topics.items():
                topic = topics["out"]
                logger.debug(
                    "MQTT for %s connected, subscribing to topic '%s'", name, topic
                )
                client.subscribe(topic)

            for name, device in self.devices.items():
                device.mqtt = self.mqtt
                if isinstance(device.raw_data, type(None)):
                    logger.debug(
                        "MQTT chached data not found for %s - requesting now", name
                    )

                    mqp = device.mqtt.send(name, force=True)
                    if isinstance(mqp, type(None)):
                        raise MQTTException("Couldn't send request to MQTT server.")

                    while not mqp.is_published:
                        pass
                        # time.sleep(0.1)

            logger.debug("Setting MQTT connected flag TRUE")
            self.mqtt.connected = True
            self._events.call(LandroidEvent.MQTT_CONNECTION, state=self.mqtt.connected)
        else:
            logger.debug("Setting MQTT connected flag FALSE")
            self.mqtt.connected = False
            self._events.call(LandroidEvent.MQTT_CONNECTION, state=self.mqtt.connected)

            raise MQTTException(connack_string(rc))

    def _on_disconnect(
        self,
        client,
        userdata,
        rc,
        properties=None,  # pylint: disable=unused-argument,invalid-name
    ):
        """MQTT callback method."""
        logger = self._log.getChild("mqtt.disconnected")
        if rc > 0:
            if rc == 7:
                if not self.mqtt.connected:
                    raise MQTTException(
                        "Unexpected MQTT disconnect - were you perhaps banned?"
                    )

            if self.mqtt.connected:
                logger.debug("MQTT connection was lost! (%s)", error_string(rc))

            logger.debug("Setting MQTT connected flag FALSE")
            self.mqtt.connected = False
            self._events.call(LandroidEvent.MQTT_CONNECTION, state=self.mqtt.connected)
            for name, topics in self.mqtt.topics.items():
                topic = topics["out"]
                logger.debug(
                    "MQTT for %s disconnected, unsubscribing from topic '%s'",
                    name,
                    topic,
                )
                client.unsubscribe(topic)

    def _fetch(self) -> None:
        """Fetch base API information."""
        self._api.get_products()

        for product in self._api.data:
            if self.__device:
                if product["name"] != self.__device:
                    continue

            device = DeviceHandler(self._api, product)
            self.devices.update({product["name"]: device})

            # device["accessories"] = None
            # for attr, val in product.items():
            # if attr == "accessories":
            #     device["accessories"] = val
            # else:
            #     setattr(device, str(attr), val)

    def enumerate(self) -> int:
        """Fetch number of devices connected to the account.

        Returns:
            int: Represents the number of available devices in the account, starting from 0 as the first devices associated with the account.
        """
        self._api.get_products()
        products = self._api.data
        self._log.debug(
            "Enumeration found %s devices on account %s", len(products), self._username
        )
        return len(products)

    def update(self) -> None:
        """Retrive current device status."""
        for name, device in self.devices.items():
            status = self._api.get_status(device.serial_number)
            status = str(status).replace("'", '"')

            while not device.is_decoded:
                pass  # Await previous dataset to be handled before sending a new into the handler.

            device.raw_data = status
            self._decode_data(device)


@contextlib.contextmanager
def pfx_to_pem(pfx_data):
    """Decrypts the .pfx file to be used with requests."""
    with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as t_pem:
        f_pem = open(t_pem.name, "wb")
        p12 = OpenSSL.crypto.load_pkcs12(base64.b64decode(pfx_data), "")
        f_pem.write(
            OpenSSL.crypto.dump_privatekey(
                OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()
            )
        )
        f_pem.write(
            OpenSSL.crypto.dump_certificate(
                OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()
            )
        )
        certauth = p12.get_ca_certificates()
        if certauth is not None:
            for cert in certauth:
                f_pem.write(
                    OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
                )
        f_pem.close()
        yield t_pem.name
