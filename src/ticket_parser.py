import os
import numpy as np
import pypdf
import re
import logging
from abc import ABC, abstractmethod
import pytesseract
import cv2


ITEM_PATTERN = re.compile(r"(\d+)(.*?)(\d+,\d{2})\s*(\d+,\d{2})?")
WEIGHT_PATTERN = re.compile(r"(\d+,\d{3}) kg (\d+,\d{2}) €/kg (\d+,\d{2})")


# TODO: Implement extract_items() and calculate_total_price() methods for GranelTicketParser


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
        self.text = self._parse_text()
        self.total_price = 0
        self.file_date = self._parse_date_from_file_path()

    def get_date(self) -> str:
        return self.file_date

    def get_text(self) -> str:
        return self.text

    @abstractmethod
    def _parse_text(self) -> None:
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


class MercadonaTicketParser(AbstractTicketParser):
    def _parse_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def _parse_text(self) -> None:
        # Extract the text from the PDF
        pdf_file_obj = open(self.file_path, "rb")
        pdf_reader = pypdf.PdfReader(pdf_file_obj)
        page_obj = pdf_reader.pages[0]
        text = page_obj.extract_text()
        pdf_file_obj.close()
        return text

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

    def extract_items(self) -> list:
        # Find the start and end of the items
        print("Extracting items...")
        print(self.text)
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
        return self.items

    def calculate_total_price(self) -> float:
        self.total_price = sum(item["total_price"] for item in self.items)
        if self.total_price == 0:
            self.logger.warning("Total price is 0. Check the parser!")
        return self.total_price


class GranelTicketParser(AbstractTicketParser):
    def _parse_date_from_file_path(self) -> str:
        # Extract the date from the file name
        # The date is the first 8 characters of the file name
        # The format is YYYYMMDD
        return self.file_path.split("/")[-1][:8]

    def _parse_text(self) -> None:
        # Extract the text from the JPEG
        img_prepared = self._prepare_image(True)
        text = pytesseract.image_to_string(
            img_prepared, lang="cat+eng+spa", config="--psm 6 --oem 3"
        )
        print(text)
        exit(0)
        return text

    def _prepare_image(self, show: bool = False) -> np.ndarray:
        # Load the image from file
        img = cv2.imread(self.file_path)

        # Convert the image to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Show the thresholded image
        if show:
            self._show_image(thresh)
        return thresh

    def _show_image(self, img):
        # Display the thresholded image
        # Create a resizable window
        cv2.namedWindow("Thresholded Image", cv2.WINDOW_NORMAL)

        # Resize the window to 800x600
        cv2.resizeWindow("Thresholded Image", 800, 600)

        # Display the thresholded image
        cv2.imshow("Thresholded Image", img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

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
    # Ejemplo tienda Mercadona
    """file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    pdf_parser = get_ticket_parser("Mercadona", file_path)
    items = pdf_parser.extract_items()
    total_price = pdf_parser.calculate_total_price()"""

    # Ejemplo tienda Granel
    # file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    file_path = "P:/tickets/20240113_granel.jpg"
    jpg_parser = get_ticket_parser("Granel", file_path)
    print(jpg_parser.get_text())
    items = jpg_parser.extract_items()
    total_price = jpg_parser.calculate_total_price()
