"""Email Collector

Usage:
  main.py YAMLCONF

Arguments:
  YAMLCONF    The path to the .yaml configuration file.

Options:
  -h --help     Show this screen.
"""

from collections import defaultdict
import os
import yaml
from docopt import docopt

from src.collector import EmailCollector
from src.parser_factory import get_ticket_parser
from src.plotter import plot_expenses_per_month, plot_expenses_per_item, plot_show
from src.utils import extract_expenses_per_month, extract_expenses_per_item


def extract_items_from_emails(email_ids, email_collector, download_folder):
    all_items = []
    for email_id in email_ids:
        file_path = email_collector.download_attachments(email_id, download_folder)
        pdf_parser = get_ticket_parser("Mercadona", file_path)
        if pdf_parser is not None:
            items = pdf_parser.extract_items()
            date = pdf_parser.get_date()
            all_items.append((items, date))
    return all_items


def extract_items_from_tickets(tickets_dir: str, vendor: str) -> list:
    # Get a list of all files in the directory
    all_files = os.listdir(tickets_dir)

    # List to store all the items
    all_items = []

    # Loop over each file
    for file_name in all_files:
        # If the file is a .jpg file and the vendor name is in the file name
        if file_name.lower().endswith(".jpg") and vendor.lower() in file_name.lower():
            # Full path to the file
            file_path = os.path.join(tickets_dir, file_name)
            print(f"Processing {file_path}...")

            # Parse the file with the vendor parser
            jpg_parser = get_ticket_parser(vendor, file_path)
            items = jpg_parser.extract_items()
            date = jpg_parser.get_date()

            # Add the items to the all_items list
            all_items.append((items, date))

    return all_items


def extract_total_per_month(dicts):
    result = defaultdict(float)
    for d in dicts:
        for key, value in d.items():
            result[key] += value
    return result


def main(yaml_conf: str) -> None:
    with open(yaml_conf, "r") as stream:
        config = yaml.safe_load(stream)
    with open(config["password"], "r") as f:
        password = f.read()

    print(f"Connecting to {config['imap_url']}...")
    print(f"Fetching emails from {config['email_sender']}...")
    print(f"and downloading attachments to {config['download_folder']}...")
    email_collector = EmailCollector(config["username"], password, config["imap_url"])
    email_collector.connect()

    email_ids = email_collector.fetch_emails(config["email_sender"])

    all_items_mercadona = extract_items_from_emails(
        email_ids, email_collector, config["download_folder"]
    )

    # Dictionary to store the total expenses per month
    expenses_per_month_mercadona = extract_expenses_per_month(all_items_mercadona)
    expenses_per_item = extract_expenses_per_item(all_items_mercadona)

    # Plot the expenses per month and per item
    plot_expenses_per_month(expenses_per_month_mercadona, title_vendor="Mercadona")
    plot_expenses_per_item(expenses_per_item, title_vendor="Mercadona")
    plot_show()

    print(f"Fetching tickets from {config['tickets_dir']}...")
    # Directory containing the tickets
    tickets_dir = config["tickets_dir"]

    # List to store all the items for Granel vendor
    all_items_granel = extract_items_from_tickets(tickets_dir, "Granel")

    # Dictionary to store the total expenses per month and per item
    expenses_per_month_granel = extract_expenses_per_month(all_items_granel)
    expenses_per_item = extract_expenses_per_item(all_items_granel)

    # Plot the expenses per month and per item
    plot_expenses_per_month(expenses_per_month_granel, title_vendor="Granel")
    plot_expenses_per_item(expenses_per_item, title_vendor="Granel")
    plot_show()

    # List to store all the items for Fruteria vendor
    all_items_fruteria = extract_items_from_tickets(tickets_dir, "Fruteria")

    # Dictionary to store the total expenses per month and per item
    expenses_per_month_fruteria = extract_expenses_per_month(all_items_fruteria)
    expenses_per_item = extract_expenses_per_item(all_items_fruteria)

    # Plot the expenses per month and per item
    plot_expenses_per_month(expenses_per_month_fruteria, title_vendor="Fruteria")
    plot_expenses_per_item(expenses_per_item, title_vendor="Fruteria")
    plot_show()

    # Plot the expenses per month and per item for all vendors
    total_expenses_per_month = extract_total_per_month(
        [
            expenses_per_month_mercadona,
            expenses_per_month_granel,
            expenses_per_month_fruteria,
        ]
    )
    plot_expenses_per_month(total_expenses_per_month, title_vendor="All Vendors")
    plot_show()


if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]
    main(yaml_conf)
