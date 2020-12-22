from importlib import machinery, util


def import_module(module: str):
    return machinery.SourceFileLoader(module, util.find_spec(module).origin).load_module(module)
