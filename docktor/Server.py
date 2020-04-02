from sanic import Sanic, response

from docktor import Manager


class Server(object):
    app = None
    manager = None
    host = None
    port = None

    def __init__(self, instances=2, host="127.0.0.1", port=1337, **kwargs):
        self.app = Sanic(__name__)
        self.host = host
        self.port = port
        self.manager = Manager(instances, control_password=kwargs.get("control_password") or "docktor",
                               debug=kwargs.get("debug") or False, directory=kwargs.get("data_directory"))

        @self.app.route("/api/instances")
        def api_instances(req):
            return response.json(self.manager.get_containers())

        @self.app.route("/api/rotate/<path:path>")
        def api_rotate_one(req, path):
            return response.json({"success": self.manager.change_container_identity(path)})

        @self.app.route("/api/rotate")
        def api_rotate_all(req):
            return response.json({"success": self.manager.change_all_identities()})

        @self.app.listener('after_server_stop')
        async def after_stop(app, loop):
            self.manager.stop()

    def run(self):
        self.manager.start()
        self.app.run(self.host, self.port, debug=True)
