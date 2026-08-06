class AndroidBackend:

    def open_app(self, package):
        raise NotImplementedError

    def close_app(self, package):
        raise NotImplementedError

    def restart_app(self, package):
        raise NotImplementedError

