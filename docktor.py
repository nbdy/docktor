from argparse import ArgumentParser
from docktor import Server


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", type=str)
    parser.add_argument("--port", default=1337, type=int)
    parser.add_argument("-i", "--instances", default=2, type=int)
    parser.add_argument("--control-password", default="docktor", type=str)
    a = parser.parse_args()

    server = Server(a.instances, a.host, a.port, control_password=a.control_password)
    server.run()
