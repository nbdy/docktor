import docker
from time import sleep
from loguru import logger
from threading import Thread
from stem.control import Controller
from stem import Signal


class Manager(Thread):
    do_run = False

    client = None
    image = None
    instances = 1
    containers = []
    controllers = []

    def get_image(self, tag):
        try:
            return self.client.images.get(tag)
        except:
            return None

    def __init__(self, instances=16, directory="./", tag="docktor"):
        Thread.__init__(self)
        self.instances = instances
        self.client = docker.from_env()
        self.image = self.get_image(tag)
        if self.image is None:
            logger.info("image '{0}' not found. building it.".format(tag))
            self.image = self.client.images.build(path=directory, tag=tag)[0]
            logger.info("build image '{0}'.".format(self.image.tags[0]))
        self.do_run = True

    def get_container(self, name):
        try:
            return self.client.containers.get(name)
        except:
            return None

    def _create_containers(self):
        c = 0
        for i in range(self.instances):
            name = self.image.tags[0].split(":")[0] + "-" + str(c)
            container = self.get_container(name)
            if container is None:
                logger.info("creating container '{0}'".format(name))
                container = self.client.containers.create(
                    self.image.tags[0],
                    name=name,
                    ports={
                        '9050/tcp': None,
                        '9051/tcp': None,
                        '8123/tcp': None,
                        '8118/tcp': None
                    },
                    detach=True,
                    auto_remove=True
                )
            self.containers.append(container)
            c += 1

    def _run_containers(self):
        for c in self.containers:
            c.start()

    '''
    does not take a docker.Container object, but the dict created in get_containers
    '''
    @staticmethod
    def get_port(info, port):
        for p in info.ports.items():
            print(p)
            if p[0] == port:
                return p[1]
        return None

    def change_identity(self, name):
        for i in self.get_containers():
            if i["name"] == name:
                with Controller.from_port(port=i["ports"]["9051/tcp"]) as c:
                    c.authenticate()
                    c.signal(Signal.NEWNYM)
                return True
        return False

    def get_containers(self):
        r = []
        for c in self.containers:
            c.reload()
            info = {
                "id": c.id,
                "short_id": c.short_id,
                "name": c.name,
                "status": c.status,
                "ports": {}
            }
            for p in c.ports.items():
                info["ports"][p[0]] = p[1][0]["HostPort"]
            r.append(info)
        return r

    def _check_containers(self):
        for c in self.containers:
            c.reload()
            print(c.name + ":")
            print("\tstatus:", c.status)
            if b"Bootstrapped 100% (done): Done" in c.logs():
                print("\ttor: bootstrapped")
            elif b"stopped: tor" in c.logs():
                print("\ttor: stopped")
            else:
                print("\ttor: starting")

    def on_run(self):
        self._create_containers()
        self._run_containers()

    def work(self):
        # self._check_containers()
        sleep(10)

    def on_stop(self):
        for c in self.containers:
            c.kill()
        self._check_containers()

    def run(self):
        self.on_run()
        while self.do_run:
            self.work()
        self.on_stop()

    def stop(self):
        self.do_run = False
