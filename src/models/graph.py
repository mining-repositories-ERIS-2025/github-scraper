import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.frequency_dict = {}

    def add_to_frequency_dict(self, key: str):
        if key in self.frequency_dict:
            self.frequency_dict[key] += 1
        else:
            self.frequency_dict[key] = 1

    def plot_histogram(self, data_dict: dict = None, title='Histogram of Data'):
        # Use self.frequency_dict if no data_dict is supplied
        if data_dict is None:
            data_dict = self.frequency_dict

        processed_data = {str(k) if k is None else k: v for k, v in data_dict.items()}
        sorted_data = dict(sorted(processed_data.items(), key=lambda item: item[1], reverse=True))

        plt.figure(figsize=(12, 5))
        bars = plt.bar(sorted_data.keys(), sorted_data.values())
        plt.xlabel('Category')
        plt.ylabel('Frequency')
        plt.title(title)
        plt.xticks(rotation=90)  # Corrected rotation to 90 for vertical labels
        plt.tight_layout()

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{int(height)}', ha='center', va='bottom')

        plt.show()