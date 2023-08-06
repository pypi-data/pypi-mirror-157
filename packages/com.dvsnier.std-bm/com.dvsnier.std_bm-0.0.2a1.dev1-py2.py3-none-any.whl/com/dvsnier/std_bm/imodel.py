# -*- coding:utf-8 -*-

from com.dvsnier.config.journal.common_config import config
from com.dvsnier.config.journal.compat_logging import logging


class IModel(object):
    '''the imodel class'''

    DEPRECATED_MAJOR_MASTER = 'master'

    MAJOR_DEPLOY = 'deploy'
    MAJOR_MAIN = 'main'
    MAJOR_RELEASE = 'release'

    MINOR_DEVELOPER = 'developer'
    MINOR_HOTFIX = 'hotfix'

    MICRO_FEATURE = 'feature'
    MICRO_KERNEL = 'kernel'

    def __init__(self):
        super(IModel, self).__init__()
        kwargs = {'output_dir_name': 'log', 'file_name': 'log', 'level': logging.INFO}
        config(kwargs)
