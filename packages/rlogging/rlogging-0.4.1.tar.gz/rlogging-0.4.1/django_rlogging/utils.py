import importlib


def get_obj(obj_path: str):
    module_path, _, method_name = obj_path.rpartition('.')
    module = importlib.import_module(module_path)
    return getattr(module, method_name)


def rlogging_setup_from_data(rlogging_data: dict):
    pass
