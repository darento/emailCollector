from abc import ABC, abstractmethod

from src.logger import get_logger


class AbstractTicketParser(ABC):
    def __init__(self, file_path: str, logger_name: str) -> None:
        # Create a logger at the class level
        self.logger = get_logger(logger_name)

        self.file_path = file_path
        self.items = []
        self.text = self._parse_ticket()
        self.total_price = 0
        self.file_date = self._parse_date_from_file_path()

    def _parse_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def get_date(self) -> str:
        return self.file_date

    def get_text(self) -> str:
        return self.text

    def calculate_total_price(self) -> float:
        self.total_price = sum(item["total_price"] for item in self.items)
        if self.total_price == 0:
            self.logger.warning("Total price is 0. Check the parser!")
        return self.total_price

    @abstractmethod
    def _parse_ticket(self) -> None:
        pass

    @abstractmethod
    def extract_items(self) -> None:
        pass


if __name__ == "__main__":
    pass
