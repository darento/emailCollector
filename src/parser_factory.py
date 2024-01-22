from src.vendors.mercadona_parser import MercadonaTicketParser
from src.vendors.granel_parser import GranelTicketParser
from src.ticket_parser import AbstractTicketParser


def get_ticket_parser(vendor: str, file_path: str) -> AbstractTicketParser:
    if vendor.upper() == "MERCADONA":
        return MercadonaTicketParser(file_path, logger_name="MercadonaTicketParser")
    elif vendor.upper() == "GRANEL":
        return GranelTicketParser(file_path, logger_name="GranelTicketParser")
    else:
        raise ValueError(f"Unknown vendor: {vendor}")
