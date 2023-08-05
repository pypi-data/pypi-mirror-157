import json
import time
import datetime
import threading
import struct
from . import logging

import websocket

from . import MessageTypes
from . import VariableTypes
from . import AccessTypes
from .ckDefines import CtpTypes, InoDrivePorts, InoDrive_LedMode, InoDriveInputsPolarity, MotionCommands, Dimensions
from .ckDefines import CK_CONST, MotionProfile, InputsConfig, PositionHold
from . import get_transaction_id

VERSION = '0.1.0'


class InoDrive(object):
    def __init__(self, target=None, **kwargs):
        self._target = target
        self._auto_connect = kwargs.get('autoConnect', False)

        self._secure = True if kwargs.get('secure') else False
        # Timeout notes:
        # connectTimeout should be 3 - 15 seconds. Low values like 3-5 should be good, even over the internet.
        # socketTimeout should be ~10. When a file transfer overwrites a file, there could be 2-3 seconds of
        # filesystem overhead and the transfer of 300k+ firmware file takes 2+ seconds.
        # Maybe we need separate file transfer and variable API timeouts.
        self._socket_timeout = kwargs.get('socketTimeout', 10)
        self._connect_timeout = kwargs.get('connectTimeout', 5)
        self._request_timeout = kwargs.get('requestTimeout', 2)
        self._keep_alive = kwargs.get('keepAlive', 5)
        self._float_precision = kwargs.get('floatPrecision')

        self._url = f'{"wss" if self._secure else "ws"}://{self._target}/api'
        logging.info(f'Target: {self._url}')

        # WebSocket instance
        self._ws = websocket.WebSocket(enable_multithread=True)

        self._axis_inputs = InputsConfig()
        self._motion_profile = MotionProfile()

        # Thread loops
        self._ws_thread = None
        self._ws_thread_running = False
        self._variables_list = []
        self._variables_list_initialized = 'none'

        self._request_queue = {}

        self._connect = False

        self._ws_thread = threading.Thread(target=self._ws_thread_loop, daemon=True)
        self._ws_thread_running = True
        self._ws_thread.start()

        if self._auto_connect:
            self.connect()

    def __del__(self):
        self.dispose()

    def dispose(self):
        try:
            if self.connected:
                self.disconnect()

            self._ws_thread_running = False
            if self._ws_thread:
                self._ws_thread.join()
                self._ws_thread = None

        except Exception as ex:
            logging.error(str(ex))

    @property
    def version(self):
        return VERSION

    @property
    def connected(self):
        if self._ws.connected and self._variables_list_initialized == 'done':
            return True
        else:
            return False
        # return self._ws.connected

    def connect(self):
        try:
            self._connect = True

            if self.connected:
                return True

            current_time = datetime.datetime.now()
            timeout_time = current_time + datetime.timedelta(seconds=self._connect_timeout)
            timeout = False
            while timeout is False:
                if current_time >= timeout_time:
                    timeout = True

                if self.connected:
                    logging.info(f'WS Connected to: {self._url}')
                    break

                time.sleep(0.01)
                current_time = datetime.datetime.now()

            if timeout is False:
                return True

        except Exception as ex:
            logging.info(str(ex))

        return False

    def disconnect(self):
        try:
            self._connect = False

            if self.connected is False:
                return True

            current_time = datetime.datetime.now()
            timeout_time = current_time + datetime.timedelta(seconds=self._connect_timeout)
            timeout = False
            while timeout is False:
                if current_time >= timeout_time:
                    timeout = True

                if self.connected is False:
                    logging.info(f'WS Disconnected from: {self._url}')
                    break

                time.sleep(0.01)
                current_time = datetime.datetime.now()

            if timeout is False:
                return True

        except Exception as ex:
            logging.error(str(ex))

        return False

    def list(self):
        try:
            return list(map(lambda x: x['name'], self._variables_list))
        except Exception as ex:
            logging.error(str(ex))

        return []

    def read(self, prop=None):
        try:
            if prop is None:
                return None

            if type(prop) == str or type(prop) == int:
                var = self._get_variable(prop)
                if var:
                    response = self._request(type=MessageTypes.varAccess, payload={'data': [{'id': var.get('id', 0)}]})

                    if response.get('success'):
                        data = response.get('data')
                        if len(data) == 1:
                            item: dict = data[0]
                            return self._get_value(item.get('val'))

            elif type(prop) == list:
                payload = []

                for item in prop:
                    var = self._get_variable(item)
                    if var:
                        payload.append({'id': var['id']})

                response = self._request(type=MessageTypes.varAccess, payload={'data': payload})

                result = {}
                if response.get('success'):
                    data = response.get('data')
                    for item in data:
                        var = self._get_variable(item.get('id'))
                        if var:
                            result.update({var.get('name', 'unknown'): self._get_value(item.get('val'))})

                return result

        except Exception as ex:
            logging.error(str(ex))

        return None

    def write(self, prop=None, value=None):
        try:
            if (type(prop) == str or type(prop) == int) and (type(value) == int or type(value) == float or type(value) == bool):
                var = self._get_variable(prop)
                if var:
                    response = self._request(type=MessageTypes.varAccess, payload={'data': [{'id': var.get('id'), 'val': self._get_value(value)}]})
                    if response.get('success'):
                        return True
            elif type(prop) == dict:
                payload = []
                for name, value in prop.items():
                    var = self._get_variable(name)
                    if var:
                        payload.append({'id': var.get('id'), 'val': self._get_value(value)})

                response = self._request(type=MessageTypes.varAccess, payload={'data': payload})
                if response.get('success'):
                    return True

        except Exception as ex:
            logging.error(str(ex))

        return False

    def _get_value(self, value=None):
        if type(value) == int:
            return value
        elif type(value) == float:
            if type(self._float_precision) == int:
                return round(value, self._float_precision)
            else:
                return value
        elif type(value) == bool:
            return True if value else False

        return None

    def _get_variable(self, item=None):
        for var in self._variables_list:
            if type(item) == str and var.get('name') == item:
                return var
            elif type(item) == int and var.get('id') == item:
                return var

        return None

    def _update_vars_list(self):
        try:
            response = self._request(type=MessageTypes.varList)
            if response.get('success'):
                data = response.get('data')
                if data and type(data) == list:
                    self._variables_list = data
        except Exception as ex:
            logging.error(str(ex))

    def _request(self, type=None, payload=None):
        try:
            if type is None:
                return {'success': False, 'error': 'Request type not specified'}

            transaction_id = get_transaction_id(8)
            current_time = datetime.datetime.now()
            timeout_time = current_time + datetime.timedelta(seconds=self._request_timeout)

            self._request_queue.update({
                transaction_id: {
                    'time': current_time + datetime.timedelta(seconds=self._request_timeout * 3),
                    'response': None,
                }
            })

            data = {'id': transaction_id, 'request': type}
            if payload is not None:
                data.update(payload)
            data = json.dumps(data)
            data = data.encode('ascii')

            self._send(data)

            response = None
            timeout = False
            while timeout is False:
                if current_time >= timeout_time:
                    timeout = True

                response = self._request_queue[transaction_id].get('response')

                if response:
                    # Remove the request from the queue
                    del self._request_queue[transaction_id]
                    break

                time.sleep(0.01)
                current_time = datetime.datetime.now()

            if timeout:
                return {'success': False, 'error': 'timeout'}
            else:
                return {'success': True, 'data': response.get('data')}

        except Exception as ex:
            logging.error(str(ex))
            return {'success': False, 'error': ex}

    def _send(self, data=None):
        try:
            if self._ws.connected:
                self._send_keep_alive_at = datetime.datetime.now() + datetime.timedelta(seconds=self._keep_alive)
                self._ws.send(data)
        except Exception as ex:
            logging.error(str(ex))

    def _ws_thread_loop(self):
        logging.debug('WS Thread start...')

        while self._ws_thread_running:
            try:
                # Check for orphan requests in the request queue
                # =====================================================================================================
                id_to_remove = []
                guard_time = datetime.datetime.now()
                for id, data in self._request_queue.items():
                    request_time = data.get('time')

                    if request_time is None or request_time <= guard_time:
                        id_to_remove.append(id)

                for id in id_to_remove:
                    logging.warning(f'Delete request ID:{id} -> Orphan request')
                    del self._request_queue[id]
                    logging.warning('Queue length:', len(self._request_queue))
                # =====================================================================================================

                # If connection has to be closed - close the connection
                # =====================================================================================================
                if self._connect is False:
                    if self.connected:
                        self._ws.close()
                    time.sleep(0.01)
                    continue
                # =====================================================================================================

                # If we are not connected - connect
                # =====================================================================================================
                if self._ws.connected is False:
                    logging.debug(f'WS Connect to: {self._url}')
                    self._variables_list_initialized = 'none'
                    try:
                        self._ws.connect(self._url, timeout=self._connect_timeout)
                    except Exception as ex:
                        time.sleep(1)
                    continue
                # =====================================================================================================

                # Is the variables list is not initialized - initialize the list
                # =====================================================================================================
                if self._variables_list_initialized == 'none':
                    data = {'id': get_transaction_id(8), 'request': MessageTypes.varList}
                    data = json.dumps(data)
                    data = data.encode('ascii')
                    self._send(data)
                    self._variables_list_initialized = 'initializing'
                # =====================================================================================================

                # Keep alive
                # =====================================================================================================
                if self._send_keep_alive_at is None or self._send_keep_alive_at <= datetime.datetime.now():
                    request = json.dumps({'id': get_transaction_id(8), 'request': MessageTypes.keepAlive})
                    request = request.encode('ascii')
                    self._send(request)
                # =====================================================================================================

                # Wait,read and handle the response
                # =====================================================================================================
                response = None
                try:
                    response = self._ws.recv()
                except websocket.WebSocketTimeoutException:
                    pass
                except Exception as ex:
                    self._ws.close()
                    self._variables_list_initialized = 'none'
                    time.sleep(0.1)

                if response:
                    response = json.loads(response.decode('utf-8'))

                    if type(response) != dict:
                        continue

                    # Update variables list
                    if response.get('response') == MessageTypes.varList:
                        data = response.get('data')
                        if data:
                            self._variables_list = data
                            self._variables_list_initialized = 'done'

                    transaction_id = response.get('id')
                    if transaction_id:
                        request = self._request_queue.get(transaction_id)
                        if request:
                            request.update({'response': response})
                # =====================================================================================================

            except Exception as ex:
                logging.error(str(ex))
                # Unhandled exception - give it some time to recover
                time.sleep(1)

        if self._ws and self._ws.connected:
            logging.debug('WS Close...')
            self._ws.close()

        logging.debug('WS Thread exit...')

    def delete_uapp(self):
        # Assume the worse
        Result = False

        logging.info(f'Deleting user application on {self._target}...')
        cmd_url = f'{"wss" if self._secure else "ws"}://{self._target}/cmd'
        cmd_ws = websocket.WebSocket(enable_multithread=True)
        try:
            cmd_ws.connect(cmd_url, timeout=self._connect_timeout)
        except Exception as ex:
            logging.debug('WS Could not connect.')

        tlv_header = struct.pack(">II", CtpTypes.CTP_TYPE_MODULE_DELETE_UAPP, 0)
        data = tlv_header

        cmd_ws.settimeout(self._socket_timeout)
        try:
            cmd_ws.send_binary(data)
            resp_bytes = cmd_ws.recv()
        except Exception as ex:
            logging.debug('WS Error: ' + str(ex))
            return False
        (resp_type, resp_len, resp_result) = struct.unpack(">IIB", resp_bytes)
        # logging.debug(f'Resp->Type={resp_type}, Len={resp_len}, Result={resp_result}')
        if resp_type == CtpTypes.CTP_TYPE_RESULT and resp_len == 1 and resp_result == 0:
            logging.debug("Success")
            Result = True

        logging.debug('WS Close...')
        cmd_ws.close()
        return Result

    def upload(self, file_name, file_bytes, transfer_type=CtpTypes.CTP_TYPE_FILE_TRANSFER):
        # Assume the worse
        Result = False

        # Check inputs
        if file_bytes is None:
            raise ValueError("parameter file_bytes cannot be None")
        if file_name is None:
            raise ValueError("parameter file_name cannot be None")
        if type(file_name) is not str:
            raise TypeError("parameter file_name must be a string")
        if type(file_bytes) is not bytes:
            raise TypeError("parameter file_bytes must be bytes")
        if type(transfer_type) is not int:
            raise TypeError("parameter transfer_type must be 'int' from CtpTypes")
        if transfer_type is not CtpTypes.CTP_TYPE_FILE_TRANSFER and \
                transfer_type is not CtpTypes.CTP_TYPE_FIRMWARE_TRANSFER and \
                transfer_type is not CtpTypes.CTP_TYPE_BACKUP_FIRMWARE_TRANSFER:
            raise ValueError("bad value for transfer_type")

        logging.info(f'Uploading {file_name} to {self._target}...')
        cmd_url = f'{"wss" if self._secure else "ws"}://{self._target}/cmd'
        cmd_ws = websocket.WebSocket(enable_multithread=True)
        try:
            cmd_ws.connect(cmd_url, timeout=self._connect_timeout)
        except Exception as ex:
            logging.debug('WS Could not connect.')

        file_name_tlv_header = struct.pack(">II", CtpTypes.CTP_TYPE_STRING, len(file_name))
        file_transfer_tlv_header = struct.pack(">II", transfer_type, 1)  # payload is 1 byte
        blob_tlv_header = struct.pack(">II", CtpTypes.CTP_TYPE_BLOB, len(file_bytes))

        data = file_transfer_tlv_header + bytes([1]) + \
               file_name_tlv_header + bytes(file_name, 'ascii') + \
               blob_tlv_header + file_bytes

        cmd_ws.settimeout(self._socket_timeout)
        try:
            cmd_ws.send_binary(data)
            resp_bytes = cmd_ws.recv()
        except Exception as ex:
            logging.debug('WS Error: ' + str(ex))
            return False
        (resp_type, resp_len, resp_result) = struct.unpack(">IIB", resp_bytes)
        # logging.debug(f'Resp->Type={resp_type}, Len={resp_len}, Result={resp_result}')
        if resp_type == CtpTypes.CTP_TYPE_RESULT and resp_len == 1 and resp_result == 0:
            logging.debug("Success")
            Result = True

        logging.debug('WS Close...')
        cmd_ws.close()
        return Result
