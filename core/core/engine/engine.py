import os
from ..config import Config
import yaml


def load_engine(path=None, context=None):
    if path is None:
        path = os.environ["FLOW_ENGINE_PATH"]
    if context is None:
        config = Config.get_instance()
        if "FLOW_CURRENT_CONTEXT" in os.environ:
            context_path = os.environ["FLOW_CURRENT_CONTEXT"]
            os.chdir(context_path)
        else:
            context_path = os.getcwd()
            
        context = config.get_context(context_path)
        print("context -->", context)

    with open(path) as f:
        engine_config = yaml.load(f, Loader=yaml.SafeLoader)
        print("engine_config from file config -->", engine_config)
                
    handler = engine_config.get("engine_handler", "bigcore.engine:Engine")
    print("handler -->", handler)
    