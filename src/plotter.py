import matplotlib.pyplot as plt


def generate_charts(data):
    plt.figure(figsize=(10, 5))
    plt.bar(data.keys(), data.values())
    plt.show()
