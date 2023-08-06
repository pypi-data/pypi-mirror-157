"""
[D]ownload [P]ublic [L]ayers
"""

import os
import sys
import boto3
import botocore
from io import BytesIO
import requests
from threading import Timer
import zipfile


from layerd import (
    _flag_add_region,
    _flag_parent_dir,
    _progress_bar,
    _stdout_del_last_row,
    __usage__,
)

def run():
    args = [*sys.argv]
    args.pop(0)
    if (not args) or ('help' in args[0].lower()):
        print(__usage__)
        exit(1)

    arn = args[0]
    names = arn.split(':')
    if not (6 <= len(names) <= 8):
        print(__usage__)
        print('Error: <ARN> not valid. Recieved ' + arn)
        exit(1)
    # for i, e in enumerate(names):
    #     print(i, e)
    region = names[3]

    layer_q = names[5]
    # print('layer_q', layer_q)
    layer_name = names[6]

    version = int(names[-1])

    names_vless = [*names]
    names_vless.pop(-1)
    arn_vless = ':'.join(names_vless)

    print('Layer:\t', layer_name)
    print('Region:\t', region)
    print('V:\t', version)

    client_lambda = boto3.client('lambda', region_name=region)
    _progress_bar(1, 10, message='Pulling')

    try:
        layer_version_d = client_lambda.get_layer_version(LayerName=arn_vless, VersionNumber=version)
    except botocore.exceptions.ClientError as err:
        _stdout_del_last_row()
        print('\nError:', err)
        return

    _progress_bar(3, 10, message='Addressing')
    layer_address = layer_version_d.get('Content', {}).get('Location', '')
    res = requests.get(layer_address, stream=True)
    _progress_bar(6, 10, message='Unzipping')
    zip = zipfile.ZipFile(BytesIO(res.content))
    _progress_bar(7.2, 10)
    layer_dir = os.path.join(
        _flag_parent_dir,
        f'{layer_q}-{layer_name}-{version}'
    )
    if _flag_add_region:
        layer_dir += f'-{region}'
    _progress_bar(8.8, 10, message='Extracting')
    zip.extractall(layer_dir)
    _progress_bar(10, 10, message='Done')
    print()
    print(f'Created: {layer_dir}/')

if __name__ == '__main__':
    run()
