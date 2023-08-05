import json

import click
from click_didyoumean import DYMGroup
from huawei_lte_api.Client import Client
from huawei_lte_api.enums.device import ControlModeEnum

from .root import cli
from ..core.connection import HRC_Connection


@cli.group(cls=DYMGroup)
def device():
    """ Device commands """
    pass


@device.command('info')
@click.option(
    '--json', 'as_json', is_flag=True,
    help='Show data in json format.'
)
def device_info(as_json: bool):
    """ Get device information """
    try:
        with HRC_Connection() as conn:
            client = Client(conn)
            device_info_dict = client.device.information()
    except Exception as e:
        msg = 'Can not get device information, reason: "{}"' \
              .format(e)
    else:
        if not as_json:
            msg = ''
            for k, v in device_info_dict.items():
                msg += '• {}: {}\n'.format(k, v)
            msg = msg[:-1]
        else:
            msg = json.dumps(device_info_dict)

    click.echo(msg)


@device.command('reboot')
def device_reboot():
    """ Reboot the router without any confirmation prompts """
    try:
        with HRC_Connection() as conn:
            Client(conn).device.set_control(ControlModeEnum.REBOOT)
    except Exception as e:
        msg = 'Execution failed, reason: "{}"'.format(e)
    else:
        msg = 'Rebooting the device, router will restart in several moments'

    click.echo(msg)
