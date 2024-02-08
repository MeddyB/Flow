from ..config import Config
import json
import copy
import os

class Context(object):

    @staticmethod
    def from_path(path, config=None):
        if config is None:
            config = Config.get_instance()
        return Context(config, path)

    def __init__(self, config, path):
        super(Context, self).__init__()
        path = os.path.abspath(path)
        root = path
        previous = root
        while not os.path.exists(os.path.join(root, ".flw")):
            root = os.path.dirname(root)
            if root == previous:
                raise Exception("Root of filesystem reached without context. From path: \"{}\"".format(path))
            previous = root
        self._secondary_path = None
        root_path = os.path.join(root, ".flw", "root")
        if os.path.exists(root_path):
            self._secondary_path = root
            with open(root_path) as f:
                root = f.read()
                root = os.path.expandvars(root.strip())
        self._config = config
        self._path = path.replace("\\", "/")
        self._root = root.replace("\\", "/")
        self._parent = None
        if not os.path.exists(self.properties_path):
            raise Exception("\"{self.properties_path}\" no such file or directory.".format(**locals()))
        self._properties = None
    
    def __repr__(self):
        return "<{} path=\"{}\">".format(self.__class__.__name__, self.path)

    @property
    def config(self):
        return self._config
    
    @property
    def entity_config(self):
        return self._config.entities[self.properties["type"]]
    
    @property
    def properties_path(self):
        return os.path.join(self._root, ".flw", "properties.json")
    
    @property
    def secondary_path(self):
        return self._secondary_path
    
    @property
    def properties(self):
        if self._properties is None:
            with open(self.properties_path) as f:
                self._properties = json.load(f)
        return self._properties
    
    def save_properties(self):
        with open(self.properties_path, "w") as f:
            json.dump(self.properties, f, indent=2, sort_keys=True)
    
    @property
    def path(self):
        return self._path
    
    @property
    def relative_root(self):
        return os.path.relpath(self._root, self._config.root).replace("\\", "/")
    
    @property
    def root(self):
        return self._root
    
    @property
    def fields(self):
        if self.parent:
            fields = self.parent.fields
        else:
            fields = {}
        
        template, parent_path = self._config.templates.get_parent_template_from_path(self._path)
        if template is None:
            raise Exception("Unable to find a template matching: {}".format(self._path))
        path_fields = template.parse(parent_path)
        fields.update(path_fields)
        fields["Entity"] = {
            "type": self.properties["type"],
            "root": self._root,
            "name": self.properties["name"]
        }
        fields[self.properties["type"]] = copy.deepcopy(self.properties)
        return fields
    
    @property
    def parent(self):
        if self._parent is None:
            current = os.path.dirname(self._root)
            previous = current
            while not os.path.exists(os.path.join(current, ".flw")):
                current = os.path.dirname(current)
                if current == previous:
                    self._parent = False
                    break
                previous = current
            if self._parent is not False:
                self._parent = Context(self._config, current)             
        return self._parent or None
    
    @property
    def project(self):
        current = self
        while current:
            if current.properties["type"] == "Project":
                return current
            current = current.parent
    
    def create_secondary_path(self, path):
        big_dir = os.path.join(path, ".flw")
        if os.path.exists(big_dir):
            raise Exception("{} already exists.".format(big_dir))
        os.makedirs(big_dir)
        with open(os.path.join(big_dir, "root"), "w") as f:
            f.write(self.root.replace(os.environ["FLOW_PROJECTS_DIR"], "${FLOW_PROJECTS_DIR}").replace("\\", "/"))
    
    def create_step(self, name):
        entity_config = self._config.entities[self.properties["type"]]
        step_config = entity_config.tasks[name]
        work_root_template = self.config.templates[step_config["work_root_template"]]
        fields = dict(self.fields)
        fields["Step"] = {
            "name": name,
        }
        work_root = work_root_template.format(fields)
        publish_root_template = self.config.templates[entity_config.tasks[name]["publish_root_template"]]
        publish_root = publish_root_template.format(fields)
        if not os.path.exists(work_root):
            os.makedirs(work_root)
        if not os.path.exists(publish_root):
            os.makedirs(publish_root)
