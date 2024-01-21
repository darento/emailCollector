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
from src.parser_factory import get_ticket_parser


def main(yaml_conf: str) -> None:
    """with open(yaml_conf, "r") as stream:
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
        pdf_parser = get_ticket_parser("Mercadona", file_path)
        items, total_price = pdf_parser.parse()
        # print(items)
        print(f"Total price: {total_price:.2f} €")
        print(f"File date: {pdf_parser.file_date}")

    print("Emails downloaded successfully!")"""

    # Ejemplo tienda Granel
    # file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    file_path = "P:/tickets/20240120_granel.jpg"
    jpg_parser = get_ticket_parser("Granel", file_path)
    items = jpg_parser.extract_items()
    total_price = jpg_parser.calculate_total_price()
    print(items)
    print(total_price)


if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]
    main(yaml_conf)
