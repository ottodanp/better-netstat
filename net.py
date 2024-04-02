from datetime import datetime
from typing import Optional, List

from psutil import Process, net_connections

UNKNOWN_ADDRESSES = ["-1", "*", "0.0.0.0"]
LOOPBACKS = ["127.", "192.168", "10."]

PROTOCOL_NUMBERS = {
    1: "TCP",
    2: "UDP",
}

S_172 = "172"
N, U, R, L, LI, LIS = "", "UNKNOWN", "REMOTE", "LOCAL", "LISTEN", "LISTENER"
DATE_FORMAT, NULL_START_TIME = "%Y-%m-%d %H:%M:%S", "00:00:00"


def check_172_address(address: str) -> bool:
    parts = address.split(".")
    return False if parts[0] != S_172 \
        else True if len(parts) != 4 \
        else (16 <= int(parts[1]) <= 31) and (0 <= int(parts[2]) <= 255) and (0 <= int(parts[3]) <= 255)


def addr_relationship(address: str) -> str:
    return U if address in UNKNOWN_ADDRESSES \
        else L if any([address.startswith(s) for s in LOOPBACKS]) or (
            address.startswith(S_172) and check_172_address(address)) else R


class Connection:
    _protocol: str
    _local_address: str
    _foreign_address: str
    _local_port: int
    _foreign_port: int
    _state: str
    _process_name: str
    _pid: int
    _relationship: str
    _process: Optional[Process]
    _process_started: float
    _flag: str
    _total_interactions: int = 0
    _total_data: int = 0

    def __init__(self, protocol: str, local_address: str, foreign_address: str, local_port: int, foreign_port: int,
                 state: str, pid: int, process: Optional[Process]):
        self._protocol = protocol
        self._local_address = local_address
        self._foreign_address = foreign_address
        self._local_port = local_port
        self._foreign_port = foreign_port
        self._state = state
        self._pid = pid
        self._process = process
        self._relationship = LIS if self._state == LI else addr_relationship(self._foreign_address)
        self._process_name = self._process.name() if self._process else U
        self._process_started = float(self._process.create_time()) if self._process else -1
        self._flag = f"{self._local_address}:{self._local_port} -> {self._foreign_address}:{self._foreign_port}"

    def __iter__(self) -> List[str]:
        started = (
            datetime.fromtimestamp(self._process_started)
            .strftime(DATE_FORMAT)
            .split(" ")[1]
        ) if self._process_started != -1 else N
        started = N if started == NULL_START_TIME else started

        yield from [self._protocol, self._local_address, self._local_port, self._foreign_address,
                    self._foreign_port, self._state, self._pid, self._process_name,
                    self._relationship, started, self._total_interactions, self._total_data]

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def local_address(self) -> str:
        return self._local_address

    @property
    def foreign_address(self) -> str:
        return self._foreign_address

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def flag(self) -> str:
        return self._flag

    @property
    def total_interactions(self) -> int:
        return self._total_interactions

    @total_interactions.setter
    def total_interactions(self, value: int) -> None:
        self._total_interactions = value

    @property
    def total_data(self) -> int:
        return self._total_data

    @total_data.setter
    def total_data(self, value: int) -> None:
        self._total_data = value


def get_netstat() -> List[Connection]:
    connections = net_connections()
    return [Connection(protocol=PROTOCOL_NUMBERS.get(conn.type),
                       local_address=conn.laddr.ip,
                       foreign_address=conn.raddr.ip if conn.raddr else N,
                       local_port=conn.laddr.port,
                       foreign_port=conn.raddr.port if conn.raddr else -1,
                       state=conn.status,
                       pid=conn.pid,
                       process=Process(conn.pid) if conn.pid else None)
            for conn in connections if PROTOCOL_NUMBERS.get(conn.type) is not None]
