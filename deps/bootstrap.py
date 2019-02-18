#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#

from . import cprint
from . import file as depsfile
from . import project
from pathlib import Path

import git
import os
import yaml

#
# fetch dependency ############################################################
#

def fetch_dependency(dirs, name, dep, loadedRepos=[]):
    cprint.info('\t loading dep ', name, ' into ', dirs[0])

    dir = dirs[0]
    repoDir = os.path.join(dir, name)
    origDir = os.path.join(dirs[-1], name)

    # if we've already loaded this repo, print a string and make an empty
    # directory
    if dep['repo'] in loadedRepos:
        repoDir = os.path.join(dirs[-1], name)
        cprint.info('\t Already loaded ', dep['repo'], ' making placeholder folder in ', repoDir )
        os.makedirs(repoDir)
        return
        
    # configure our clone arguments, setting the location to clone to and the
    # tag if it was passed to us
    cloneArgs = [name]
    if 'tag' in dep:
        cloneArgs.extend(['--branch', dep['tag']])
        
    # clone the directory if it doesnt already exist, and checkout the
    # requested commit if available
    if not os.path.exists(repoDir):
        git.Git(dir).clone(dep['repo'], *cloneArgs)
        repo = git.Repo(repoDir)
        if 'sha' in dep:
            repo.git.checkout(dep['sha'])

    # put an empty file in the deps directory, since we are moving them to
    # the top level project
    if not os.path.exists(origDir):
        os.makedirs(origDir)
        Path(os.path.join(origDir, 'CMakeLists.txt')).touch()

    loadedRepos.append(dep['repo'])

#
# load config #################################################################
#

def load_deps(dir):
    config = depsfile.load_config(dir)
    if config is None:
        return
    
    if 'repo' not in config:
        cprint.err('Could not find `repo` key in config', config)

    cloneDir = os.path.join(dir, config['repo']['cloneDir']);
    cloneDirs.append(cloneDir)
    
    if not os.path.exists(cloneDir):
        os.makedirs(cloneDir)
    
    #
    # clone dependencies ######################################################
    #
    
    if not config is None and 'dependencies' in config:
        deps = config['dependencies']
        for name in deps:
            fetch_dependency(cloneDirs, name, deps[name], loadedRepos)
            
        # for each of our dependencies, check to see if we have any tracked
        # dependencies, and handle them appropriately
        for name in deps:
            load_deps(os.path.join(cloneDir,name), cloneDirs, loadedRepos)

#
# bootstrap ###################################################################
#

def bootstrap(dir):
    cprint.info('bootstrapping ', dir)
    depsfile.init_config(dir)
    load_deps(dir)
