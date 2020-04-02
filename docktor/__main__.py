from argparse import ArgumentParser
from docktor import Server

import os
import sys

sys.path.append(os.path.dirname(__file__))


def is_installed():
    return __file__.startswith("/usr/local")


def main():
    if is_installed():
        d = "/usr/local/lib/python3.7/dist-packages/docktor-0.42-py3.7.egg/docktor/data/"
    else:
        d = "data/"

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", type=str)
    parser.add_argument("--port", default=1337, type=int)
    parser.add_argument("-i", "--instances", default=2, type=int)
    parser.add_argument("--control-password", default="docktor", type=str)
    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--data-directory", default=d, type=str)
    a = parser.parse_args()

    server = Server(a.instances, a.host, a.port, control_password=a.control_password, debug=a.debug,
                    data_directory=a.data_directory)
    server.run()


if __name__ == '__main__':
    main()
