#
# (C) BLACKTRIANGLES 2019
# http://www.blacktriangles.com
#

from . import cprint
from . import file as dfile
from . import project

import git
import os

#
# create patch ################################################################
#

def create_patch(dir, name):
    cprint.info('patching ', name, ' in ', dir)
    config = dfile.load_config(dir)
    if not config:
        cprint.err('could not load config at ', dir)
        return

    config = project.ProjectConfig(dir, config['project'])

    repoPath = os.path.join(config.installDir, name)
    if not os.path.exists(repoPath):
        cprint.err('could not find repo at ', repoPath)
        return

    repo = git.Repo(repoPath)
    if not repo:
        cprint.err('could not load repo at ', repoPath)
        return

    repo.git.add(all=True)
    diff = repo.git.diff(staged=True)

    if not os.path.exists(config.patchDir):
        os.makedirs(config.patchDir)

    patchPath = os.path.join(config.patchDir, name)
    with open(patchPath, 'w') as f:
        f.write(diff+'\n')
