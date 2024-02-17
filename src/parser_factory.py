from src.vendors.fruteria_parser import FruteriaTicketParser
from src.vendors.mercadona_parser import MercadonaTicketParser
from src.vendors.granel_parser import GranelTicketParser
from src.ticket_parser import AbstractTicketParser


def get_ticket_parser(vendor: str, file_path: str) -> AbstractTicketParser:
    if vendor.upper() == "MERCADONA":
        return MercadonaTicketParser(file_path, logger_name="MercadonaTicketParser")
    elif vendor.upper() == "GRANEL":
        return GranelTicketParser(file_path, logger_name="GranelTicketParser")
    elif vendor.upper() == "FRUTERIA":
        return FruteriaTicketParser(file_path, logger_name="FruteriaTicketParser")
    else:
        raise ValueError(f"Unknown vendor: {vendor}")
