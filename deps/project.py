#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#

from . import cprint
from . import file as dfile

from pathlib import Path
import git
import os
import platform
import subprocess

#
# dependency class ############################################################
#

class Dependency:
    """ Represents a project dependency """

    #
    # members #################################################################
    #

    # the root directory of this dependency
    directory = None

    # (required) the name of this dependency
    name = None

    # (required) the uri for the git repository of this dependency
    repo = None

    # (optional) the git tag this dependency is currently set to
    tag = None

    # (optional) the commit sha this dependency is set to
    sha = None

    # (required) the root project that this dependency was pulled into
    project = None

    # (required) a list of commands to execute afer syncing this repo
    commands = []

    #
    # properties ##############################################################
    #

    @property
    def cloneArgs(self):
        result = [self.name]
        if self.tag:
            result.extend(['--branch', self.tag])

        return result

    #
    # constructor #############################################################
    #

    def __init__(self, name, project, yml):
        self.name = name
        self.project = project
        if 'repo' not in yml:
            raise ValueError('Dependency %s does not have a value for repo' % (name))

        self.repo = yml['repo']
        if 'tag' in yml:
            self.tag = yml['tag']

        if 'sha' in yml:
            self.sha = yml['sha']

        if 'cmds' in yml:
            self.commands = yml['cmds']

    #
    # public methods ##########################################################
    #

    def install(self, force_cmd):
        cprint.info('\tinstalling: ', self.name)
        cloneArgs = self.cloneArgs
        self.directory = os.path.join(self.project.installDirectory, self.name)

        fresh = False
        if not os.path.exists(self.directory):
            git.Git(self.project.installDirectory).clone(self.repo, *cloneArgs)
            fresh = True

        repo = git.Repo(self.directory)
        if self.sha:
            repo.git.checkout(self.sha)
            fresh = True

        if fresh:
            # apply the patch
            patchPath = os.path.join(self.project.patchDirectory, self.name)
            if os.path.exists(patchPath):
                cprint.info('\t\tpatch found at ', patchPath)
                repo.git.apply([patchPath])

        if fresh or force_cmd:
            #
            # execute the commands
            #
            if len(self.commands) > 0:
                platform_name = platform.system().lower()
                if platform_name in self.commands:
                    cwd = self.directory
                    cmd_list = self.commands[platform_name.lower()]
                    for cmd in cmd_list:
                        cmda = cmd.split(' ')
                        print('##### Executing: %s' % (cmd))
                        try:
                            output = subprocess.check_call(cmda, cwd=cwd)
                            print(output)
                        except subprocess.CalledProcessError as e:
                            print('##### FAILED #####\n %s' % (' '.join(cmd)))

                        print('')


        # if we are a subproject, we should create placeholders so we dont
        # break subproject cmake project
        subprojDir = os.path.join(self.project.config.installDir, self.name)
        if self.directory != subprojDir and not os.path.exists(subprojDir):
            os.makedirs(subprojDir)
            Path(os.path.join(subprojDir,'CMakeLists.txt')).touch()

    #
    # -------------------------------------------------------------------------
    #

    def getProject(self):
        if not self.directory:
            return None

        config = dfile.load_config(self.directory)
        if not config:
            return None

        return Project(self.directory, self.project)

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
            raise ValueError('Project configuration does not contain an installDir')

        if 'patchDir' not in self.yml:
            raise ValueError('Project configuration does not contain a patchDir')

        self.installDir = os.path.join(self.rootDir, self.yml['installDir'])
        self.patchDir = os.path.join(self.rootDir, self.yml['patchDir'])

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

    # projects contained in this project
    subprojects = []

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
        return os.path.join(self.rootDirectory, self.config.patchDir)

    #
    # constructor #############################################################
    #

    def __init__(self, directory, parent=None):
        cprint.warn(directory)
        self.directory = os.path.realpath(directory)
        self.yml = dfile.load_config(self.directory)
        self.parent = parent

        if 'project' not in self.yml:
            raise ValueError('deps.yml file does not have a project section', self.directory)

        self.config = ProjectConfig(directory, self.yml['project'])

    #
    # public methods ##########################################################
    #

    def install(self, force_cmd):
        cprint.info('installing ', self.directory)
        if 'dependencies' not in self.yml:
            cprint.warn('No dependencies found in project', self.directory)

        deps = self.yml['dependencies']
        for name in deps:
            dep = self._installDependency(name, deps[name], force_cmd)
            if dep or force_cmd:
                subproject = dep.getProject()
                if subproject is not None:
                    subproject.install(force_cmd)
                    self.subprojects.append(subproject)

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
    # private methods #########################################################
    #

    def _installDependency(self, name, yml, force_cmd):
        dep = Dependency(name, self, yml)
        if not self.isInstalled(dep):
            dep.install(force_cmd)
            if self.parent:
                self.parent.dependencies.append(dep)
            self.dependencies.append(dep)
            return dep

    #
    # end class ###############################################################
    #
