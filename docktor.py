import docker
from loguru import logger
from time import sleep
from threading import Thread
from sanic import Sanic, response


class Manager(Thread):
    do_run = False

    client = None
    image = None
    instances = 1
    containers = []

    def get_image(self, tag):
        try:
            return self.client.images.get(tag)
        except Exception as e:
            logger.info(e)
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
        except Exception as e:
            logger.info(e)
            return None

    def _run_containers(self):
        logger.info("running {0} containers".format(self.instances))
        c = 0
        for i in range(self.instances):
            name = self.image.tags[0].split(":")[0] + "-" + str(c)
            logger.info("going to run container '{0}'".format(name))
            self.containers.append(self.client.containers.run(
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
            ))
            c += 1

    def get_containers(self):
        r = []
        for c in self.containers:
            r.append({
                "id": c.id,
                "short_id": c.short_id,
                "name": c.name,
                "status": c.status,
                "ports": c.ports
            })
        logger.info(r)
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


class Server(object):
    app = None
    manager = None
    host = None
    port = None

    def __init__(self, host, port, instances=2):
        self.app = Sanic(__name__)
        self.host = host
        self.port = port
        self.manager = Manager(instances)

        @self.app.route("/api/instances")
        def api_instances(req):
            return response.json(self.manager.get_containers())

        @self.app.route("/api/rotate/<path:path>")
        def api_rotate(req, path):
            return response.json({})  # todo use stem to change ip for instance

        @self.app.route("/api/create/<path:path>")
        def api_create(req, path):
            return response.json({})  # todo create new instance

        @self.app.route("/api/kill/<path:path>")
        def api_kill(req, path):
            return response.json({})  # todo kill instance

        @self.app.listener('after_server_stop')
        async def after_stop(app, loop):
            self.manager.stop()

    def run(self):
        self.manager.start()
        self.app.run(self.host, self.port, debug=True)


if __name__ == '__main__':
    logger.info("starting")
    server = Server("127.0.0.1", 1337)
    server.run()
