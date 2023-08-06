import argparse
import time
from inspect import signature
from functools import partial
from typing import Any, Callable, Optional, Sequence, Type, Union
from cozyblanket import CozyBlanketConnection


def throw_error(msg : str) -> None:
    print("[ERROR] " + msg)
    exit()


def make_cozy_command(name : str, command : Callable) -> Type[argparse.Action]:
    class CommandAction(argparse.Action):
        def __call__(self, parser: argparse.ArgumentParser, namespace : argparse.Namespace, values: Union[str, Sequence[Any], None], option_string : Optional[str]=None) -> None:
            if not 'commands' in namespace:
                setattr(namespace, 'commands', [])
            previous = namespace.commands
            comm = (name, partial(command, *values if values else []))
            previous.append(comm)
            setattr(namespace, 'commands', previous)
    return CommandAction


def cozy_command(command:Callable) -> None:
    global parser
    global CB
    name = command.__name__.replace("_", "-")
    params = signature(command).parameters
    n : Union[int, str] = len(params)

    if n == 1:
        _, param = list(params.items())[0]
        if not param.default is param.empty:
            n = '?'

    mv = tuple([p.name for _, p in params.items()])
    parser.add_argument(f"--{name}", action=make_cozy_command(name, command), type=str, nargs=n, metavar=mv)


# INIT
parser = argparse.ArgumentParser(description='CozyBlanket remote control.')
parser.add_argument("-i", "--id", type=int, help="Device ID")

# COMMANDS
@cozy_command
def ping() -> bool:
    print(f"PING {'ACK' if CB.ping() else 'FAILED'}")
    return True


@cozy_command
def document_create(name : str = "default") -> bool:
    return CB.document_create(name)


@cozy_command
def document_open(name : str = "default") -> bool:
    return CB.document_open(name)


@cozy_command
def document_close() -> bool:
    return CB.document_close()


@cozy_command
def scene_clear() -> bool:
    return CB.scene_clear()


@cozy_command
def editmesh_check_changes() -> bool:
    changes = CB.editmesh_check_changes()
    print(f"EDITMESH CHANGES {changes}")
    return True


@cozy_command
def editmesh_check_symmetry() -> bool:
    symmetry = CB.editmesh_check_symmetry()
    print(f"EDITMESH SYMMETRY {symmetry}")
    return True


@cozy_command
def editmesh_load(obj_path : str) -> bool:
    return CB.editmesh_load_obj(obj_path)


@cozy_command
def editmesh_pull(obj_path : str) -> bool:
    return CB.editmesh_pull_obj(obj_path)


@cozy_command
def target_push(obj_path : str, name : str) -> bool:
    return CB.target_push_obj(obj_path, name)


@cozy_command
def target_load(name : str) -> bool:
    return CB.target_load(name)


@cozy_command
def notification_send(title : str, content : str) -> bool:
    return CB.notification_send(title, content)


@cozy_command
def delay(seconds : str) -> bool:
    try:
        s = float(seconds)
    except ValueError:
        throw_error("Delay value is not a number.")

    try:
        time.sleep(s)
    except ValueError:
        throw_error("Invalid delay value.")
    return True


# PARSE AND RUN
args = parser.parse_args()

device_id = ""
if args.id:
    device_id = str(args.id)
    print(f"Connecting to device {device_id}")
else:
    print("Connecting to any device.")


CB = CozyBlanketConnection(device_id)

if not CB.connect():
    throw_error("Cannot connect to device.")

if not hasattr(args, "commands"):
    throw_error("No commands provided.")

for name, cmd in args.commands:
    ret = cmd()
    if not ret:
        throw_error(f"{name} failed.")
