from argparse import ArgumentParser
from os.path import split, join
from docktor import Server


def main():
    cdir, cfile = split(__file__)
    DATA_PATH = join(cdir, "data")

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", type=str)
    parser.add_argument("--port", default=1337, type=int)
    parser.add_argument("-i", "--instances", default=2, type=int)
    parser.add_argument("--control-password", default="docktor", type=str)
    parser.add_argument("--debug", default=False, action="store_true")
    parser.add_argument("--data-directory", default=DATA_PATH, type=str)
    a = parser.parse_args()

    server = Server(a.instances, a.host, a.port, control_password=a.control_password, debug=a.debug,
                    data_directory=a.data_directory)
    server.run()


if __name__ == '__main__':
    main()
