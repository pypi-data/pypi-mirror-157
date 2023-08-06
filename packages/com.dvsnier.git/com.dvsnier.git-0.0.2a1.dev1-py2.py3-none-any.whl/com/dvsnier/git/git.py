# -*- coding:utf-8 -*-

import os

from com.dvsnier.config.journal.compat_logging import logging


class Git(object):
    'the git class'

    def __init__(self):
        super(Git, self).__init__()

    def config(self, output_dir_name='git', file_name='vcs'):
        '''
            the configure logging modules
            note:
                1. the currently, only one process instance log object is supported.
                2. the following consideration is to support multi process and multi instance log objects
        '''
        # kwargs = {'output_dir_name': output_dir_name, 'file_name': file_name}
        # logging_conf(kwargs)
        logging.set_kw_output_dir_name(os.path.join(os.getcwd(), 'out',
                                                    output_dir_name)).set_kw_file_name(file_name).set_kw_level(
                                                        logging.DEBUG).set_logging_name('dvs-git').build()
