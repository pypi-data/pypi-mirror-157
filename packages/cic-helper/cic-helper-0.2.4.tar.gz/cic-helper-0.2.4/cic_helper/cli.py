import logging
import pathlib
import subprocess
import sys

import click

from cic_helper.constants import (
    DEFAULT_CHAIN_SPEC,
    DEFAULT_GAS_LIMIT,
    DEFAULT_RPC_PROVIDER,
)
from cic_helper.Person import load_people_from_csv, save_people_to_csv

log = logging.getLogger(__name__)

log_format = "%(message)s"


def set_log_level(level: int = 1):
    # ERROR, WARN, INFO, DEBUG
    if level == 1:
        logging.basicConfig(format=log_format, level=logging.INFO)
    else:
        logging.basicConfig(format=log_format, level=logging.DEBUG)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("-v", "--verbose", count=True, help="Verbosity Level (-v,-vv)")
@click.option(
    "--fee-limit",
    nargs=1,
    type=str,
    default="800000",
    show_default=True,
    help="Fee limit for each tx",
)
@click.option("-t", "--token", type=str, nargs=1, default=False, help="Token Address")
@click.option(
    "-p",
    "--rpc_provider",
    type=str,
    nargs=1,
    default=DEFAULT_RPC_PROVIDER,
    show_default=True,
    help="RPC Provider",
)
@click.option(
    "-i",
    "--chain_spec",
    type=str,
    nargs=1,
    default=DEFAULT_CHAIN_SPEC,
    show_default=True,
    help="Chain Spec",
)
def get_balances(filename, verbose, fee_limit, token, rpc_provider, chain_spec):
    set_log_level(verbose)
    people = load_people_from_csv(filename)
    for person in people:
        err = person.verify(user_address=True)
        if err:
            raise Exception(err)
    for person in people:
        person.get_balance(token, chain_spec, rpc_provider, fee_limit)
    save_people_to_csv(filename, people)


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("-v", "--verbose", count=True, help="Verbosity Level (-v,-vv)")
def verify_amount(filename, verbose):
    set_log_level(verbose)
    people = load_people_from_csv(filename)
    for person in people:
        err = person.verify(user_address=True, balance=True, contract_address=True)
        if err:
            log.error(err)


@cli.command()
@click.option("-c", "--config", type=str, help="Path to Kitabu Config Folder")
def run(config):
    base = pathlib.Path(__file__).parent.resolve()
    kitabu_path = config or base.joinpath("kitabu")
    result = subprocess.run(["bash", "run.sh"], stdout=subprocess.PIPE, cwd=kitabu_path)
    log.info(result)


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("-v", "--verbose", count=True, help="Verbosity Level (-v,-vv)")
def get_addresses(filename, verbose):
    set_log_level(verbose)
    people = load_people_from_csv(filename)
    log.info(f"Fetching Address for {len(people)} People")
    for idx, person in enumerate(people):
        log.info(f"[{idx}/{len(people)}] Fetching address for: {person.phone_number}")
        person.get_address()
        if person.user_address is None:
            log.error(f"Failed to get address for {person.phone_number}, so skipping")

    log.info(f"Saving to {filename}")
    save_people_to_csv(filename, people)
    log.info(f"Saved to {filename}")


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("contract_address", type=str)
@click.option(
    "--fee-limit",
    nargs=1,
    type=str,
    default=str(DEFAULT_GAS_LIMIT),
    show_default=True,
    help="Fee limit for each tx",
)
@click.option("-v", "--verbose", count=True, help="Verbosity Level (-v,-vv)")
@click.option(
    "-p",
    "--rpc_provider",
    type=str,
    nargs=1,
    show_default=True,
    default=DEFAULT_RPC_PROVIDER,
    help="RPC Provider",
)
@click.option(
    "-i",
    "--chain_spec",
    type=str,
    nargs=1,
    show_default=True,
    default=DEFAULT_CHAIN_SPEC,
    help="Chain Spec",
)
@click.option(
    "-y",
    "--signer",
    type=str,
    required=True,
    help='Signer Keyfile Location (e.g "/home/sarafu//wor-deployer-wallet-keyfile")',
)
def send(
    filename, contract_address, fee_limit, rpc_provider, chain_spec, signer, verbose
):
    set_log_level(verbose)
    people = load_people_from_csv(filename)
    errors = []
    for person in people:
        person.contract_address = contract_address
        err = person.verify(user_address=True, contract_address=True)
        if err:
            errors.append(err)
    if len(errors) > 0:
        log.error(errors)
        sys.exit(1)

    save_people_to_csv(filename=filename, people=people)
    for person in people:
        person.send(
            contract_address, signer, chain_spec, rpc_provider, fee_limit=fee_limit
        )


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    cli()
