"""
Layerd. Download Lambda Layers.
"""

import os
import sys


__author__ = 'ronnathaniel'

__usage__ = '' + \
'Usage:     \n' + \
'\tlayerd <ARN>  \n' + \
'\t\t@arg ARN being an Amazon Resource Name of a Public AWS Lambda Layer. \n' + \
'\t\t@example arn:aws:lambda:REGION:ACC:layer:NAME:VERSION. \n' + \
'\tFeature Flags (By Environment): \n' + \
'\t\tLAYERD_REGION=TRUE for REGION in DIR. \n' + \
'\t\t\tDefault=FALSE \n' + \
'\t\tLAYERD_PARENT_DIR=<PATH> \n' + \
'\t\t\tDefault=. \n'

__region__ = os.environ.get('AWS_REGION')

_flag_add_region = str(True).lower() in os.environ.get('LAYERD_REGION', '').lower()
_flag_parent_dir = os.environ.get('LAYERD_PARENT_DIR', '.')


def _stdout_del_last_row(
    width: int = os.get_terminal_size(0)[0],
):
    print(('\r') + (' ' * int(width)) + ('\r') , end='\r', flush=True)

def _progress_bar(
    current_iter: int,
    total_iter: int,
    message: str = None,
    width: int = os.get_terminal_size(0)[0] // 2,
):
    pc = int(100 * current_iter / total_iter)
    filled = int(width * current_iter / total_iter)
    bar = ('█' * filled) + ('-' * (width - filled))
    print(f'\r{message or "Pulling"}: |{bar}| {pc}% ', end='')
    if current_iter == total_iter:
        _stdout_del_last_row()
