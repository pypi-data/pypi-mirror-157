import logging
import os
from datetime import datetime
from pathlib import Path

import dotenv

from oeleo.connectors import SSHConnector, register_password
from oeleo.utils import logger
from oeleo.workers import simple_worker, ssh_worker

log = logger()


def main():
    log.setLevel(logging.INFO)
    log.info(f"Starting oeleo!")
    dotenv.load_dotenv()
    filter_extension = os.environ["OELEO_FILTER_EXTENSION"]
    worker = simple_worker()
    worker.connect_to_db()
    worker.filter_local(filter_extension)
    worker.check(filter_extension)
    worker.run()


def example_check_with_ssh_connection():
    print(" example_check_with_ssh_connection ".center(80, "-"))
    log.setLevel(logging.INFO)
    log.info(f"Starting oeleo!")
    dotenv.load_dotenv()

    external_dir = "/home/jepe@ad.ife.no/Temp"
    filter_extension = "res"

    register_password(os.environ["OELEO_PASSWORD"])
    connector = SSHConnector(directory=external_dir)
    connector.connect()

    worker = ssh_worker(
        db_name=r"test_databases\test_ssh_to_odin.db",
        base_directory_from=Path(r"C:\scripting\processing_cellpy\raw"),
        connector=connector,
    )
    worker.connect_to_db()
    try:
        worker.check(filter_extension, update_db=True)
        worker.filter_local(filter_extension)
        worker.run()
    finally:
        connector.close()


def example_check_first_then_run():
    print(" example_check_first_then_run ".center(80, "-"))
    not_before = datetime(year=2021, month=3, day=1, hour=1, minute=0, second=0)
    not_after = datetime(year=2022, month=7, day=1, hour=1, minute=0, second=0)
    print("Starting...")

    my_filters = [
        ("not_before", not_before),
        ("not_after", not_after),
    ]

    log.setLevel(logging.INFO)
    log.info(f"Starting oeleo!")
    dotenv.load_dotenv()
    filter_extension = "res"
    worker = simple_worker(
        db_name=r"test_databases\another.db",
        base_directory_from=Path(r"C:\scripting\processing_cellpy\raw"),
        base_directory_to=Path(r"C:\scripting\trash"),
    )
    worker.connect_to_db()
    worker.filter_local(filter_extension)
    worker.check(filter_extension, additional_filters=my_filters)
    run_oeleo = input("\n Continue ([y]/n)? ") or "y"
    if run_oeleo.lower() in ["y", "yes"]:
        worker.run()


if __name__ == "__main__":
    main()
    example_check_first_then_run()
    example_check_with_ssh_connection()
