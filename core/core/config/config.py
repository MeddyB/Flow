from collections import OrderedDict
import yaml
import copy
import json
import os
from ..template import Templates

class EntityConfig(object):

    def __init__(self, config, entity_type, root_template, tasks):
        super(EntityConfig, self).__init__()
        self._config = config
        self._entity_type = entity_type
        self._root_template = root_template
        self._tasks = tasks

    @property
    def config(self):
        return self._config

    @property
    def entity_type(self):
        return self._entity_type
    
    @property
    def handler(self):
        return self._handler
    
    @property
    def root_template(self):
        return self._root_template
    
    @property
    def tasks(self):
        return self._tasks
    
    @property
    def parent_entity(self):
        return self._parent_entity


class Config(object):

    _instance = None

    @staticmethod
    def get_instance():
        if Config._instance is None:
            Config._instance = Config(os.environ["FLOW_CONFIG_LOCATION"])
        return Config._instance

    def __init__(self, path):
        super(Config, self).__init__()
        self._name = None
        self._version = None
        self._templates = Templates()
        self._path = path
        self._root_template = None
        self._entities = {}
        self._load_config()
    
    @property
    def name(self):
        return self._name
    
    @property
    def version(self):
        return self._version
    
    @property
    def path(self):
        return self._path
    
    @property
    def entities(self):
        return self._entities
    
    @property
    def root(self):
        return self._root_template.format({})
    
    @property
    def templates(self):
        return self._templates
    
    def _load_config(self):
        # Read config.yml file and load templates
        # Set a dict with all EntitiyConfigs objects 
        # to sending to context and make folders
        with open(os.path.join(self._path, "config.yml")) as f:
            config = yaml.load(f, Loader=yaml.Loader)
        self._name = config.get("name", None)
        self._version = config.get("version", None)
        templates_path = os.path.join(self._path, "templates.yml")
        self._templates.load(templates_path)
        self._root_template = self._templates[config["root_template"]]
        for entity_name, entity_config in config["entities"].items():
            root_template = self._templates[entity_config["root_template"]]
            tasks = OrderedDict((s["name"], s) for s in entity_config.get("tasks", []))
            self._entities[entity_name] = EntityConfig(self, entity_name, root_template, tasks)

    def create_context(self, entity_type, entity_name, root_path, properties=None):
        path = os.path.abspath(root_path).replace("\\", "/")
        entity = copy.deepcopy(properties or {})
        entity["type"] = entity_type
        entity["name"] = entity_name
        template = self._entities[entity_type].root_template
        
        fields = template.parse(path)
        fields_entity = fields[entity_type]
        for key, fields_value in fields_entity.items():
            if key in entity:
                if fields_value != entity[key]:
                    raise Exception("{entity_type}.name field with value {repr(fields_entity['name'])} doesn't match entity_name {repr(entity_name)}".format(**locals()))
            else:
                entity[key] = fields_value
        
        properties_dir = os.path.join(root_path, ".flw")
        if os.path.exists(properties_dir):
            raise Exception("Cannot create entity {entity_type} {entity_name}. Entity already exists at \"{properties_dir}\".".format(**locals()))
        os.makedirs(properties_dir)
        with open(os.path.join(properties_dir, "properties.json"), "w") as f:
            json.dump(entity, f, indent=2, sort_keys=True)
        context = self.get_context(root_path)
        for step in self._entities[entity_type].tasks.values():
            context.create_step(step["name"])    
        return context
    
    def list_contexts(self, path, recursive=False):
        import pathlib
        root = pathlib.Path(path)
        root.rglob("*")
        for path in root.rglob("*"):
            if path.is_file():
                if '.flw' in path.parts:
                    index_big = str(path).split('.flw')
                    path = index_big[0]
                    yield os.path.dirname(path)
            
    def get_context(self, path):
        from ..context import Context
        return Context(self, path)
