from __future__ import annotations
from typing import List

import asyncio
import asyncio_dgram
import socket
import logging
import json

from keba_kecontact.wallbox import Wallbox, WallboxDeviceInfo

_LOGGER = logging.getLogger(__name__)

UDP_PORT = 7090


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class KebaKeContact(metaclass=SingletonMeta):
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None, timeout: int = 3):
        """Constructor."""
        self._loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop() if loop is None else loop
        )

        self._stream = None
        self._wallbox_map = dict()

        self._timeout: int = timeout

        # discovery
        self._discovery_event: asyncio.Event = asyncio.Event()
        self._discovery_event.set()
        self._found_hosts: list[str] = []

        # device info fetching
        self._device_info_event: asyncio.Event = asyncio.Event()
        self._device_info_event.set()
        self._device_info_host: str = ""
        self._device_info: WallboxDeviceInfo | None = None

    async def discover_devices(self, broadcast_addr) -> List[str]:

        _LOGGER.info(f"Discover devices in {broadcast_addr}")

        self._discovery_event.clear()

        await self.send(broadcast_addr, "i")
        await asyncio.sleep(self._timeout)

        self._discovery_event.set()

        return self._found_hosts

    async def get_device_info(self, host: str) -> WallboxDeviceInfo:
        async with asyncio.Lock():
            _LOGGER.debug(f"Requesting device info from {host}")

            self._device_info_event.clear()
            self._device_info_host = host

            await self.send(host, "report 1")

            # Wait for positive response from host
            try:
                await asyncio.wait_for(
                    self._device_info_event.wait(), timeout=self._timeout
                )
            except asyncio.TimeoutError:
                _LOGGER.warning(
                    f"Wallbox at {host} has not replied within {self._timeout }s. Abort."
                )
                raise SetupError("Could not get device info")
            return self._device_info

    async def setup_wallbox(self, host: str, **kwargs) -> Wallbox:

        _LOGGER.debug(f"Start connecting to {host}")

        # check if wallbox is already configured
        if host in self._wallbox_map:
            _LOGGER.info(
                f"Wallbox at {host} already configured. Return existing object."
            )
            return self._wallbox_map.get(host)

        # Get device info and create wallbox object and add it to observing map
        device_info = await self.get_device_info(host)

        for wb in self.get_wallboxes():
            if wb.device_info.device_id == device_info.device_id:
                _LOGGER.info(
                    f"Found same wallbox (Serial: {device_info.device_id}{wb.device_info.host}) on a different IP address ({device_info.host}). Updating device info ..."
                )
                # re-write wallbox object
                wb.device_info = device_info

                # update map key               
                self._wallbox_map[host] = self._wallbox_map.pop(wb.device_info.host)

                return wb

        # Wallbox not known, thus create a new instance for it
        wallbox = Wallbox(self, device_info, self._loop, **kwargs)
        self._wallbox_map.update({host: wallbox})

        _LOGGER.info(
            f"{device_info.manufacturer} Wallbox (Serial: {device_info.device_id}) at {device_info.host} successfully connected."
        )
        return wallbox

    def remove_wallbox(self, host: str) -> None:
        if host in self._wallbox_map:
            wb = self.get_wallbox(host)
            wb.stop_periodic_request()
            self._wallbox_map.pop(host)
            _LOGGER.debug(f"Wallbox at {host} removed.")
        else:
            _LOGGER.warning(
                f"Wallbox at {host} could not be removed as it was not configured."
            )

    def get_wallboxes(self) -> list(Wallbox):
        return list(self._wallbox_map.values())

    def get_wallbox(self, host) -> Wallbox:
        return self._wallbox_map.get(host)

    async def send(self, host: str, payload: str) -> None:
        async with asyncio.Lock():
            _LOGGER.debug("Send %s to %s", payload, host)

            # Bind socket and start listening if not yet done
            if self._stream is None:
                self._stream = await asyncio_dgram.bind(("0.0.0.0", UDP_PORT))

                if hasattr(socket, "SO_BROADCAST"):
                    self._stream.socket.setsockopt(
                        socket.SOL_SOCKET, socket.SO_BROADCAST, 1
                    )

                self._loop.create_task(self._listen())
                _LOGGER.debug(
                    f"Socket binding created (0.0.0.0) and listening started on port {UDP_PORT}."
                )

            await self._stream.send(payload.encode("cp437", "ignore"), (host, UDP_PORT))
            await asyncio.sleep(0.1)  # Sleep for 100ms as given in the manual

    async def _listen(self) -> None:
        data, remote_addr = await self._stream.recv()  # Listen until something received
        self._loop.create_task(self._listen())  # Listen again
        self._loop.create_task(self._internal_callback(data, remote_addr))  # Callback

    async def _internal_callback(self, data, remote_addr) -> None:
        _LOGGER.debug(f"Datagram received from {remote_addr}: {data.decode()!r}")

        if not self._device_info_event.is_set():  # waiting for an ID 1 report
            report_1_json = json.loads(data.decode())
            device_info = WallboxDeviceInfo(remote_addr[0], report_1_json)

            if device_info:
                # Check if requested host
                if device_info.host == self._device_info_host:
                    self._device_info = device_info
                    self._device_info_host = ""
                    self._device_info_event.set()
                else:
                    _LOGGER.warning(
                        "Received device info from another host that was not requested"
                    )
        if not self._discovery_event.is_set():  # waiting for discovery ("i")
            if remote_addr not in self._found_hosts:
                if "Firmware" in data.decode():
                    self._found_hosts.append(remote_addr[0])
                    _LOGGER.debug(f"Found device with IP address {remote_addr}.")

        # callback datagram received on respective wallbox
        if remote_addr[0] not in self._wallbox_map:
            _LOGGER.debug("Received something from a not yet registered wallbox.")
        else:
            wb = self._wallbox_map.get(remote_addr[0])
            self._loop.create_task(wb.datagram_received(data))


class SetupError(Exception):
    """Error to indicate we cannot connect."""
