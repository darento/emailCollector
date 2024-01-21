from src.mercadona_parser import MercadonaTicketParser
from src.granel_parser import GranelTicketParser


def get_ticket_parser(vendor, file_path):
    if vendor.upper() == "MERCADONA":
        return MercadonaTicketParser(file_path)
    elif vendor.upper() == "GRANEL":
        return GranelTicketParser(file_path)
    else:
        raise ValueError(f"Unknown vendor: {vendor}")
