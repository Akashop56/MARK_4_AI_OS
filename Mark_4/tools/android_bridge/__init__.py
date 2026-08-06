from .termux_backend import TermuxBackend


class AndroidBridge:


    def __init__(self):

        self.backend = TermuxBackend()



    def open_app(self, package):

        return self.backend.open_app(package)



    def launch(self, package):

        return self.open_app(package)



    def close_app(self, package):

        return self.backend.close_app(package)



    def restart_app(self, package):

        return self.backend.restart_app(package)



android = AndroidBridge()