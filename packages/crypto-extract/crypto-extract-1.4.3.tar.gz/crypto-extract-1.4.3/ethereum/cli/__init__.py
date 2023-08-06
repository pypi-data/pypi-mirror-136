import click

from ethereum.cli.extract_blocks_and_transactions import extract_blocks_and_transactions
from ethereum.cli.extract_traces import extract_traces
from ethereum.cli.extract_verified_contract import extract_verified_contract
from ethereum.logging_util import logging_basic_config

logging_basic_config()


@click.group()
@click.pass_context
def cli(ctx):
    pass


cli.add_command(extract_blocks_and_transactions, 'extract_blocks_and_transactions')
cli.add_command(extract_traces, 'extract_traces')
cli.add_command(extract_verified_contract, 'extract_verified_contract')
