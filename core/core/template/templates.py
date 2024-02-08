import glob
from lucidity import Template as LucidityTemplate, ParseError
import sys
import yaml
import os
import re
if sys.version_info[0] == 2:
    UserDict = dict
else:
    from collections import UserDict

def _normalize_backslashes(match):
    groups = match.groupdict()
    if groups["other"] is not None:
        return groups["other"].replace("\\", "/")
    return groups["placeholder"]

class Template(LucidityTemplate):

    def __init__(
            self,
            name,
            pattern,
            anchor,
            default_placeholder_expression='[\w_.\-]+',
            duplicate_placeholder_mode=1,
            template_resolver=None,
            paths_mapping=None):
        self._expanded_pattern = None
        self._references = None
        self._regular_expression = None
        self._expanded_regular_expression = None
        super(Template, self).__init__(
            name,
            pattern,
            anchor,
            default_placeholder_expression=default_placeholder_expression,
            duplicate_placeholder_mode=duplicate_placeholder_mode,
            template_resolver=template_resolver)
        self._paths_mapping = paths_mapping or {}
        
    
    def expanded_pattern(self):
        if self._expanded_pattern is None:
            self._expanded_pattern = super(Template, self).expanded_pattern()
        return self._expanded_pattern
    
    def references(self):
        if self._references is None:
            self._references = super(Template, self).references()
        return self._references
    
    def _construct_regular_expression(self, pattern):
        if pattern == self._pattern:
            if self._regular_expression is None:
                self._regular_expression = super(Template, self)._construct_regular_expression(pattern)
            return self._regular_expression
        if pattern == self.expanded_pattern():
            if self._expanded_regular_expression is None:
                self._expanded_regular_expression = super(Template, self)._construct_regular_expression(pattern)
            return self._expanded_regular_expression
        else:
            return super(Template, self)._construct_regular_expression(pattern)
    
    def parse(self, path):
        for search, replace in self._paths_mapping.items():
            if path.startswith(search):
                path = replace + path[len(search):]
        return super(Template, self).parse(path)

class Templates(UserDict):

    def __init__(self):
        super(Templates, self).__init__()
        self._templates = {}
        self._paths_mapping = {}
    
    def load(self, path):
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        self._paths_mapping = data.get("paths_mapping", {})
        for key, definition in data["templates"].items():
            template = self.create_template(key, definition)
            self._templates[key] = template
    
    def __getitem__(self, key):
        return self._templates[key]
    
    def create_template(self, name, definition):
        definition = os.path.expandvars(definition)
        definition = re.sub(
            r'(?P<placeholder>{(.+?)(:(\\}|.)+?)?})|(?P<other>.+?)',
            _normalize_backslashes,
            definition
        )

        return Template(
            name=name,
            pattern=definition,
            template_resolver=self._templates,
            duplicate_placeholder_mode=Template.STRICT,
            anchor=Template.ANCHOR_BOTH,
            paths_mapping=self._paths_mapping,
        )
    
    def keys(self):
        return self._templates.keys()
    
    def items(self):
        return self._templates.items()
    
    def values(self):
        return self._templates.values()
    
    def get_parent_template_from_path(self, path):
        current = path
        previous = None
        template = None
        while previous != current:
            template = self.get_template_from_path(current)
            if template:
                return template, current
            previous = current
            current = os.path.dirname(current)
        return None, None

    def get_template_from_path(self, path, templates=None):
        if templates is None:
            templates = sorted(self._templates.values(), key=lambda t: t.expanded_pattern())
        path = path.replace("\\", "/")
        for template in templates:
            if not isinstance(template, Template):
                template = self._templates[template]
            try:
                template.parse(path)
                return template
            except ParseError:
                continue
    
    def get_paths_from_template(self, template, fields=None):
        if not isinstance(template, Template):
            template = self._templates[template]
        
        if fields is None:
            fields = {}
        
        for key in template.keys():
            current = fields
            parts = key.split(".")
            for key_part in parts[:-1]:
                current = current.setdefault(key_part, {})
            if parts[-1] not in current:
                current[parts[-1]] = "*"
        
        pattern = template.format(fields)
        _paths = glob.glob(pattern)
        paths = []
        for path in _paths:
            path = path.replace("\\", "/")
            try:
                template.parse(path)
                paths.append(path)
            except ParseError as e:
                continue
        return paths

