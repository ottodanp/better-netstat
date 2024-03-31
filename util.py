from os import system, name, popen
from typing import List

from psutil import net_connections, Process

from net import Connection


class Colours:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    CLEAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    YELLOW = '\033[33m'


PORTS = {
    "http": 80,
    "https": 443,
    "ftp": 21,
    "ssh": 22,
    "telnet": 23,
    "smtp": 25,
    "dns": 53,
    "dhcp": 67,
    "tftp": 69,
    "http-alt": 8080,
    "pop3": 110,
    "nntp": 119,
    "ntp": 123,
    "imap": 143,
}

STATES = {
    "ESTABLISHED": f"{Colours.GREEN}ESTABLISHED{Colours.CLEAR}",
    "LISTEN": f"{Colours.CYAN}LISTENING{Colours.CLEAR}",
    "TIME_WAIT": f"{Colours.BLUE}TIME_WAIT{Colours.CLEAR}",
    "CLOSE_WAIT": f"{Colours.BLUE}CLOSE_WAIT{Colours.CLEAR}",
    "SYN_SENT": f"{Colours.GREEN}SYN_SENT{Colours.CLEAR}",
    "SYN_RECEIVED": f"{Colours.GREEN}SYN_RECEIVED{Colours.CLEAR}",
    "FIN_WAIT1": f"{Colours.BLUE}FIN_WAIT_1{Colours.CLEAR}",
    "FIN_WAIT2": f"{Colours.BLUE}FIN_WAIT_2{Colours.CLEAR}",
    "CLOSED": f"{Colours.FAIL}CLOSED{Colours.CLEAR}",
    "LAST_ACK": f"{Colours.FAIL}LAST_ACK{Colours.CLEAR}",
    "CLOSING": f"{Colours.FAIL}CLOSING{Colours.CLEAR}",
    "UNKNOWN": f"{Colours.FAIL}UNKNOWN{Colours.CLEAR}",
    "NONE": f"",
    "None": "None"
}

PROTOCOLS = {
    "TCP": f"{Colours.YELLOW}TCP{Colours.CLEAR}",
    "UDP": f"{Colours.BLUE}UDP{Colours.CLEAR}"
}

PROTOCOL_NUMBERS = {
    1: "TCP",
    2: "UDP",
}

RELATIONSHIPS = {
    "LOCAL": f"{Colours.GREEN}LOCAL{Colours.CLEAR}",
    "REMOTE": f"{Colours.BLUE}REMOTE{Colours.CLEAR}",
    "UNKNOWN": f"{Colours.FAIL}UNKNOWN{Colours.CLEAR}",
    "LISTENER": f"{Colours.CYAN}LISTENER{Colours.CLEAR}"
}

DIRECTIONS = {
    "INCOMING": f"{Colours.GREEN}INCOMING{Colours.CLEAR}",
    "OUTGOING": f"{Colours.BLUE}OUTGOING{Colours.CLEAR}",
    "UNKNOWN": f"{Colours.FAIL}UNKNOWN{Colours.CLEAR}"
}

UNKNOWN_ADDRESSES = ["-1", "*", "0.0.0.0"]
LOOPBACKS = ["127.", "192.168", "10."]


def addr_relationship(address: str) -> str:
    if address in UNKNOWN_ADDRESSES:
        return "UNKNOWN"

    if any([address.startswith(s) for s in LOOPBACKS]):
        return "LOCAL"

    if address.startswith("172."):
        parts = address.split(".")
        if 16 <= int(parts[1]) <= 31:
            return "LOCAL"

    return "REMOTE"


def sort_connections(connections: List[Connection], protocol: str) -> List[Connection]:
    return sorted([c for c in connections if c.protocol == protocol], key=lambda x: x.process_name)


def get_netstat() -> List[Connection]:
    connections = net_connections()
    return [Connection(protocol=PROTOCOL_NUMBERS.get(conn.type),
                       local_address=conn.laddr.ip,
                       foreign_address=conn.raddr.ip if conn.raddr else "",
                       local_port=conn.laddr.port,
                       foreign_port=conn.raddr.port if conn.raddr else -1,
                       state=conn.status,
                       pid=conn.pid,
                       process=Process(conn.pid) if conn.pid else None)
            for conn in connections if PROTOCOL_NUMBERS.get(conn.type) is not None]


def clear():
    system('cls' if name == 'nt' else 'clear')


def maximize_terminal():
    if name == 'posix':
        rows, cols = popen('stty size', 'r').read().split()
        system(f"printf '\033[8;{rows};{cols}t'")
    elif name == 'nt':
        system('mode con cols=9999 lines=9999')
