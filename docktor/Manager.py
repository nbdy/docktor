import docker
from time import sleep
from loguru import logger
from threading import Thread
from stem.control import Controller
from stem import Signal


class Manager(Thread):
    daemon = True
    do_run = False

    client = None
    image = None
    instances = 1
    containers = []

    control_password = None

    def get_image(self, tag):
        try:
            return self.client.images.get(tag)
        except:
            return None

    def __init__(self, instances=16, control_password="docktor", directory="./", tag="docktor"):
        Thread.__init__(self)
        self.instances = instances
        self.control_password = control_password
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
            logger.info("running container '{0}'".format(c.name))
            c.start()

    '''
    does not take a docker.Container object, but the dict created in get_containers
    :parameter info ^
    :parameter port ex: 8118/tcp
    :returns integer of the port
    '''
    @staticmethod
    def get_port(info, port):
        for p in info["ports"].items():
            if p[0] == port:
                return int(p[1])
        return None

    def change_identity(self, port):
        with Controller.from_port(port=int(port)) as c:
            c.authenticate(self.control_password)
            c.signal(Signal.NEWNYM)
        return True

    def change_container_identity(self, name):
        for i in self.get_containers():
            if i["name"] == name:
                return self.change_identity(i["ports"]["9051/tcp"])
        return False

    def change_all_identities(self):
        for i in self.get_containers():
            self.change_identity(i["ports"]["9051/tcp"])
        return True

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

    def wait_until_ready(self):
        logger.info("waiting till all containers are up and bootstrapped")
        while True:
            running_count = 0
            for c in self.containers:
                if b"Bootstrapped 100% (done): Done" in c.logs():
                    running_count += 1
            if running_count == len(self.containers):
                break
        logger.info("all containers should be up and ready")

    def on_run(self):
        self._create_containers()
        self._run_containers()

    def work(self):
        sleep(10)

    def on_stop(self):
        pass  # since we auto remove containers there is no need to do anything here atm

    def run(self):
        self.on_run()
        while self.do_run:
            self.work()
        self.on_stop()

    def stop(self):
        self.do_run = False
