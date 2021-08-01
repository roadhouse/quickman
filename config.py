import yaml
from collections import ChainMap


class Config:
    """config object"""
    def __init__(self, file_path):
        self.file_path = file_path

    def config_file_content(self):
        """ config in json """
        with open(self.file_path) as content:
            return yaml.safe_load(content)

    def wrap_segments(self, path):
        """ wrap all jsonpath segments with single quotes """
        return map(lambda segment: "'{0}'".format(segment), path)

    def jsonpath(self, path):
        """ generate jsonpath string """
        return '.'.join(["$"] + list(self.wrap_segments(path)))

    def realpaths(self, entry):
        """ concatenate the base segment with the attr segment """
        base = entry['base']
        paths = entry['fields']

        def path(attr_name):
            return base + [paths[attr_name]]

        def jpaths(attr):
            return (attr, self.jsonpath(path(attr)))

        return dict(map(jpaths, paths.keys()))

    def jsonpaths(self):
        """ all generate jsonpaths contained in config file """
        cfg = self.config_file_content()["kismet"]
        groups = cfg.keys()

        def paths_from_group(group):
            return self.realpaths(cfg[group])

        return dict(ChainMap(*map(paths_from_group, groups)))
