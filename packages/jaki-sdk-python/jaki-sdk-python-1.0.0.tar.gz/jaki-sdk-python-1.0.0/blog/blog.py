import threading

from twisted.internet import reactor
from twisted.internet.error import ReactorAlreadyRunning


class PrintBlog(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        try:
            print("开始 reactor")
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            pass