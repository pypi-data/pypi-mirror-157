import csv
import logging
import re
import shutil
import subprocess
from tempfile import NamedTemporaryFile
from typing import List

from chainlib.eth.address import is_address

from cic_helper.constants import CSV_HEADER, DEFAULT_GAS_LIMIT

log = logging.getLogger(__name__)


class Person:
    def __init__(
        self,
        phone_number: str,
        user_address: str,
        contract_address: str,
        current_balance: str,
        send_amount: str,
        timestamp: str,
    ):
        self.phone_number = (
            phone_number if phone_number.startswith("+") else f"+{phone_number}"
        )
        self.user_address = user_address
        self.contract_address = contract_address
        self.current_balance = current_balance
        self.send_amount = int(send_amount)
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.phone_number} {self.user_address} {self.send_amount}"

    def get_address(self, failHard=False):
        result = subprocess.run(
            ["clicada", "u", self.phone_number], capture_output=True, text=True
        )
        output = result.stdout
        regex = re.search("Network address: (0x[a-fA-F0-9]{40})", output)
        try:
            self.user_address = regex.group(1)
        except Exception as e:
            log.debug(e)
            log.error(f"Failed to get address for {self.phone_number}")
            pass
        finally:
            if self.user_address is None and failHard:
                raise Exception(
                    f"Failed to get address for {self.phone_number}\n STDOUT: {result.stdout}\n STDERR:{result.stderr}"
                )
        return self.user_address

    def get_balance(
        self,
        contract_address: str,
        chain_spec: str,
        rpc_provider: str,
        fee_limit=DEFAULT_GAS_LIMIT,
    ):
        if contract_address:
            self.contract_address = contract_address
        cmd = [
            "erc20-balance",
            "--fee-limit",
            str(fee_limit),
            "-p",
            rpc_provider,
            "-i",
            chain_spec,
            "-u",
            "-e",
            self.contract_address,
            self.user_address,
        ]
        log.debug(">" + " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            self.current_balance = str(float(result.stdout.strip()))
            log.info(f"{self.phone_number} - {self.current_balance}")
        except Exception as e:
            self.current_balance = ""
            log.debug(e)
            log.error(
                f"Failed to get balance for: {self.phone_number} ({self.user_address})"
            )
            pass
        return self.current_balance

    def verify(self, user_address=False, balance=False, contract_address=False):
        errors = []
        if user_address:
            if not is_address(self.user_address):
                errors.append("  - No Valid User Address")
        if contract_address:
            if not is_address(self.contract_address):
                errors.append("  - No Valid Token Address")
        if balance and not self.has_corrent_amount():
            errors.append(
                f"  - Incorrect balance. Expected Current Balance {self.current_balance} > {self.send_amount} - 1"
            )
        if len(errors) > 0:
            errors.insert(0, f"{self.phone_number}")
            return "\n".join(errors)
        else:
            return None

    def send(
        self,
        contract_address,
        signer_keyfile,
        chain_spec: str,
        rpc_provider: str,
        fee_limit=DEFAULT_GAS_LIMIT,
    ):
        self.contract_address = contract_address
        log.info(
            f"  Sending {self.send_amount} to {self.phone_number} ({self.user_address})"
        )
        cmd = [
            "erc20-transfer",
            "-p",
            rpc_provider,
            "-i",
            chain_spec,
            "-u",
            "-e",
            contract_address,
            "--fee-limit",
            str(fee_limit),
            "-y",
            signer_keyfile,
            "-a",
            self.user_address,
            str(self.send_amount),
            "-s",
            "-w",
        ]
        log.debug("> " + " ".join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            log.info("Stdout: " + str(result.stdout))
            log.info("Error: " + str(result.stderr))
        except Exception as e:
            log.error(e)

    def to_row(self) -> List[str]:
        return [
            self.phone_number,
            self.user_address,
            self.contract_address,
            self.current_balance,
            str(self.send_amount),
            self.timestamp,
        ]


def person_from_row(row: List[str]) -> Person:
    return Person(*row)


def load_people_from_csv(filename: str) -> List[Person]:
    people = []
    with open(filename) as file:
        csvreader = csv.reader(file, delimiter=",")
        for idx, row in enumerate(csvreader):
            if idx == 0:
                if row != CSV_HEADER:
                    raise Exception(
                        f'Seems you are using the wrong csv format. Expected the header to be: \n\t {", ".join(CSV_HEADER)}'
                    )
                continue
            people.append(person_from_row(row))
    return people


def save_people_to_csv(filename: str, people: List[Person]):
    with NamedTemporaryFile("w+t", newline="", delete=False) as tempfile:
        csvWriter = csv.writer(tempfile, delimiter=",", quotechar='"')
        csvWriter.writerow(CSV_HEADER)
        csvWriter.writerows([person.to_row() for person in people])
        shutil.move(tempfile.name, filename)
