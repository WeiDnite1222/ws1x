from client import Manage as ClientSide
from server import Manage as ServerSide
import argparse


def main():
    parser = argparse.ArgumentParser(description='SpaceNET Server Management')

    parser.add_argument("-side", "--side", help="Current mode (client or server)", default="client")
    # parser.add_argument("-window", "--window", help="Display Window (Client-Only)", action='store_true')

    args = parser.parse_args()

    currentSide = None

    if args.side.lower() == "client":
        currentSide = ClientSide
    elif args.side.lower() == "server":
        currentSide = ServerSide
    else:
        print("Invalid side name {}".format(args.side))

    if currentSide is None:
        print("Could not determine current side. Exiting...")
        return -1

    elif currentSide == ClientSide:
        print("Starting client...")
        ClientSide()
    elif currentSide == ServerSide:
        print("Starting server...")
        ServerSide()

    return 0

if __name__ == '__main__':
    main()

