#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#

from . import cprint
import os
import yaml

#
# get deps file path ##########################################################
#

def make_config_path(dir):
    return os.path.join(dir, 'deps.yml')

#
# init config #################################################################
#

def init_config(dir):
    configPath = make_config_path(dir)
    if not os.path.exists(configPath):
        config = {
            'repo': {
                'cloneDir': 'extern'
            },
            'dependencies': {}
        }

        save_config(dir, config)

#
# load config #################################################################
#

def load_config(dir, create=False):
    configPath = make_config_path(dir)
    if not os.path.exists(configPath):
        if create:
            init_config(dir)
        else:
            return None

    with open(configPath, 'r') as f:
        ymlString = f.read()
        config = yaml.load(ymlString)

    return config

#
# save config #################################################################
#

def save_config(dir, config):
    configPath = make_config_path(dir)

    with open(configPath, 'w') as f:
        ymlString = yaml.dump(config, f)

#
# add dependency ##############################################################
#

def add_dependency(config, name, repo, sha=None, tag=None):
    deps = config['dependencies']
    if deps is None:
        deps = {}

    if not name in deps:
        entry = { 'repo': repo }
        if not sha is None:
            entry['sha'] = sha
        if not tag is None:
            entry['tag'] = tag

        deps[name] = entry

    return config

#
# add dependency file #########################################################
#

def add_dependency_to_file(dir, name, repo, sha=None, tag=None):
    config = load_config(dir, create=True)
    if not config is None:
        config = add_dependency(config, name, repo, sha, tag)
        save_config(dir, config)

#
# remove dependency ###########################################################
#

def remove_dependency(config, name):
    deps = config['dependencies']
    if name in deps:
        del deps[name]
    return config

#
# remove dependency file ######################################################
#

def remove_dependency_from_file(dir, name):
    config = load_config(dir)
    if not config is None:
        config = remove_dependency(config, name)
        save_config(dir, config)

