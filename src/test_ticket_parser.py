# test_ticket_parser.py
import pytest
from .ticket_parser import get_ticket_parser


def test_mercadona():
    file_path = "../downloads/20240105 Mercadona 12,50 €.pdf"
    pdf_parser = get_ticket_parser("Mercadona", file_path)
    items = pdf_parser.extract_items()
    total_price = pdf_parser.calculate_total_price()
    # Add assertions here based on what you expect the output to be
    # For example:
    assert len(items) == 5
    assert abs(total_price - 12.50) < 0.01


def test_granel():
    file_path = "P:/tickets/20240113_granel.jpg"
    jpg_parser = get_ticket_parser("Granel", file_path)
    items = jpg_parser.extract_items()
    total_price = jpg_parser.calculate_total_price()
    # Add assertions here based on what you expect the output to be
