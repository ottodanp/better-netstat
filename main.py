from sys import argv

from util import maximize_terminal, clear


def start_network_monitor():
    from net_monitor import NetworkMonitor

    monitor = NetworkMonitor()
    monitor.start()


def start_connection_viewer():
    from active_connections import ConnectionViewer

    viewer = ConnectionViewer()
    viewer.start()


def main():
    maximize_terminal()
    try:
        var = argv[1]
        if var == "monitor":
            start_network_monitor()
        elif var == "viewer":
            start_connection_viewer()
        else:
            print("invalid input")

    except IndexError:
        i = input("n => Network Monitor\nv => Connection Viewer\n").lower()
        if i == "n":
            start_network_monitor()
        elif i == "v":
            start_connection_viewer()
        else:
            print("invalid input")


if __name__ == '__main__':
    main()
