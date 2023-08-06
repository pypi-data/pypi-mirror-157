# -*- coding:utf-8 -*-

import argparse
import json
import os
from com.dvsnier.config.journal.compat_logging import logging
from com.dvsnier.std_bm import DEBUGGER, VERSIONS
from com.dvsnier.std_bm.branch_model import BranchModel
import sys


def execute(args=None):
    ''' the execute command '''
    if args is None:
        args = sys.argv[1:]
    logging.set_kw_output_dir_name(os.path.join(os.getcwd(), 'out', 'dvs-bsm')).set_kw_file_name('log').set_kw_level(
        logging.DEBUG).set_logging_name('dvs-bsm').build()
    parser = argparse.ArgumentParser(prog='dvs-bsm', description='this is a standard branch model execution program.')
    parser.add_argument('-V', '--version', action='version', version=VERSIONS, help='the show version and exit.')
    parser.add_argument('dest_project',
                        action='store',
                        nargs='+',
                        metavar='destination-project-or-list',
                        help='the project directory of the branch model to be standardized')
    parser.add_argument('-cp',
                        '--current-project',
                        action='store',
                        nargs=1,
                        default=os.getcwd(),
                        type=str,
                        metavar='current-project',
                        dest='current_project',
                        help='the current execution directory')
    parser.add_argument('-pf',
                        '--project-prefix',
                        action='store',
                        nargs=1,
                        default=os.getcwd(),
                        type=str,
                        metavar='project-prefix',
                        dest='project_prefix',
                        help='the current project prefix directory')
    parser.add_argument('-nd',
                        '--local-flag',
                        action='store_true',
                        default=False,
                        dest='flag',
                        help='if flags == true, do not delete branch list of local repository, otherwise delete it.')
    parser.add_argument(
        '-r',
        '--associate-remote',
        action='store_true',
        default=False,
        dest='is_associate_remote',
        help='if associate-remote == true, do associate branch list of remote repository, otherwise not it.')
    args = parser.parse_args(args)
    run(args)


def run(args):
    ''' the run script command '''
    model = BranchModel()
    # if args.current_project:
    #     print('args.current_project: {}'.format(args.current_project))
    # if args.dest_project:
    #     print('args.dest_project: {}'.format(args.dest_project))
    # if args.project_prefix:
    #     print('args.project_prefix: {}'.format(args.project_prefix))
    # if args.flag:
    #     print('args.flag: {}'.format('1'))
    # else:
    #     print('args.flag: {}'.format('0'))
    # if args.is_associate_remote:
    #     print('args.is_associate_remote: {}'.format(args.is_associate_remote))
    # else:
    #     print('args.is_associate_remote: {}'.format(args.is_associate_remote))
    # # logging.error('vars(args): {}'.format(json.dumps(vars(args), indent=4)))
    if DEBUGGER:
        # print('vars(args): {}'.format(vars(args)))
        logging.warning('the current config(args): {}'.format(json.dumps(vars(args), indent=4)))
    if args.dest_project:
        if args.is_associate_remote:
            model.execute(args.dest_project, is_associate_remote=args.is_associate_remote)
        else:
            if args.flag:
                model.execute(args.dest_project, flags=1)
            else:
                model.execute(args.dest_project)


if __name__ == "__main__":
    '''the main function entry'''
    execute()
