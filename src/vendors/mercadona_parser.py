import re
import pypdf

from src.ticket_parser import AbstractTicketParser

ITEM_PATTERN_MERCA = re.compile(r"(\d+)(.*?)(\d+,\d{2})\s*(\d+,\d{2})?")
WEIGHT_PATTERN_MERCA = re.compile(r"(\d+,\d{3}) kg (\d+,\d{2}) €/kg (\d+,\d{2})")


class MercadonaTicketParser(AbstractTicketParser):
    def _parse_ticket(self) -> None:
        # Extract the text from the PDF
        pdf_file_obj = open(self.file_path, "rb")
        pdf_reader = pypdf.PdfReader(pdf_file_obj)
        page_obj = pdf_reader.pages[0]
        text = page_obj.extract_text()
        pdf_file_obj.close()
        return text

    def parse_line(self, lines_iter: iter) -> dict:
        for line in lines_iter:
            match = ITEM_PATTERN_MERCA.match(line.strip())
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
                match = WEIGHT_PATTERN_MERCA.match(next_line.strip())
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
        self.logger.debug(f"Extracted items: {self.items}")
        return self.items
