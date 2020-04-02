import docker
from time import sleep
from loguru import logger
from threading import Thread
from stem.control import Controller
from stem import Signal


class Manager(Thread):
    daemon = True
    do_run = False
    debug = False

    client = None
    image = None
    instances = 1
    containers = []

    control_password = None

    def get_image(self, tag):
        """
        gets image from docker client
        :param tag: image tag
        :return: Image object or None if Image could not be found
        """
        try:
            return self.client.images.get(tag)
        except Exception as e:
            if self.debug:
                logger.exception(e)
            return None

    def __init__(self, instances=16, control_password="docktor", directory="data", tag="docktor", debug=False):
        """
        initializes Manager object
        :param instances: number of desired instances
        :param control_password: tor control password for ALL containers
        :param directory: data directory which contains the Dockerfile and so on
        :param tag: Container tag
        :param debug: be more verbose
        """
        Thread.__init__(self)
        self.debug = debug
        if self.debug:
            logger.debug("using data directory: {0}".format(directory))
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
        """
        gets container by name from docker
        :param name: container name
        :return: Container object or None if Container does not exist
        """
        try:
            return self.client.containers.get(name)
        except Exception as e:
            if self.debug:
                logger.exception(e)
            return None

    def _create_containers(self):
        """
        creates containers
        :return: None
        """
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
        """
        calls .start() on all containers
        :return: None
        """
        for c in self.containers:
            logger.info("running container '{0}'".format(c.name))
            c.start()

    def get_port(self, info, port):
        """
        does not take a docker.Container object, but the dict created in get_containers
        :param info: ^
        :param port: ex: 8118/tcp
        :return: integer of the port
        """
        if self.debug:
            logger.debug("getting forwarded port for {0}".format(port))
            logger.debug(info)
        for p in info["ports"].items():
            if p[0] == port:
                return int(p[1])
        return None

    def change_identity(self, port):
        """
        changes the identity (ip) of the corresponding container
        :param port: control port of container
        :return: returns True when done
        """
        with Controller.from_port(port=int(port)) as c:
            c.authenticate(self.control_password)
            if not c.is_newnym_available():
                nnw = c.get_newnym_wait()
                logger.info("sleeping {0} until next newnym is available".format(nnw))
                sleep(nnw)
            c.signal(Signal.NEWNYM)
            c.close()
        return True

    def change_container_identity(self, name):
        """
        changes container identity
        :param name: name of container
        :return: True when identity was changed or False if container could not be found
        """
        for i in self.get_containers():
            if i["name"] == name:
                return self.change_identity(i["ports"]["9051/tcp"])
        return False

    def change_all_identities(self):
        """
        changes identities of all containers
        :return: True when done
        """
        for i in self.get_containers():
            self.change_identity(i["ports"]["9051/tcp"])
        return True

    def get_containers(self):
        """
        :return: dict list of all containers
        """
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
        """
        waits until all tor instances in all containers are bootstrapped
        :return: None
        """
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
        """
        creates and runs containers
        :return: None
        """
        self._create_containers()
        self._run_containers()

    @staticmethod
    def work():
        """
        does nothing
        :return: None
        """
        sleep(0.42)

    def on_stop(self):
        """
        stops / kills containers
        :return: None
        """
        logger.info("stopping containers")
        for c in self.containers:
            c.kill()

    def run(self):
        """
        calls on_run / work / on_stop
        :return: None
        """
        self.on_run()
        while self.do_run:
            self.work()
        self.on_stop()

    def stop(self):
        """
        sets do_run to false (basically stops the manager)
        :return: None
        """
        self.do_run = False
