#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#

from . import cprint
from . import file as dfile

from pathlib import Path
import git
import os
import yaml

#
# dependency class ############################################################
#

class Dependency:
    """ Represents a project dependency """

    #
    # members #################################################################
    #

    # (required) the name of this dependency
    name = None

    # (required) the uri for the git repository of this dependency
    repo = None

    # (optional) the git tag this dependency is currently set to
    tag = None

    # (optional) the commit sha this dependency is set to
    sha = None

    # (optional) the patch name to apply after pulling this dependency
    patch = None

    # (required) the root project that this dependency was pulled into
    project = None

    #
    # properties ##############################################################
    #

    @property
    def cloneArgs(self):
        result = [self.name]
        if self.tag:
            result.extend(['--branch', self.tag])

    #
    # constructor #############################################################
    #

    def __init__(self, name, project, yml):
        self.name = name
        self.project = project
        if 'repo' not in yml:
            raise ValueException('Dependency %s does not have a value for repo' % (name))

        self.repo = yml['repo']
        if 'tag' in yml:
            self.tag = yml['tag']

        if 'sha' in yml:
            self.sha = yml['sha']

        if 'patch' in yml:
            self.patch = yml['patch']

    #
    # public methods ##########################################################
    #
    
    def install(self):
        cloneArgs = self.cloneArgs
        git.Git(self.project.installDirectory).clone(self.repo, *cloneArgs)
        repoDir = os.path.join(self.project.installDirectory, self.name)
        repo = git.Repo(repoDir)
        if self.sha:
            repo.git.checkout(self.sha)

        if self.patchName:
            patchPath = os.path.join(self.project.patchDirectory, self.patch)
            repo.git.apply([patchPath])

    #
    # end class ###############################################################
    #

#
# project config class ########################################################
#

class ProjectConfig:
    """ Represents the configuration of a project """

    #
    # members #################################################################
    #

    # the root path of the project
    rootDir = None

    # the path dependencies are installed into
    installDir = None

    # the path patches are stored for this project
    patchDir = None

    # the raw yml config for this project
    yml = None

    #
    # constructor #############################################################
    #

    def __init__(self, dir, ymlConfig):
        self.yml = ymlConfig
        self.rootDir = dir
        if 'installDir' not in self.yml:
            raise ValueException('Project configuration does not contain an installDir')

        if 'patchDir' not in self.yml:
            raise ValueException('Project configuration does not contain a patchDir')

        self.installDir = os.path.join(self.rootDir, self.yml['installDir']
        self.patchDir = os.path.join(self.rootDir, self.yml['patchDir']

    #
    # public methods ##########################################################
    #

    #
    # end class ###############################################################
    #

#
# project class ###############################################################
#

class Project:
    """Represents a project with dependencies"""

    #
    #  members ################################################################
    #

    # the directory of this project, if this is the root project it is the
    # same s the rootDirectory, if this is a subproject, it is the location
    # of the project inside the main project
    directory = None

    # the root project if this is a sub-dependency, otherwise None
    parent = None

    # the configuration for this project
    config = None

    # the raw yml configuration for this project
    yml = None

    # a list of the dependencies this project has
    dependencies = []

    #
    # properties ##############################################################
    #

    @property
    def rootDirectory(self):
        if self.parent:
            return self.parent.rootDirectory

        return self.directory

    #
    # -------------------------------------------------------------------------
    #

    @property
    def installDirectory(self):
        if self.parent:
            return self.parent.installDirectory

        return os.path.join(self.rootDirectory, self.config.installDir)

    #
    # -------------------------------------------------------------------------
    #

    @property
    def patchDirectory(self):
        if self.parent:
            return self.parent.patchDirectory

        return os.path.join(self.rootDirectory, self.config.patchDir)

    #
    # constructor #############################################################
    #

    def __init__(self, directory, parent=None):
        self.directory = os.path.realpath(directory)
        self.yml = dfile.load_config(self.directory)
        self.parent = parent

        if 'project' not in self.yml:
            raise ValueException('deps.yml file does not have a project section', self.directory)

        self.config = ProjectConfig(self.yml['project'])

    #
    # public methods ##########################################################
    #

    def install(self):
        if 'dependencies' not in self.yml:
            cprint.warn('No dependencies found in project', self.directory)

        deps = self.yml['dependencies']
        for name in deps:
            self.installDependency(name, deps[name])

    #
    # -------------------------------------------------------------------------
    #

    def installDependency(self, name, yml):
        dep = Depencency(name, self, yml)
        if not self.isInstalled(dep):
            dep.install()
            if self.parent:
                self.parent.dependencies.append(dep)
            self.dependencies.append(dep)

    #
    # -------------------------------------------------------------------------
    #

    def isInstalled(self, dep):
        # all deps are installed to the root project so check there first
        if self.parent:
            return self.parent.isInstalled(dep)

        # otherwise we are the root, check our dependency list
        for check in self.dependencies:
            if check.repo == dep.repo:
                return True
        return False

    #
    # end class ###############################################################
    #
