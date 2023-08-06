import numpy as np
import numpy.typing as npt
import socket
import time
import math
import threading
import random
from struct import pack, unpack
from typing import Callable, Dict, List, Optional, Tuple
from . import utils as ut


class CozyBlanketConnection:
    BROADCAST_PORT = 8606
    CONNECTION_PORT = 8607
    DATA_STREAM_PORT = 8608
    REMOTE_ACTIONS_PORT = 8609

    def __init__(self, cozyblanket_id: Optional[str] = None, name : str = "") -> None:
        self.name : str = name
        self._device_ip : str = ""
        self._device_id : Optional[str] = cozyblanket_id
        self._data_broadcast : Optional[socket.socket] = None
        self._remote_actions : Optional[CozyBlanketRemoteActions] = None

    def _send_command(self, command: bytes, data: bytes = bytes(), timeout: float = 10.0) -> Tuple[bool, bytes]:
        if self._device_ip == "":
            if not self.connect():
                return False, bytes()

        try:
            connection = ut.init_socket(socket.SOCK_STREAM)
            connection.connect(
                (self._device_ip, CozyBlanketConnection.CONNECTION_PORT))
            connection.settimeout(None)

            command_size = len(command)
            data_size = len(data)
            total_size = 4 + command_size + data_size
            package = pack("ii", total_size, command_size) + \
                command + bytes(data)

            connection.sendall(package)
        except Exception as e:
            print("[Send Command] Exception: ", e)
            connection.close()
            return False, bytes()

        try:
            connection.settimeout(timeout)
            ret_data = ut.receive_data(connection)
        except Exception as e:
            print("[Command Response] Exception: ", e)
            return False, bytes()
        finally:
            connection.close()

        return ut.is_command_return_ok(ret_data), ret_data

    ### CONNECTION ###
    def has_connection_available(self) -> bool:
        return self._device_ip != ""

    def connect(self, timeout: float = 5.0) -> bool:
        try:
            broadcast = ut.init_socket(socket.SOCK_DGRAM)
            broadcast.bind(("", CozyBlanketConnection.BROADCAST_PORT))
            broadcast.settimeout(timeout)
        except Exception as e:
            print("[Connect] Exception: ", e)
            broadcast.close()
            return False

        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                payload, ip = broadcast.recvfrom(4096)
                content = payload.decode()
                if self._device_id:
                    bcast_id = content.split("/")[1]
                    if self._device_id != bcast_id:
                        continue
                self._device_ip = ip[0]
                break
        except socket.timeout:
            return False
        finally:
            broadcast.close()

        return self.ping()

    def ping(self) -> bool:
        if not self.has_connection_available():
            return False
        return self._send_command(b"PING", timeout=2.0)[0]

    def disconnect(self) -> None:
        if self._remote_actions:
            self._remote_actions.disconnect()

    ### DOCUMENT ###
    def document_create(self, name: str = "default") -> bool:
        return self._send_command(b"DOCUMENT_CREATE", ut.pack_str(name))[0]

    def document_open(self, name: str = "default") -> bool:
        return self._send_command(b"DOCUMENT_OPEN", ut.pack_str(name))[0]

    def document_close(self) -> bool:
        return self._send_command(b"DOCUMENT_CLOSE")[0]

    ### SCENE ###
    def scene_clear(self) -> bool:
        return self._send_command(b"SCENE_CLEAR")[0]

    ### EDITMESH ###
    def editmesh_check_changes(self) -> bool:
        success, response = self._send_command(b"EDITMESH_CHANGES_CHECK")
        return success and response[0] != 0

    def editmesh_check_symmetry(self) -> bool:
        success, response = self._send_command(b"EDITMESH_SYMMETRY_CHECK")
        return success and response[0] != 0

    def editmesh_load(self, vertices: npt.NDArray[np.single], faces: List[Tuple[int, ...]]) -> bool:
        data = pack("ii", len(vertices), len(faces))

        coords = []
        for v in vertices:
            coords.append(v[0])
            coords.append(v[1])
            coords.append(v[2])

        indices = []
        for f in faces:
            indices.append(len(f))
            for i in f:
                indices.append(i)

        data += pack("%sf" % len(coords), *coords)
        data += pack("%si" % len(indices), *indices)

        return self._send_command(b"EDITMESH_LOAD", data)[0]

    def editmesh_load_obj(self, path: str) -> bool:
        if not ut.check_path(path, "r"):
            return False
        vertices, faces = ut.load_obj(path)
        return self.editmesh_load(vertices, faces)

    def editmesh_pull(self) -> ut.Mesh:
        success, response = self._send_command(b"EDITMESH_PULL")
        if not success:
            return (np.array(np.single, []), [])

        mesh_elem_count = unpack('ii', response[:8])
        vcount = mesh_elem_count[0]

        vertex_co = np.frombuffer(response, np.single, vcount * 3, 8)
        remaining_bytes = len(response) - 8 - 2 - (vcount * 3 * 4)
        indices = np.frombuffer(response, np.intc, remaining_bytes // 4, 8 + (vcount * 3 * 4))

        vertices: npt.NDArray[np.single] = np.array([(vertex_co[i], vertex_co[i + 1], vertex_co[i + 2]) for i in range(0, len(vertex_co), 3)])
        faces: List[Tuple[int, ...]] = []
        index_it = 0
        while index_it < len(indices):
            vcount_face = indices[index_it]
            index_it += 1
            faces.append(tuple(indices[index_it:index_it + vcount_face]))
            index_it += vcount_face
        return (vertices, faces)

    def editmesh_pull_obj(self, path: str) -> bool:
        if not ut.check_path(path, "w"):
            return False

        vertices, faces = self.editmesh_pull()
        if vertices.size == 0 or len(faces) == 0:
            return False

        ut.write_obj(path, vertices, faces)
        return True

    ### TARGET ###
    def target_push(self, coords: npt.NDArray[np.single], indices: npt.NDArray[np.int32], name: str = "__target") -> bool:
        data = ut.pack_str(name)
        data += pack("ii", len(coords) // 3, len(indices))
        data += pack("%sf" % len(coords), *coords)
        data += pack("%si" % len(indices), *indices)
        return self._send_command(b"TARGET_PUSH", data)[0]

    def target_push_obj(self, path: str, name: str = "__target") -> bool:
        if not ut.check_path(path, "r"):
            return False

        coords, indices = ut.load_obj_arrays(path)
        return self.target_push(coords, indices, name)

    def target_load(self, name: str = "__target") -> bool:
        return self._send_command(b"TARGET_LOAD", ut.pack_str(name))[0]

    ### NOTIFICATIONS ###
    def notification_send(self, title : str, content : str) -> bool:
        t = ut.pack_str(title)
        c = ut.pack_str(content)
        return self._send_command(b"NOTIFICATION_SEND", t + c)[0]

    ### CAMERA ###
    def camera_transform_get(self) -> Optional[ut.Transform]:
        success, response = self._send_command(b"CAMERA_TRANSFORM_GET")
        if not success:
            return None
        return ut.decode_transform(response)

    def camera_transform_broadcast(self, seconds : float) -> bool:
        data = pack("i", int(math.ceil(seconds)))
        success, _ = self._send_command(b"CAMERA_TRANSFORM_BROADCAST", data)
        if not success:
            return False

        if not self._data_broadcast:
            self._data_broadcast = ut.init_socket(socket.SOCK_DGRAM)
            self._data_broadcast.bind(
                ("", CozyBlanketConnection.DATA_STREAM_PORT))
        return True

    def camera_transform_broadcast_update(self) -> Optional[ut.Transform]:
        if not self._data_broadcast:
            return None
        self._data_broadcast.settimeout(1)
        self._data_broadcast.setblocking(False)
        newestData = None

        while True:
            try:
                data = self._data_broadcast.recv(36)
                if data:
                    newestData = data
            except BlockingIOError:
                break
            except Exception as e:
                print("[Camera Update] Exception: ", e)
                break

        if newestData:
            return ut.decode_transform(newestData)
        return None

    # REMOTE ACTIONS
    def remote_actions_add(self, name : str, action : Callable) -> bool:
        if not self._remote_actions:
            self._remote_actions = CozyBlanketRemoteActions(self)
        return self._remote_actions.add(name, action)

    def remote_actions_remove(self, name : str) -> bool:
        if not self._remote_actions:
            return False
        success, empty = self._remote_actions.remove(name)
        if empty:
            self.remote_actions_clear()
        return success

    def remote_actions_clear(self) -> None:
        if not self._remote_actions:
            return
        self._remote_actions.disconnect()
        self._remote_actions = None

    def remote_actions_process(self) -> None:
        if not self._remote_actions:
            return
        self._remote_actions.process()

class CozyBlanketRemoteActions:

    def __init__(self, cozyblanket_connection : CozyBlanketConnection):
        self._connection: CozyBlanketConnection = cozyblanket_connection
        self._actions : Dict[str, Callable]= {}
        self._actions_lock = threading.Lock()

        self._calls : List[str] = []
        self._calls_lock = threading.Lock()

        self._server_port = CozyBlanketConnection.REMOTE_ACTIONS_PORT + 1
        self._server_thread_stop = threading.Event()
        self._server_thread = threading.Thread(target=self._server_loop)
        self._server_thread.start()

        self._report_thread_stop = threading.Event()
        self._report_thread = threading.Thread(target=self._report_loop)
        self._report_thread.start()

    def disconnect(self) -> None:
        self._server_thread_stop.set()
        self._report_thread_stop.set()
        self._server_thread.join(1.0)
        self._report_thread.join(1.0)

    def add(self, action_name: str, callback: Callable) -> bool:
        with self._actions_lock:
            if action_name in self._actions:
                return False
            self._actions[action_name] = callback
            return True

    def remove(self, action_name: str) -> Tuple[bool, bool]:
        with self._actions_lock:
            if action_name in self._actions:
                del self._actions[action_name]
                return True, len(self._actions) == 0
            return False, False

    def process(self) -> None:
        with self._calls_lock:
            for command in reversed(self._calls):
                if command in self._actions:
                    self._actions[command]()
            self._calls = []

    def _server_loop(self) -> None:
        server_socket : Optional[socket.socket] = None
        while not self._server_thread_stop.is_set():
            while server_socket == None:
                try:
                    server_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(("", self._server_port))
                    server_socket.settimeout(0.05)
                    server_socket.listen()
                except socket.error as e:
                    if e.errno == 48:
                        self._server_port += 1
                        time.sleep(random.random() * 0.01)
                    else:
                        print("[Remote Action Server] Exception:", e)
                    server_socket.close()
                    server_socket = None
                    break

            if not server_socket:
                time.sleep(0.1)
                continue

            try:
                connection, _ = server_socket.accept()
                data = ut.receive_data(connection)
                if data == None or data == bytearray():
                    print("Received empty action")
                    continue
            except socket.timeout:
                continue
            except Exception as e:
                print("[Remote Action Server] Connection Exception:", e)
                server_socket.close()
                server_socket = None
                if 'connection' in locals() and connection != None:
                    connection.close()
                continue

            if not ut.is_command_return_ok(data):
                print(
                    "[Remote Action Server] Missing 'OK' token at the end of remote action call.")
                continue

            str_len = unpack("i", data[:4])[0]
            action_name = data[4:4+str_len].decode()

            with self._calls_lock:
                self._calls.append(action_name)

    def _report_loop(self) -> None:
        last_sent = time.time()
        while not self._server_thread_stop.is_set():
            if self._connection._device_ip == "":
                time.sleep(0.5)
                continue

            if time.time() - last_sent < 3.0:
                time.sleep(0.1)
                continue

            try:
                connection_socket = ut.init_socket(socket.SOCK_STREAM)
                connection_socket.connect(
                    (self._connection._device_ip, CozyBlanketConnection.REMOTE_ACTIONS_PORT))
                connection_socket.settimeout(0.5)
                data = ut.pack_str(self._connection.name) + \
                    pack("ii", self._server_port, len(self._actions))
                for action_name in self._actions.keys():
                    data += ut.pack_str(action_name)
                connection_socket.sendall(data)
                last_sent = time.time()
            except socket.error as e:
                connection_socket.close()

                if e.errno != 61:
                    print("[Report Connection] Exception: ", e)
                    time.sleep(1.0)
                else:
                    time.sleep(0.1)