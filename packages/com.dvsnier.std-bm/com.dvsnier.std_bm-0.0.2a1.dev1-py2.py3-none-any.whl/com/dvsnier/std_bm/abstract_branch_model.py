# -*- coding:utf-8 -*-

import os
import pickle
import sys
import tempfile
from com.dvsnier.config.journal.compat_logging import logging
from com.dvsnier.directory.base_file import BaseFile
# from com.dvsnier.git.branch.branch import Branch
from com.dvsnier.process.execute import execute
from com.dvsnier.std_bm.imodel import IModel


class AbstractBranchModel(IModel, object):
    '''the abstract branch model class'''
    def __init__(self):
        super(AbstractBranchModel, self).__init__()
        self.directory = BaseFile(True)
        self.temp_dir = tempfile.mkdtemp(prefix='dvs-bsm-')

    def get_current_branch_list(self):
        'the current branch list'
        branch_queue = []
        branch_list_strs = execute(['git branch --list']).strip()
        if branch_list_strs:
            branch_list = branch_list_strs.split('\n')
            if branch_list:
                for branch in branch_list:
                    branch_element = branch.split(' ')
                    if branch_element:
                        branch_queue.append(branch_element[-1])
        return branch_queue

    def get_remote_branch_list(self):
        'the current remote branch list'
        branch_queue = []
        branch_list_strs = execute(['git branch --remotes']).strip()
        if branch_list_strs:
            branch_list = branch_list_strs.split('\n')
            if branch_list:
                for branch in branch_list:
                    branch_element = branch.split(' ')
                    if branch_element:
                        branch_queue.append(branch_element[-1])
        return branch_queue

    def get_remote_prune(self):
        'the remote prune'
        prune_result = execute(['git remote prune origin'])
        return prune_result

    def has_remote(self):
        'the judge whether the current git repository is associated with the remote repository'
        local_result = execute(['git config --local --list'])
        if local_result and local_result.find('remote.origin.url') >= 0 and local_result.find(
                'remote.origin.fetch') >= 0:
            return True
        return False

    def has_specifical_branch(self, branch_name, is_remote=False):
        'the judge whether the current git repository is specifical branch name'
        branch_list = []
        if is_remote:
            branch_list = self.get_remote_branch_list()
            if branch_name:
                branch_name = 'origin/' + branch_name
            else:
                raise KeyError('the current branch name is an invalid parameter value')
        else:
            branch_list = self.get_current_branch_list()
        if branch_name and branch_list and len(branch_list) > 0 and branch_name in branch_list:
            return True
        return False

    def update_or_synchronization_local_git_branch_with_no_me(self):
        '''
            Update or synchronize the original branch list, and then all branches except me are deleted, local repository only
        '''
        branch_queue = self.get_current_branch_list()
        # current_branch_name = Branch().get_branch()
        wrs = self.directory.get_work_region_space()
        if wrs and isinstance(wrs, str):
            pgs_file_name = os.path.join(self.temp_dir, 'python_git_branch_synchronization.pkl')
            original_branch_queue = pickle.load(open(pgs_file_name, 'rb'))
            if original_branch_queue:
                logging.info('the currently load file directory is {} that load local branch list is {}'.format(
                    pgs_file_name, original_branch_queue))
                if branch_queue:
                    execute(['git checkout {}'.format(original_branch_queue[0])])
                    # for branch_name in branch_queue:
                    #     if branch_name == current_branch_name or branch_name in original_branch_queue:
                    #         continue
                    #     else:
                    #         result = execute(['git branch -d {}'.format(branch_name)])
                    #         if result:
                    #             logging.warning('{}'.format(result))
                    #             logging.debug('the current local branch {} associated with remote has been deleted'.format(branch_name))
            else:
                if branch_queue and 'developer' in branch_queue:
                    execute(['git checkout {}'.format('developer')])
            os.remove(pgs_file_name)

    def update_or_synchronization_original_git_branch(self):
        '''
            Update or synchronize the original branch list,\
            so as to avoid the situation that a large number of local and remote branches are associated with each statistical data
        '''
        wrs = self.directory.get_work_region_space()
        if wrs and isinstance(wrs, str):
            pgs_file_name = os.path.join(self.temp_dir, 'python_git_branch_synchronization.pkl')
            original_branch_queue = pickle.load(open(pgs_file_name, 'rb'))
            logging.info('the currently load file directory is {} that load local branch list is {}'.format(
                pgs_file_name, original_branch_queue))
            current_branch_queue = self.get_current_branch_list()
            if current_branch_queue and original_branch_queue:
                execute(['git checkout {}'.format(original_branch_queue[0])])
                for branch_name in current_branch_queue:
                    if branch_name in original_branch_queue:
                        continue
                    else:
                        result = execute(['git branch -d {}'.format(branch_name)])
                        if result:
                            logging.warning('{}'.format(result))
                            logging.debug(
                                'the currently, the local branch {} associated with remote has been deleted'.format(
                                    branch_name))
            os.remove(pgs_file_name)

    def write_original_and_stash_git_branch(self):
        '''
            The staging branch is written to the specified file,\
            and it is restored to the state before statistics after the data has been made available for subsequent statistics
        '''
        original_branch_queue = self.get_current_branch_list()
        if original_branch_queue and self.directory:
            if self.DEPRECATED_MAJOR_MASTER in original_branch_queue:
                original_branch_queue.remove(self.DEPRECATED_MAJOR_MASTER)
            wrs = self.directory.get_work_region_space()
            if wrs and isinstance(wrs, str):
                pgs_file_name = os.path.join(self.temp_dir, 'python_git_branch_synchronization.pkl')
                with open(pgs_file_name, 'wb') as output:
                    if sys.version_info.major >= 3:
                        pickle.dump(original_branch_queue, output, pickle.DEFAULT_PROTOCOL)
                    else:
                        pickle.dump(original_branch_queue, output)
                    logging.info('the currently written file directory is {} that write local branch list is {}'.format(
                        pgs_file_name, original_branch_queue))
        else:
            logging.warning('the current local branch list is invaild, skipping the process of writing to file.')
