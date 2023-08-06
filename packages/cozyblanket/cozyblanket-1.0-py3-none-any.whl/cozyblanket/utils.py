import socket
from struct import pack, unpack
from typing import Optional, Tuple, List
import numpy as np
import numpy.typing as npt


Mesh = Tuple[npt.NDArray[np.single], List[Tuple[int, ...]]]
Vector3 = Tuple[float, float, float]
Transform = Tuple[Vector3, Vector3, Vector3]

def init_socket(mode : socket.SocketKind) -> socket.socket:
    s = socket.socket(socket.AF_INET, mode)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s

def check_path(path : str, mode : str) -> bool:
    try:
        with open(path, mode) as f:
            pass
    except IOError as e:
        print(f"[ERROR] Can't open file at '{path}' -> {e}")
        return False
    return True

def pack_str(s : str) -> bytes:
    return pack("i", len(s)) + s.encode()

def receive_data_array(connection : socket.socket, length : int) -> bytes:
    data = bytearray()
    while len(data) < length:
        packet = connection.recv(length - len(data))
        data.extend(packet)
    return data

def receive_data(connection : socket.socket) -> bytes:
    size_data = receive_data_array(connection, 4)
    
    if not size_data:
        return bytes()
    response_size = unpack('i', size_data)[0]
    return receive_data_array(connection, response_size)

def is_command_return_ok(data : Optional[bytes]) -> bool:
    if not data:
        return False
    return data[-2:] == b"OK"

def decode_transform(data : bytes) -> Transform:
    t_floats = unpack('fffffffff', data[:36])
    position = (t_floats[0], t_floats[1], t_floats[2])
    forward = (t_floats[3], t_floats[4], t_floats[5])
    up = (t_floats[6], t_floats[7], t_floats[8])
    return (position, forward, up)

def load_obj(path : str) -> Mesh:
    vertices = []
    faces = []
    for line in open(path, "r"):
        if line.startswith('#'): 
            continue
        values = line.split()
        if not values: 
            continue
        if values[0] == 'v':
            vcoords = list(map(float, values[1:4]))
            vertices.append((vcoords[0], vcoords[1], vcoords[2]))
        elif values[0] == 'f':
            face = []
            for val in values[1:]:
                w = val.split('/')
                index = int(w[0])
                index += -1 if index >= 0 else len(vcoords) // 3
                face.append(index)
            faces.append(tuple(face))
    return np.array(vertices), faces


def load_obj_arrays(path : str) -> Tuple[npt.NDArray[np.single], npt.NDArray[np.int32]]:
    coords = []
    indices = []

    for line in open(path, "r"):
        if line.startswith('#'): 
            continue
        values = line.split()
        if not values: 
            continue
        if values[0] == 'v':
            vcoords = map(float, values[1:4])
            for v in vcoords:
                coords.append(v)
        elif values[0] == 'f':
            face = []
            for val in values[1:]:
                w = val.split('/')
                index = int(w[0])
                index += -1 if index >= 0 else len(coords) // 3
                face.append(index)
            for i in range(0, len(face) - 2):
                indices.append(face[0])
                indices.append(face[i + 2])
                indices.append(face[i + 1])
    return np.array(coords), np.array(indices)

def write_obj(path : str, vertices : npt.NDArray[np.single], faces : List[Tuple[int, ...]]) -> None:
    with open(path, 'w') as obj:
        for v in vertices:
            obj.write("v %.4f %.4f %.4f\n" % (v[0], v[1], v[2]))
        for f in faces:
            obj.write("f")
            for fv in f:
                obj.write(" %d" % (fv + 1))
            obj.write("\n")