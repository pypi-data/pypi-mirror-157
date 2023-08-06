# -*- coding:utf-8 -*-

import os
import time
from com.dvsnier.config.journal.compat_logging import logging
from com.dvsnier.process.execute import execute
from com.dvsnier.std_bm.abstract_branch_model import AbstractBranchModel


class BranchModel(AbstractBranchModel, object):
    '''the branch model class'''

    __flags = 0

    def __init__(self):
        super(BranchModel, self).__init__()
        self.directory.set_work_region_space(os.getcwd())

    def execute(self, dest_project, is_associate_remote=False, flags=0):
        '''
            the start executing standard branch model policy

            the notice:

                flags parameters:

                    1. flags == 1, do not delete branch list of local repository
        '''
        start = time.time()
        self.__flags = flags
        if isinstance(dest_project, list):
            for project in dest_project:
                self.__execute_with_simple(project, is_associate_remote)
        elif isinstance(dest_project, str):
            self.__execute_with_simple(dest_project, is_associate_remote)
        else:
            raise KeyError(
                'the current parameter is invalid and illegal. only str and list absolute path methods are supported')
        end = time.time()
        logging.info('the execute branch model has completed, that total time consumed {:.3f} seconds '.format(end -
                                                                                                               start))

    def __execute_with_simple(self, dest_project, is_associate_remote=False):
        if dest_project and os.path.exists(dest_project):
            self.directory.set_executed_region_space(dest_project)
            logging.warning('the current destination directory that is {}s '.format(dest_project))
            os.chdir(dest_project)
            self.write_original_and_stash_git_branch()
            if self.has_remote():  # the remote repository
                if is_associate_remote:
                    self.__execute_with_remote()
                else:
                    self.__execute_with_local()
            else:  # the local repository
                self.__execute_with_local()

    def __execute_with_local(self):
        execute(['git stash'])
        if self.has_specifical_branch(self.MICRO_FEATURE):
            execute(['git checkout {}'.format(self.MICRO_FEATURE)])
        elif self.has_specifical_branch(self.MICRO_KERNEL):
            execute(['git checkout {}'.format(self.MICRO_KERNEL)])
        else:
            pass
        self.__detection_and_repaired_branch(self.MICRO_FEATURE, self.MICRO_FEATURE, is_remote=False)
        self.__detection_and_repaired_branch(self.MICRO_KERNEL, self.MICRO_KERNEL, is_remote=False)
        if self.has_specifical_branch(self.MINOR_DEVELOPER):
            execute(['git checkout {}'.format(self.MINOR_DEVELOPER)])
        elif self.has_specifical_branch(self.MINOR_HOTFIX):
            execute(['git checkout {}'.format(self.MINOR_HOTFIX)])
        else:
            pass
        self.__detection_and_repaired_branch(self.MINOR_DEVELOPER, self.MINOR_DEVELOPER, is_remote=False)
        self.__detection_and_repaired_branch(self.MINOR_HOTFIX, self.MINOR_HOTFIX, is_remote=False)
        if self.has_specifical_branch(self.DEPRECATED_MAJOR_MASTER):
            execute(['git checkout {}'.format(self.DEPRECATED_MAJOR_MASTER)])
        elif self.has_specifical_branch(self.MAJOR_MAIN):
            execute(['git checkout {}'.format(self.MAJOR_MAIN)])
        elif self.has_specifical_branch(self.MAJOR_DEPLOY):
            execute(['git checkout {}'.format(self.MAJOR_DEPLOY)])
        elif self.has_specifical_branch(self.MAJOR_RELEASE):
            execute(['git checkout {}'.format(self.MAJOR_RELEASE)])
        else:
            pass
        self.__detection_and_repaired_branch(self.DEPRECATED_MAJOR_MASTER, self.MAJOR_MAIN, is_remote=False)
        self.__detection_and_repaired_branch(self.MAJOR_MAIN, self.MAJOR_MAIN, is_remote=False)
        self.__detection_and_repaired_branch(self.MAJOR_DEPLOY, self.MAJOR_DEPLOY, is_remote=False)
        self.__detection_and_repaired_branch(self.MAJOR_RELEASE, self.MAJOR_RELEASE, is_remote=False)
        self.update_or_synchronization_local_git_branch_with_no_me()

    def __execute_with_remote(self):
        execute(['git stash'])
        if self.has_specifical_branch(self.MICRO_FEATURE, is_remote=True):
            execute(['git checkout {}'.format(self.MICRO_FEATURE)])
        elif self.has_specifical_branch(self.MICRO_KERNEL, is_remote=True):
            execute(['git checkout {}'.format(self.MICRO_KERNEL)])
        else:
            pass
        self.__detection_and_repaired_branch(self.MICRO_FEATURE, self.MICRO_FEATURE, is_remote=True)
        self.__detection_and_repaired_branch(self.MICRO_KERNEL, self.MICRO_KERNEL, is_remote=True)
        if self.has_specifical_branch(self.MINOR_DEVELOPER, is_remote=True):
            execute(['git checkout {}'.format(self.MINOR_DEVELOPER)])
        elif self.has_specifical_branch(self.MINOR_HOTFIX, is_remote=True):
            execute(['git checkout {}'.format(self.MINOR_HOTFIX)])
        else:
            pass
        self.__detection_and_repaired_branch(self.MINOR_DEVELOPER, self.MINOR_DEVELOPER, is_remote=True)
        self.__detection_and_repaired_branch(self.MINOR_HOTFIX, self.MINOR_HOTFIX, is_remote=True)
        if self.has_specifical_branch(self.DEPRECATED_MAJOR_MASTER, is_remote=True):
            execute(['git checkout {}'.format(self.DEPRECATED_MAJOR_MASTER)])
        elif self.has_specifical_branch(self.MAJOR_MAIN, is_remote=True):
            execute(['git checkout {}'.format(self.MAJOR_MAIN)])
        elif self.has_specifical_branch(self.MAJOR_DEPLOY, is_remote=True):
            execute(['git checkout {}'.format(self.MAJOR_DEPLOY)])
        elif self.has_specifical_branch(self.MAJOR_RELEASE, is_remote=True):
            execute(['git checkout {}'.format(self.MAJOR_RELEASE)])
        else:
            pass
        self.__detection_and_repaired_branch(self.DEPRECATED_MAJOR_MASTER, self.MAJOR_MAIN, is_remote=True)
        self.__detection_and_repaired_branch(self.MAJOR_MAIN, self.MAJOR_MAIN, is_remote=True)
        self.__detection_and_repaired_branch(self.MAJOR_DEPLOY, self.MAJOR_DEPLOY, is_remote=True)
        self.__detection_and_repaired_branch(self.MAJOR_RELEASE, self.MAJOR_RELEASE, is_remote=True)
        if self.__flags == 1:
            self.update_or_synchronization_local_git_branch_with_no_me()
        else:
            self.update_or_synchronization_original_git_branch()

    def __detection_and_repaired_branch(self, detection_name, betterment_name, is_remote=False):
        if detection_name:
            execute(['git stash'])
            if self.has_specifical_branch(detection_name, is_remote):
                checkout_result = execute(['git checkout {}'.format(detection_name)])
                if checkout_result:
                    logging.debug('The current branch name is switched that is {}'.format(detection_name))
                if betterment_name and detection_name != betterment_name:
                    execute(['git branch -m {}'.format(betterment_name)])
                    if is_remote:
                        execute(['git push -u origin {}:{}'.format(betterment_name, betterment_name)])
                        execute(['git push origin :{}'.format(detection_name)])
                    logging.debug('The current branch name is repaired that is {}'.format(betterment_name))
                else:
                    logging.debug('The current branch name({}) does not need to be modified and then skipped.'.format(
                        betterment_name))
            else:
                if betterment_name and not self.has_specifical_branch(betterment_name, is_remote):
                    execute(['git checkout -b {}'.format(betterment_name)])
                    if is_remote:
                        # execute(['git checkout -b {} --track {}/{}'.format(betterment_name, 'origin', betterment_name)])
                        execute(['git push -u origin {}:{}'.format(betterment_name, betterment_name)])
                    logging.debug('The current branch name is created that is {}'.format(betterment_name))
                else:
                    logging.debug('The current branch name({}) does not need to be modified and then skipped.'.format(
                        betterment_name))
