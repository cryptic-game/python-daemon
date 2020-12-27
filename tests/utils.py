import runpy
from importlib import machinery, util


def import_module(module: str):
    return machinery.SourceFileLoader(module, util.find_spec(module).origin).load_module(module)


def run_module(module: str):
    runpy.run_module(module, {}, "__main__")
