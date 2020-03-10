from sanic import Sanic, response

from . import Manager


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
            return response.json({"success": self.manager.change_identity(path)})

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