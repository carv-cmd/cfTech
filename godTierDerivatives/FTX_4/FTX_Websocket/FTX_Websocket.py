import json
import time
import sys
from threading import Thread, Lock, BoundedSemaphore

from websocket import enableTrace
from websocket import WebSocketApp

__all__ = ['WebsocketManager', 'Lock']


class WebsocketManager:
    _CONNECT_TIMEOUT_S = 5

    def __init__(self):
        self.connect_lock = Lock()
        self.disconnecter = BoundedSemaphore(value=1)
        self.ws = None

    def _send(self, message):
        self.connect()
        self.ws.send(message)

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
            with open('../temp_storage/socket_errors.txt', mode='a+') as error_log:
                error_log.write(f'{repr(error)}')
        except OSError as e:
            raise e
        finally:
            self._reconnect(ws)

    def _connect(self):
        assert not self.ws, "ws should be closed before attempting to connect"
        enableTrace(True)

        # Initialize websocket and assign callbacks to WebSocketApp(**kwargs)
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._wrap_callback(self._on_message),
            on_close=self._wrap_callback(self._on_close),
            on_error=self._wrap_callback(self._on_error),
            on_pong=self._wrap_callback(self._on_pong),
        )

        websocket_thread = Thread(target=self._run_websocket, args=(self.ws,))
        websocket_thread.setDaemon(True)
        websocket_thread.start()

        # Waits for socket to connect
        ts = time.time()
        while self.ws and (not self.ws.sock or not self.ws.sock.connected):
            if time.time() - ts > self._CONNECT_TIMEOUT_S:
                self.ws = None
                return
            time.sleep(0.1)

    def _wrap_callback(self, func):
        """ Call back decorator """
        def wrapped_f(ws, *args, **kwargs):
            if ws is self.ws:
                try:
                    func(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')
        return wrapped_f

    def _run_websocket(self, ws):
        """ Default = websocket.run_forever(ping_interval=15) """
        try:
            ws.run_forever(ping_interval=15)
        except Exception as e:
            raise Exception(f'Unexpected error while running websocket: {e}')
        finally:
            self._reconnect(ws)

    def _reconnect(self, ws):
        """ Automatically attempt to reconnect for long polling sessions """
        assert ws is not None, '_reconnect should only be called with an existing ws'
        if ws is self.ws:
            self.ws = None
            ws.close()
            self.connect()

    def _disconnect(self, ws):
        """
        Blocks _reconnect when attempting to sever ws connection completely
        Raises sys.exit() to exit interpreter safely
        """
        self.disconnecter.acquire()
        assert ws is not None, '_disconnect should only be called with an existing ws'
        if ws is self.ws:
            self.ws = None
            ws.close()
            sys.exit()

    def reconnect(self) -> None:
        """ See _reconnect """
        if self.ws is not None:
            self._reconnect(self.ws)

    def connect(self):
        """
        Establish a WebSocketApp connection with FTX streaming servers
        Called implicitly by FtxWebsocketClient.inst.methods -> instance.get_foobar
        Call explicitly to customize server polls. Pointless for the most part
        """
        print('\n>>> Opening Websocket Connection w/ FTX servers. . .')
        if self.ws:
            return
        with self.connect_lock:
            while not self.ws:
                self._connect()
                if self.ws:
                    print('>>> Successfully Opened Websocket Connection. . .\n')
                    return

    def disconnect(self):
        """
        Closes the WebSocketApp connection w/ FTX servers
        Explicit call is required to override _reconnect
        Call from KeyboardInterrupt exception loop to gracefully terminate
        """
        print('\n>>> Closing Websocket Connection w/ FTX Servers. . .')
        if not self.ws:
            return
        try:
            with self.connect_lock:
                self._disconnect(self.ws)
        except SystemExit:
            self.disconnecter.release()
        finally:
            print('\t>>> Successfully Closed Websocket Connection. . .')

    def send_json(self, message):
        """ Encode message as JSON and send to FTX servers """
        self._send(json.dumps(message))


if __name__ == '__main__':
    print(f'>>> Running FTX_Websocket as {__name__}')

else:
    print(f'>>> Running FTX_Websocket as {__name__}')
