import re
from typing import Generator
import pytesseract

from src.utils import convert_to_float
from src.ticket_parser import AbstractTicketParser
from src.image_processor import ImageProcessor


class FruteriaTicketParser(AbstractTicketParser):
    def __init__(self, file_path: str, logger_name: str = "FruteriaTicketParser"):
        super().__init__(file_path, logger_name)

    def _clean_ocr_text(self, text: str) -> str:
        # Remove unwanted characters
        text = re.sub(r"[|]", "", text)

        # Replace multiple occurrences of newlines with a single newline
        text = re.sub(r"\n+", "\n", text)

        # Remove spaces after dots and commas (for price and weight parsing)
        text = re.sub(r"(?<=\.) +(?=\d)|(?<=\d) +(?=,)", "", text)

        return text

    def _clean_product_name(self, product: str) -> str:

        return product

    def _parse_ticket(self) -> None:
        # Extract the text from the JPEG
        img_processor = ImageProcessor(img_path=self.file_path)
        img_prepared = img_processor.enhance_image(
            show=True, high_contrast=True, gaussian_blur=True
        )
        text = pytesseract.image_to_string(
            img_prepared, lang="spa", config="--psm 4 --oem 1"
        )
        cleaned_text = self._clean_ocr_text(text)
        self.logger.debug(cleaned_text)
        return cleaned_text

    def parse_line(self, lines_iter: iter) -> Generator[dict, None, None]:
        for line in lines_iter:
            product = " ".join(line.strip().split(" ")[1:])
            print(product)
            # product = self._clean_product_name(product)
            next_line = next(lines_iter)
            next_line_split = next_line.strip().split(" ")
            weight_kg = convert_to_float(next_line_split[0])
            price_per_kg = convert_to_float(next_line_split[1])
            total_price = convert_to_float(next_line_split[2])
            item = {
                "product": product,
                "weight_kg": weight_kg,
                "price_per_kg": price_per_kg,
                "total_price": total_price,
            }
            yield item

    def extract_items(self) -> list[dict]:
        # Find the start and end of the items
        start = self.text.find("Artículo")
        end = self.text.find("Total")
        items_text = self.text[start:end]

        # remove first and last line (Descripción and empty line)
        lines = items_text.split("\n")[1:-1]
        print(lines)
        exit(0)
        self.logger.debug(f"TEXT: \n{self.text}")
        self.logger.debug(f"LINES: \n{lines}")

        # create iterator to check next line
        lines_iter = iter(lines)

        for item in self.parse_line(lines_iter):
            self.items.append(item)
        self.logger.debug(f"Extracted items: {self.items}")
        return self.items
