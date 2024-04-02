import platform
from os import system, name, popen
from threading import current_thread, Lock
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
    RED = '\033[91m'
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
    "CLOSED": f"{Colours.RED}CLOSED{Colours.CLEAR}",
    "LAST_ACK": f"{Colours.RED}LAST_ACK{Colours.CLEAR}",
    "CLOSING": f"{Colours.RED}CLOSING{Colours.CLEAR}",
    "UNKNOWN": f"{Colours.RED}UNKNOWN{Colours.CLEAR}",
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
    "UNKNOWN": f"{Colours.RED}UNKNOWN{Colours.CLEAR}",
    "LISTENER": f"{Colours.CYAN}LISTENER{Colours.CLEAR}"
}

DIRECTIONS = {
    "INCOMING": f"{Colours.GREEN}INCOMING{Colours.CLEAR}",
    "OUTGOING": f"{Colours.BLUE}OUTGOING{Colours.CLEAR}",
    "UNKNOWN": f"{Colours.RED}UNKNOWN{Colours.CLEAR}"
}


def sort_connections(connections: List[Connection], protocol: str) -> List[Connection]:
    return sorted([c for c in connections if c.protocol == protocol], key=lambda x: x.process_name)


def add_formatting(dat: List) -> List:
    dat[0] = PROTOCOLS[dat[0]]
    dat[5] = STATES[dat[5]]
    dat[8] = RELATIONSHIPS[dat[8]]
    if len(dat) == 10:
        dat[9] = DIRECTIONS[dat[9]]
    return dat


def display_connections(connections: List[Connection], display_headers: List[str]) -> None:
    tcp_data = sort_connections(connections, "TCP")
    udp_data = sort_connections(connections, "UDP")
    data = map(lambda x: add_formatting(list(x)), tcp_data + udp_data)
    print(tabulate(data, headers=display_headers), f"\nTotal Connections: {len(connections)}")


def clear():
    system('cls' if name == 'nt' else 'clear')


def maximize_terminal():
    s = platform.system()
    if s in ["Darwin", "Linux"]:
        rows, cols = popen('stty size', 'r').read().split()
        system(f"printf '\033[8;{rows};{cols}t'")
    elif s == 'Windows':
        system('mode con cols=9999 lines=9999')


def display_loop(sleep_time: int, display_callback: callable, pause: Lock):
    thread = current_thread()
    while getattr(thread, "running", True):
        with pause:
            clear()
            display_callback()

        sleep(sleep_time)
