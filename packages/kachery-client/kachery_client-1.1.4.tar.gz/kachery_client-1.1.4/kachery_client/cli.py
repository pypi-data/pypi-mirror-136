import os
import sys
from typing import Union


import click
import kachery_client as kc
from ._daemon_connection import _get_node_id, _read_client_auth_code


@click.group(help="Kachery peer-to-peer command-line client")
def cli():
    pass

@click.command(help="Get info about the kachery daemon")
def info():
    node_id = _get_node_id()
    try:
        client_auth_code = _read_client_auth_code()
    except:
        client_auth_code = None
    print(f'Node ID: {node_id}')
    if client_auth_code:
        print('You have access to this daemon')
    else:
        print('You do not have access to this daemon')

@click.command(help="Load or download a file.")
@click.argument('uri')
@click.option('--dest', default=None, help='Optional local path of destination file.')
@click.option('--ephemeral-channel', default=None, help='Load direct from channel in ephemeral mode')
def load_file(uri, dest, ephemeral_channel):
    if ephemeral_channel:
        kec = kc.EphemeralClient(channel=ephemeral_channel)
        x = kec.load_file(uri, dest=dest)
    else:
        x = kc.load_file(uri, dest=dest)
    print(x)

@click.command(help="Store a file on the local node (and optionally upload to a channel).")
@click.argument('path')
@click.option('--upload-to-channel', default=None, help='Optionally upload to a kachery channel')
@click.option('--single-chunk', is_flag=True, help='Whether to upload the file all in one chunk')
def store_file(path: str, upload_to_channel: Union[None, str], single_chunk: bool):
    if upload_to_channel is not None:
        x = kc.upload_file(path, channel=upload_to_channel, single_chunk=single_chunk)
    else:
        x = kc.store_file(path)
    print(x)

@click.command(help="Store a link to file locally.")
@click.argument('path')
def link_file(path: str):
    x = kc.link_file(path)
    print(x)

@click.command(help="Download a file and write the content to stdout.")
@click.argument('uri')
@click.option('--start', help='The start byte (optional)', default=None)
@click.option('--end', help='The end byte non-inclusive (optional)', default=None)
@click.option('--ephemeral-channel', default=None, help='Load direct from channel in ephemeral mode')
def cat_file(uri, start, end, ephemeral_channel):
    old_stdout = sys.stdout
    sys.stdout = None

    if ephemeral_channel is not None:
        kk = kc.EphemeralClient(channel=ephemeral_channel)
    else:
        kk = kc

    if start is None and end is None:
        path1 = kk.load_file(uri)
        if not path1:
            raise Exception('Error loading file for cat.')
        sys.stdout = old_stdout
        with open(path1, 'rb') as f:
            while True:
                data = os.read(f.fileno(), 4096)
                if len(data) == 0:
                    break
                os.write(sys.stdout.fileno(), data)
    else:
        assert start is not None and end is not None
        start = int(start)
        end = int(end)
        assert start <= end
        if start == end:
            return
        sys.stdout = old_stdout
        if ephemeral_channel is not None:
            raise Exception('Cannot load byte range in ephemeral mode. Not yet implemented.')
        kk.load_bytes(uri=uri, start=start, end=end, write_to_stdout=True)

@click.command(help="Generate and print a random node ID with an associated private key")
def generate_node_id():
    try:
        import ed25519
    except:
        raise Exception('Unable to import ed25519. Use pip install ed25519.')
    privKey, pubKey = ed25519.create_keypair()
    private_key_hex = privKey.to_ascii(encoding='hex').decode('utf-8')
    public_key_hex = pubKey.to_ascii(encoding='hex').decode('utf-8')
    
    # Let's test it
    msg = b'Message for Ed25519 signing'
    signature = privKey.sign(msg, encoding='hex') # signature (64 bytes)
    try:
        pubKey.verify(signature, msg, encoding='hex')
        # The signature is valid
    except:
        print("Invalid signature!")
    
    print(f'Random node ID: {public_key_hex}')
    print(f'Corresponding private key (hex): {private_key_hex}')
    

@click.command(help="Display kachery_client version and exit.")
def version():
    click.echo(f"This is kachery_client version {kc.__version__}")
    exit()

cli.add_command(cat_file)
cli.add_command(load_file)
cli.add_command(store_file)
cli.add_command(link_file)
cli.add_command(info)
cli.add_command(version)
cli.add_command(generate_node_id)
