#!/usr/bin/python3

#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#


#
# imports #####################################################################
#
import git
import os
import yaml

#
# load config #################################################################
#

rootDir = os.getcwd()
loadedRepos = []

def load_deps(dir, cloneDir=None):
    config = None
    depsPath = os.path.join(dir, 'deps.yml')
    print(depsPath)
    if not os.path.exists(depsPath):
        return

    with open(depsPath) as f:
        yml = f.read();
        config = yaml.load(yml)
    
    if cloneDir is None:
        cloneDir = os.path.join(dir, config["repo"]['cloneDir'])
    
    if not os.path.exists(cloneDir):
        os.makedirs(cloneDir)
    
    #
    # clone dependencies ##########################################################
    #
    
    if not config is None and 'dependencies' in config:
        deps = config['dependencies']
        for name in deps:
            repoDir = os.path.join(cloneDir, name)
            print('\tloading dep', name, 'into', repoDir)
            dep = deps[name]

            if dep['repo'] in loadedRepos:
                print('Already loaded', dep['repo'])
                os.makedirs(repoDir)
                return
        
            cloneArgs = [name]
            if 'tag' in dep:
                cloneArgs.extend(['--branch', dep['tag']])
        
            loadedRepos.append(dep['repo'])
            if not os.path.exists(repoDir):
                git.Git(cloneDir).clone(dep['repo'], *cloneArgs)

            repo = git.Repo(repoDir)
        
            if 'sha' in dep:
                repo.git.checkout(dep['sha'])

        for name in deps:
            load_deps(os.path.join(cloneDir,name), cloneDir)

load_deps(rootDir)
