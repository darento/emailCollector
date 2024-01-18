import os
import pypdf
import re
import logging
from abc import ABC, abstractmethod
import pytesseract


ITEM_PATTERN = re.compile(r"(\d+)(.*?)(\d+,\d{2})\s*(\d+,\d{2})?")
WEIGHT_PATTERN = re.compile(r"(\d+,\d{3}) kg (\d+,\d{2}) €/kg (\d+,\d{2})")


# TODO: Add a class for the OCR parser
# TODO: Add a class for the PDF parser


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
        self.total_price = 0
        self.file_date = self._extract_date_from_file_path()

    def open_pdf(self) -> None:
        self.pdf_file_obj = open(self.file_path, "rb")
        self.pdf_reader = pypdf.PdfReader(self.pdf_file_obj)
        self.page_obj = self.pdf_reader.pages[0]
        self.text = self.page_obj.extract_text()

    def close_pdf(self) -> None:
        self.pdf_file_obj.close()

    def extract_lines(self) -> None:
        self.lines = self.text.split("\n")

    def parse(self) -> tuple:
        self.open_pdf()
        self.extract_lines()
        self.extract_items()
        self.calculate_total_price()
        self.close_pdf()
        return self.items, self.total_price

    def get_date(self) -> str:
        return self.file_date

    @abstractmethod
    def _extract_date_from_file_path(self) -> str:
        pass

    @abstractmethod
    def extract_items(self) -> None:
        pass

    @abstractmethod
    def calculate_total_price(self) -> None:
        pass


class MercadonaTicketParser(AbstractTicketParser):
    def _extract_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def parse_line(self, lines_iter):
        for line in lines_iter:
            match = ITEM_PATTERN.match(line.strip())
            if match:
                self.logger.debug(f"Match: {match.groups()}")
                item = {
                    "units": int(match.group(1)),
                    "product": match.group(2).strip(),
                    "price_per_unit": float(match.group(3).replace(",", "."))
                    if match.group(3)
                    else None,
                    "total_price": float(match.group(4).replace(",", "."))
                    if match.group(4)
                    else float(match.group(3).replace(",", ".")),
                }
                yield item
            else:
                # If the current line doesn't match, check the next line
                next_line = next(lines_iter)
                match = WEIGHT_PATTERN.match(next_line.strip())
                if match:
                    self.logger.debug(f"No match: {match.groups()}")
                    item = {
                        "product": line[1:].strip(),
                        "weight_kg": float(match.group(1).replace(",", ".")),
                        "price_per_kg": float(match.group(2).replace(",", ".")),
                        "total_price": float(match.group(3).replace(",", ".")),
                    }
                    yield item

    def extract_items(self):
        # Find the start and end of the items
        start = self.text.find("Descripció")
        end = self.text.find("TOTAL")
        items_text = self.text[start:end]

        # remove first and last line (Descripción and empty line)
        lines = items_text.split("\n")[1:-1]

        self.logger.debug(f"TEXT: \n{self.text}")
        self.logger.debug(f"LINES: \n{lines}")

        # create iterator to check next line
        lines_iter = iter(lines)
        for item in self.parse_line(lines_iter):
            self.items.append(item)

    def calculate_total_price(self):
        self.total_price = sum(item["total_price"] for item in self.items)
        if self.total_price == 0:
            self.logger.warning("Total price is 0. Check the parser!")


class GranelTicketParser(AbstractTicketParser):
    def _extract_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def extract_items(self):
        print(self.text)

    def calculate_total_price(self):
        # Implement OtherVendor-specific logic here
        pass


# factory function
def get_ticket_parser(vendor, file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")

    if vendor == "Mercadona":
        return MercadonaTicketParser(file_path)
    elif vendor == "Granel":
        return GranelTicketParser(file_path)
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")


if __name__ == "__main__":
    # Ejemplo tienda Granel
    # file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    file_path = "P:/tickets/20240113_fruteria.pdf"
    print(file_path)
    pdf_parser = get_ticket_parser("Granel", file_path)
    items, total_price = pdf_parser.parse()
