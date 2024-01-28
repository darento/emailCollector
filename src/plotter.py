import matplotlib.pyplot as plt
import numpy as np


def set_plot_params(title: str, x_label: str, y_label: str):
    plt.title(title, fontsize=16)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.grid(axis="x")


def plot_expenses_per_month(expenses_per_month: dict, title_vendor: str = None) -> None:
    # Sort the dictionary by month
    expenses_per_month = dict(sorted(expenses_per_month.items()))

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(
        range(len(expenses_per_month)),
        list(expenses_per_month.values()),
        align="center",
        color="skyblue",
    )
    plt.xticks(range(len(expenses_per_month)), list(expenses_per_month.keys()))
    set_plot_params(f"Expenses per Month {title_vendor}", "Month", "Expenses (€)")


def plot_expenses_per_item(expenses_per_item: dict, title_vendor: str = None) -> None:
    # Sort the dictionary by item
    expenses_per_item = dict(sorted(expenses_per_item.items()))

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.barh(
        range(len(expenses_per_item)),
        list(expenses_per_item.values()),
        align="center",
        color="skyblue",
    )
    plt.yticks(
        range(len(expenses_per_item)),
        list(expenses_per_item.keys()),
    )
    set_plot_params(f"Expenses per Month {title_vendor}", "Expenses (€)", "Item")


def plot_show():
    plt.show()
