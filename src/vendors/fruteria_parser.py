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
        product = " ".join(product.strip().split(" "))
        return product

    def _parse_product_info(self, line: str) -> tuple:
        next_line_split = line.strip().split(" ")
        if len(next_line_split) > 4:
            weight_kg = convert_to_float(next_line_split[2])
            price_per_kg = convert_to_float(next_line_split[4])
        else:
            weight_kg = convert_to_float(next_line_split[1])
            price_per_kg = convert_to_float(next_line_split[2])
        total_price = convert_to_float(next_line_split[-1])
        return weight_kg, price_per_kg, total_price

    def _parse_ticket(self) -> None:
        # Extract the text from the JPEG
        img_processor = ImageProcessor(img_path=self.file_path)
        img_prepared = img_processor.enhance_image(
            show=True, high_contrast=True, gaussian_blur=True
        )
        text = pytesseract.image_to_string(
            img_prepared, lang="cat+eng+spa", config="--psm 4 --oem 1"
        )
        cleaned_text = self._clean_ocr_text(text)
        self.logger.debug(cleaned_text)
        return cleaned_text

    def parse_line(self, lines_iter: iter) -> Generator[dict, None, None]:
        for line in lines_iter:
            product = line
            product = self._clean_product_name(product)
            product_info = next(lines_iter)
            weight_kg, price_per_kg, total_price = self._parse_product_info(
                product_info
            )
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

        self.logger.debug(f"TEXT: \n{self.text}")
        self.logger.debug(f"LINES: \n{lines}")

        # create iterator to check next line
        lines_iter = iter(lines)

        for item in self.parse_line(lines_iter):
            self.items.append(item)
        self.logger.debug(f"Extracted items: {self.items}")
        return self.items
