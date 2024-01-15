import PyPDF2
import re


class TicketParser:
    def __init__(self, file_path: str, file_format: str) -> None:
        self.file_path = file_path
        self.file_format = file_format

    def open_pdf(self):
        self.pdf_file_obj = open(self.file_path, "rb")
        self.pdf_reader = PyPDF2.PdfReader(self.pdf_file_obj)
        self.page_obj = self.pdf_reader.pages[0]
        self.text = self.page_obj.extract_text()

    def close_pdf(self):
        self.pdf_file_obj.close()

    def extract_lines(self):
        self.lines = self.text.split("\n")

    def extract_items_mercadona(self):
        self.items = []
        start = self.text.find("Descripción")
        end = self.text.find("TOTAL")
        items_text = self.text[start:end]
        lines = items_text.split("\n")[1:]
        for line in lines:
            print(line)
            # TODO: split the product name from the price and price per unit
            # TODO: separte the num of units from the product name
            item = {
                "product": item_match.group(1),
                "units": int(item_match.group(2)),
                "price_per_unit": float(item_match.group(3).replace(",", ".")),
            }
            self.items.append(item)
        print(self.items)
        exit(0)

    def calculate_total_price(self):
        self.total_price = sum(
            item["units"] * item["price_per_unit"] for item in self.items
        )

    def parse(self):
        self.open_pdf()
        self.extract_lines()
        if self.file_format == "mercadona":
            self.extract_items_mercadona()
        self.calculate_total_price()
        self.close_pdf()
        return self.items, self.total_price
