from websocket_server import WebsocketServer
import json
import threading
from logger import log


class Websocket():
    server = None

    def __init__(self, events):
        self.events = events

    def start(self, host='0.0.0.0', port=9001):
        self.server = self.__connect(host, port)

        # Start a new thread and keep the connection alive
        thread = threading.Thread(target=self.server.run_forever)
        thread.daemon = True
        thread.start()

    def __connect(self, host='0.0.0.0', port=9001):
        """
        Create a new websocket server and return it
        """
        server = WebsocketServer(port, host)
        server.set_fn_new_client(self.__client_connected)
        server.set_fn_client_left(self.__client_left)
        server.set_fn_message_received(self.__message_received)

        return server

    @staticmethod
    def __client_connected(client, server):
        """
        Called for every client connecting (after handshake)
        """
        log("New Client(%d) connected." % client['id'])

    @staticmethod
    def __client_left(client, server):
        """
        Called for every client disconnecting
        """
        log("Client(%d) disconnected" % client['id'])

    @staticmethod
    def __message_received(client, server, message):
        """
        Called when a client sends a message
        """
        data = json.loads(message)

        log("Client(%d) said: %s" % (client['id'], data['type']))

    def send_data_message(self, type, args=None):
        """
        Sends a message to all connected clients.
        Only listens to MessageTypes.
        """

        if type not in list(self.events):
            return

        if args is None:
            args = {}

        log('WEBSOCKET CALL - Type: %d' % type)

        data = {'type': type, 'data': args}
        data = json.dumps(data)

        self.server.send_message_to_all(data)
