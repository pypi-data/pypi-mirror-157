import inspect
from typing import Callable

from bolinette.exceptions import InternalError


def _parse_params(function, *args, **kwargs):
    cur_arg = 0
    arg_cnt = len(args)
    out_args = []
    out_kwargs = {}
    for key, param in inspect.signature(function).parameters.items():
        match param.kind:
            case param.POSITIONAL_ONLY:
                if cur_arg < arg_cnt:
                    out_args.append(args[cur_arg])
                    cur_arg += 1
                else:
                    out_args.append(param.default if not param.empty else None)
            case param.KEYWORD_ONLY:
                out_kwargs[key] = kwargs.pop(
                    key, param.default if not param.empty else None
                )
            case param.POSITIONAL_OR_KEYWORD:
                if cur_arg < arg_cnt:
                    out_args.append(args[cur_arg])
                    cur_arg += 1
                else:
                    out_args.append(
                        kwargs.pop(key, param.default if not param.empty else None)
                    )
            case param.VAR_POSITIONAL:
                while cur_arg < arg_cnt:
                    out_args.append(args[cur_arg])
                    cur_arg += 1
            case param.VAR_KEYWORD:
                for p_name, p_value in kwargs.items():
                    out_kwargs[p_name] = p_value
    return out_args, out_kwargs


def invoke(function: Callable, *args, **kwargs):
    if callable(function):
        args, kwargs = _parse_params(function, *args, **kwargs)
        return function(*args, **kwargs)
    raise InternalError(f"internal.not_function:{function.__name__}")


def getattr_(entity, key, default):
    if isinstance(entity, dict):
        return entity.get(key, default)
    return getattr(entity, key, default)


def hasattr_(entity, key):
    if isinstance(entity, dict):
        return key in entity
    return hasattr(entity, key)


def setattr_(entity, key, value):
    if isinstance(entity, dict):
        entity[key] = value
    else:
        setattr(entity, key, value)


def is_db_entity(entity) -> bool:
    return hasattr(entity, "_sa_instance_state")
