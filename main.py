"""Email Collector

Usage:
  main.py YAMLCONF

Arguments:
  YAMLCONF    The path to the .yaml configuration file.

Options:
  -h --help     Show this screen.
"""

import yaml
from docopt import docopt

from src.collector import EmailCollector
from src.ticket_parser import TicketParser


def main(yaml_conf: str) -> None:
    with open(yaml_conf, "r") as stream:
        config = yaml.safe_load(stream)

    with open(config["password"], "r") as f:
        password = f.read()

    email_collector = EmailCollector(config["username"], password, config["imap_url"])
    email_collector.connect()

    email_ids = email_collector.fetch_emails(config["email_sender"])

    for email_id in email_ids:
        file_path = email_collector.download_attachments(
            email_id, config["download_folder"]
        )
        ticket_parser = TicketParser(file_path, "mercadona")
        items, total_price = ticket_parser.parse()

    print("Emails downloaded successfully!")


if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]
    main(yaml_conf)
