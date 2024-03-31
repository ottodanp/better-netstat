from threading import Thread
from time import sleep
from typing import List

import pyshark
from pyshark.packet.packet import Packet

from net import get_netstat, Connection
from util import clear, maximize_terminal, display_connections, display_loop

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started", "Total Interactions", "Total Data"]


class NetworkMonitor:
    _active_connections: List[Connection]
    _sniffer_thread: Thread
    _connection_update_thread: Thread
    _interface: str

    def __init__(self, interface: str = 'WiFi'):
        self._interface = interface
        cap = pyshark.LiveCapture(interface=self._interface)
        self._sniffer_thread = Thread(target=cap.apply_on_packets, args=(self._packet_callback,))
        self._connection_update_thread = Thread(target=self._connection_update_thread)
        self._active_connections = []

    def start(self) -> "NetworkMonitor":
        self._connection_update_thread.start()
        self._sniffer_thread.start()

        return self

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
            return
        source_ip = packet.ip.src
        destination_ip = packet.ip.dst

        for conn in self._active_connections:
            if conn.local_address == source_ip and conn.foreign_address == destination_ip:
                conn.total_interactions += 1
                conn.total_data += int(packet.length)
                break

    @property
    def active_connections(self) -> List[Connection]:
        return self._active_connections


def main(m: NetworkMonitor):
    display_loop(
        sleep_time=5,
        callback=lambda: display_connections(m.active_connections, DISPLAY_HEADERS)
    )


if __name__ == '__main__':
    maximize_terminal()
    clear()
    monitor = NetworkMonitor()
    main(monitor.start())
