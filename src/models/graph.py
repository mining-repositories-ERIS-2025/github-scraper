import matplotlib.pyplot as plt
import numpy as np

class BarGraph:
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

        plt.savefig(f'./data_stages/{title}.png')

class FrequencyMatrix:
    def __init__(self):
        self.frequency_dict = {}

    def add_to_frequency_dict(self, key1: str, key2: str):
        if key1 in self.frequency_dict:
            if key2 in self.frequency_dict[key1]:
                self.frequency_dict[key1][key2] += 1
            else:
                self.frequency_dict[key1][key2] = 1
        else:
            self.frequency_dict[key1] = {key2: 1}

    def plot_matrix(self, data_dict: dict = None, title='Frequency Matrix'):
        if data_dict is None:
            data_dict = self.frequency_dict

        # Create a set of all unique keys for key1 and key2
        key1_set = set(data_dict.keys())
        key2_set = set()
        for sub_dict in data_dict.values():
            key2_set.update(sub_dict.keys())

        # Create sorted lists of keys
        sorted_key1 = sorted(key1_set)
        sorted_key2 = sorted(key2_set)

        # Initialize a matrix with zeros
        matrix = np.zeros((len(sorted_key1), len(sorted_key2)))

        # Fill the matrix with frequency values
        for i, key1 in enumerate(sorted_key1):
            for j, key2 in enumerate(sorted_key2):
                if key2 in data_dict[key1]:
                    matrix[i, j] = data_dict[key1][key2]

        # Plot the matrix
        plt.figure(figsize=(7, 10))
        plt.imshow(matrix, cmap='viridis', interpolation='nearest')
        plt.colorbar(label='Frequency')
        plt.xticks(range(len(sorted_key2)), sorted_key2, rotation=90)
        plt.yticks(range(len(sorted_key1)), sorted_key1)
        plt.xlabel('Bug Type')
        plt.ylabel('Patch Type')
        plt.title(title)
        plt.tight_layout()

        # Annotate the matrix with frequency values
        for i in range(len(sorted_key1)):
            for j in range(len(sorted_key2)):
                plt.text(j, i, int(matrix[i, j]), ha='center', va='center', color='white')

        plt.savefig(f'./data_stages/{title}.png')