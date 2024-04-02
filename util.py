from os import system, name, popen
from time import sleep
from typing import List

from tabulate import tabulate

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
    "NONE": "",
    "None": ""
}

PROTOCOLS = {
    "TCP": f"{Colours.YELLOW}TCP{Colours.CLEAR}",
    "UDP": f"{Colours.BLUE}UDP{Colours.CLEAR}"
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


def sort_connections(connections: List[Connection], protocol: str) -> List[Connection]:
    return sorted([c for c in connections if c.protocol == protocol], key=lambda x: x.process_name)


def display_connections(connections: List[Connection], display_headers: List[str]) -> None:
    tcp_data = sort_connections(connections, "TCP")
    udp_data = sort_connections(connections, "UDP")
    data = map(lambda x: list(x), tcp_data + udp_data)
    n = []
    for d in data:
        d[0] = PROTOCOLS[d[0]]
        d[5] = STATES[d[5]]
        d[8] = RELATIONSHIPS[d[8]]
        if len(d) == 10:
            d[9] = DIRECTIONS[d[9]]
        n.append(d)
    print(tabulate(n, headers=display_headers), f"\nTotal Connections: {len(connections)}")


def clear():
    system('cls' if name == 'nt' else 'clear')


def maximize_terminal():
    if name == 'posix':
        rows, cols = popen('stty size', 'r').read().split()
        system(f"printf '\033[8;{rows};{cols}t'")
    elif name == 'nt':
        system('mode con cols=9999 lines=9999')


def display_loop(sleep_time: int, callback: callable, condition_callback: callable):
    while condition_callback():
        clear()
        callback()
        sleep(sleep_time)
