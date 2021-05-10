# import sys
import json
import time
import logging
from threading import Thread, Lock, Condition

from websocket import WebSocketApp
# from websocket import enableTrace
# enableTrace(True)

__all__ = ['WebsocketManager', 'Thread', 'Lock', 'logging', 'Condition']

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s')


class WebsocketManager:
    _CONNECT_TIMEOUT_S = 5

    def __init__(self):
        self.connect_lock = Lock()
        self.disconnect_lock = Condition()
        self.ws = None

    def _wrap_callback(self, func):
        """ Call back decorator """
        def wrapped_f(ws, *args, **kwargs):
            if ws is self.ws:
                try:
                    func(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')
        return wrapped_f

    def _get_url(self):
        raise NotImplementedError()

    def _on_message(self, ws, message):
        """ Call back function implemented in FTX_ws_Client """
        raise NotImplementedError()

    def _on_pong(self, ws, message):
        """ Call back function implemented in FTX_ws_Client """
        raise NotImplementedError()

    def _on_close(self, ws):
        """ Automatically resets websocket connection """
        self._reconnect(ws)

    def _on_error(self, ws, error):
        try:
            with open('../socket_errors.txt', mode='a+') as error_log:
                error_log.write(f'{repr(error)}')
        except OSError as e:
            raise e
        finally:
            self._reconnect(ws)

    def _reconnect(self, ws):
        """ Automatically attempt to reconnect for long polling sessions """
        assert ws is not None, '_reconnect should only be called with an existing ws'
        if ws is self.ws:
            self.ws = None
            ws.close()
            self.connect()

    def reconnect(self) -> None:
        """ See _reconnect """
        if self.ws is not None:
            self._reconnect(self.ws)

    def _run_websocket(self, ws):
        """ Default = websocket.run_forever(ping_interval=15) """
        try:
            ws.run_forever(ping_interval=15)
        except Exception as e:
            raise Exception(f'Unexpected error while running websocket: {e}')
        finally:
            self._reconnect(ws)

    def _connect(self):
        assert not self.ws, "ws should be closed before attempting to connect"
        # Initialize websocket and assign callbacks to WebSocketApp(**kwargs)
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._wrap_callback(self._on_message),
            on_close=self._wrap_callback(self._on_close),
            on_error=self._wrap_callback(self._on_error),
            on_pong=self._wrap_callback(self._on_pong),
        )

        websocket_thread = Thread(name='FOREVER_SOCKET', target=self._run_websocket, args=(self.ws,))
        websocket_thread.setDaemon(True)
        websocket_thread.start()

        # Waits for socket to connect
        ts = time.time()
        while self.ws and (not self.ws.sock or not self.ws.sock.connected):
            if time.time() - ts > self._CONNECT_TIMEOUT_S:
                self.ws = None
                return
            time.sleep(0.1)

    def _disconnect(self, ws):
        assert self.ws, "ws should be open before attempting to close"
        if self.ws:
            self.ws = None
            ws.close()
            time.sleep(0.5)

    def _send(self, message):
        self.connect()
        self.ws.send(message)

    def connect(self):
        """
        Establish a WebSocketApp connection with FTX streaming servers
        Called implicitly by FtxWebsocketClient.inst.methods -> instance.get_foobar
        Call explicitly to customize server polls. Pointless for the most part
        """
        # print('\n>>> Opening Websocket Connection w/ FTX servers. . .\n')
        if self.ws:
            return
        with self.connect_lock:
            while not self.ws:
                self._connect()
                if self.ws:
                    print('>>> Successfully Opened Websocket Connection. . .\n')
                    return

    def disconnect(self):
        if not self.ws:
            return
        self._disconnect(self.ws)

    def send_json(self, message):
        """ Encode message as JSON and send to FTX servers """
        self._send(json.dumps(message))


if __name__ == '__main__':
    print(f'>>> Running FTX_Websocket as {__name__}')

else:
    print(f'>>> Running FTX_Websocket as {__name__}')
