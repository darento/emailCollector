import logging

from abc import ABC, abstractmethod


class AbstractTicketParser(ABC):
    # Create a logger at the class level
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    # Check if the logger has handlers
    if not logger.handlers:
        # Create a console handler with level DEBUG
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.items = []
        self.text = self._parse_ticket()
        self.total_price = 0
        self.file_date = self._parse_date_from_file_path()

    def get_date(self) -> str:
        return self.file_date

    def get_text(self) -> str:
        return self.text

    @abstractmethod
    def _parse_ticket(self) -> None:
        pass

    @abstractmethod
    def _parse_date_from_file_path(self) -> str:
        pass

    @abstractmethod
    def extract_items(self) -> None:
        pass

    @abstractmethod
    def calculate_total_price(self) -> None:
        pass


if __name__ == "__main__":
    # Ejemplo tienda Mercadona
    """file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    pdf_parser = get_ticket_parser("Mercadona", file_path)
    items = pdf_parser.extract_items()
    total_price = pdf_parser.calculate_total_price()"""

    # Ejemplo tienda Granel
    # file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    file_path = "P:/tickets/20240120_granel.jpg"
    jpg_parser = get_ticket_parser("Granel", file_path)
    items = jpg_parser.extract_items()
    total_price = jpg_parser.calculate_total_price()
    print(items)
    print(total_price)
