from threading import Thread, Lock, Event
from time import sleep
from typing import List

import pyshark
from pyshark.packet.packet import Packet

from net import get_netstat, Connection
from util import display_loop, display_connections

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started", "Total Interactions", "Total Data"]

pause = Lock()


class NetworkMonitor:
    _active_connections: List[Connection]
    _sniffer_thread: Thread
    _connection_update_thread: Thread
    _display_thread: Thread
    _interface: str
    _running: bool
    _stop_event: Event

    def __init__(self, interface: str = 'WiFi'):
        self._interface = interface
        self._stop_event = Event()
        cap = pyshark.LiveCapture(interface=self._interface)
        self._sniffer_thread = Thread(target=cap.apply_on_packets, args=(self._packet_callback,))
        self._sniffer_thread._stop_event = self._stop_event
        self._connection_update_thread = Thread(target=self._connection_update_thread)
        self._display_thread = Thread(target=display_loop, args=(5, self.display_callback, pause))
        self._running = True
        self._active_connections = []

    def display_callback(self) -> None:
        display_connections(self._active_connections, DISPLAY_HEADERS)

    def _input_listener(self):
        while self._running:
            i = input()
            if i == "q":
                self.stop()
                print("Shutting Down...")

            elif i == "p":
                print("Paused")
                with pause:
                    input("Press Enter to Resume")

    def _connection_update_thread(self) -> None:
        while True:
            self._update_connections()
            sleep(5)

    def _update_connections(self) -> None:
        new = get_netstat()
        new_flags = set([c.flag for c in new])
        active_flags = set([c.flag for c in self._active_connections])

        for c in new:
            if c.flag not in active_flags:
                self._active_connections.append(c)

        self._active_connections = [c for c in self._active_connections if c.flag in new_flags]

    def _packet_callback(self, packet: Packet) -> None:
        if not hasattr(packet, 'ip'):
            input(packet)
            return
        source_ip = packet.ip.src
        destination_ip = packet.ip.dst

        for conn in self._active_connections:
            if conn.local_address == source_ip and conn.foreign_address == destination_ip:
                conn.total_interactions += 1
                conn.total_data += int(packet.length)
                break

    def start(self) -> None:
        self._connection_update_thread.start()
        self._sniffer_thread.start()
        self._display_thread.start()
        self._input_listener()

    def stop(self) -> None:
        self._running = False
        self._stop_event.set()
        self._display_thread.running = False

    @property
    def active_connections(self) -> List[Connection]:
        return self._active_connections
