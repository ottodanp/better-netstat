import ctypes
from datetime import datetime
from threading import Thread
from time import sleep
from typing import List, Optional

import pyshark
from psutil import net_connections, Process
from pydantic import BaseModel, BaseConfig
from pyshark.packet.packet import Packet
from tabulate import tabulate

from util import *


class Connection(BaseModel):
    protocol: str
    local_address: str
    foreign_address: str
    local_port: int
    foreign_port: int
    state: str
    process_name: str
    pid: int
    relationship: str
    process: Optional[Process]
    process_started: Optional[float]
    flag: str
    total_interactions: int = 0
    total_data: int = 0

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.relationship = "LISTENER" if self.state == "LISTEN" else addr_relationship(self.foreign_address)
        self.process_name = self.process.name() if self.process else "UNKNOWN"
        self.process_started = float(self.process.create_time()) if self.process else -1
        self.flag = f"{self.local_address}:{self.local_port} -> {self.foreign_address}:{self.foreign_port}"

    def __iter__(self) -> List[str]:
        started = (
            datetime.fromtimestamp(self.process_started)
            .strftime("%Y-%m-%d %H:%M:%S")
            .split(" ")[1]
        ) if self.process_started != -1 else ""
        started = "" if started == "00:00:00" else started

        yield from [PROTOCOLS[self.protocol], self.local_address, self.local_port, self.foreign_address,
                    self.foreign_port, STATES[self.state], self.pid, self.process_name,
                    RELATIONSHIPS[self.relationship], started, self.total_interactions, self.total_data]


def sort_connections(connections: List[Connection], protocol: str) -> List[Connection]:
    return sorted([c for c in connections if c.protocol == protocol], key=lambda x: x.process_name)


def get_netstat() -> List[Connection]:
    connections = net_connections()
    res = []
    for conn in connections:
        pid = conn.pid
        protocol = PROTOCOL_NUMBERS.get(conn.type)
        if protocol is None:
            continue

        local_host, local_port = conn.laddr.ip, conn.laddr.port

        if conn.raddr:
            foreign_host, foreign_port = conn.raddr.ip, conn.raddr.port
        else:
            foreign_host, foreign_port = "", -1

        state = conn.status

        c = Connection(protocol=protocol, local_address=local_host, foreign_address=foreign_host,
                       local_port=local_port, foreign_port=foreign_port, state=state, pid=pid, process_name="",
                       relationship="UNKNOWN", process=Process(pid) if pid else None, process_started=-1, flag="")

        res.append(c)

    return res


class NetworkMonitor:
    _active_connections: List[Connection]
    _sniffer_thread: Thread
    _connection_update_thread: Thread

    def __init__(self):
        cap = pyshark.LiveCapture(interface='WiFi')
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
        new_flags = [c.flag for c in new]
        active_flags = [c.flag for c in self._active_connections]

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

    def display_data(self) -> None:
        headers = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started", "Total Interactions", "Total Data"]
        tcp_data = sort_connections(self._active_connections, "TCP")
        udp_data = sort_connections(self._active_connections, "UDP")
        data = map(lambda x: list(x), tcp_data + udp_data)
        print(tabulate(data, headers=headers), f"\nTotal Connections: {len(self._active_connections)}")


def display_connections(m: NetworkMonitor):
    while True:
        clear()
        m.display_data()
        sleep(5)


if __name__ == '__main__':
    maximize_terminal()
    clear()
    monitor = NetworkMonitor()
    display_connections(monitor.start())
