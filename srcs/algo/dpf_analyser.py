import math
import os

import matplotlib.pyplot as plt
from collections import Counter
import json
import numpy as np
from scipy.optimize import fsolve
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from srcs.p2m.p2m_types import DpfType
from srcs.p2m import p2m_path


N_COMPONENTS = 5

class BoundaryFinder:
    def __init__(self, gaussian_list: list[tuple]):
        self.gaussian_list: list[tuple] = gaussian_list
        self.gaussian_list.sort(key=lambda x: x[0])

    def _decision_boundary(self, x, mean1, var1, weight1, mean2, var2, weight2):
        lhs = np.log(weight1 / weight2) + 0.5 * (np.log(var2) - np.log(var1))
        rhs = (x - mean2) ** 2 / (2 * var2) - (x - mean1) ** 2 / (2 * var1)
        return lhs - rhs

    def _calculate_boundary(self, gaussian1, gaussian2):
        x_boundary = fsolve(self._decision_boundary, 0, args=(
            *gaussian1,
            *gaussian2,
        ))
        return float(x_boundary[0])

    def find_neutral_index(self) -> int:
        means: list[tuple[int, int]] = [(i, e[0]) for i, e in enumerate(self.gaussian_list)]
        neutral_index: int = sorted(means, key=lambda x:abs(x[1]))[0][0]
        return neutral_index

    def find_note_on_decision_boundary(self):
        note_on_index = self.find_neutral_index() + 1
        note_on_gaussian = self.gaussian_list[note_on_index]
        possible_boundaries = [
            self._calculate_boundary(x, note_on_gaussian) for x in self.gaussian_list[:note_on_index]
        ]
        return max(possible_boundaries)

    def find_note_off_decision_boundary(self):
        note_on_index = self.find_neutral_index() - 1
        note_on_gaussian = self.gaussian_list[note_on_index]
        possible_boundaries = [
            self._calculate_boundary(x, note_on_gaussian) for x in self.gaussian_list[note_on_index + 1:]
        ]
        return min(possible_boundaries)


def flatten_list(data) -> list:
    if not isinstance(data, list):
        return [data]
    flat_list = []

    for item in data:
        flat_list.extend(flatten_list(item))

    return flat_list


class Analyser:
    def __init__(self, raw_data: list[int] | list[list[int]] | None=None):
        self.scaler: StandardScaler = StandardScaler()
        self.raw_data: list[int] = [] if raw_data is None else flatten_list(raw_data)
        self._data: list[int] = []
        self.gaussian_list: list[tuple] = []
        self.generate_data_from_raw()

    def generate_data_from_raw(self):
        self.gaussian_list = []
        self._data = []

        data_counter = Counter(flatten_list(self.raw_data))

        for k, i in data_counter.items():
            max_freq = 1000
            val = round(- max_freq / i + max_freq // 10)
            data_counter[k] = val if val >= 0 else 0

        # frequencies = sorted(list(data_counter.values()))

        for val, frequency in data_counter.items():
            self._data += [val] * frequency

    def set_data(self, new_data):
        self.raw_data = new_data
        self.generate_data_from_raw()

    def _load_data_from_file(self, file_path: str):
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                self.raw_data += json_data["dpf"]
        except (json.decoder.JSONDecodeError, KeyError):
            pass

    def load_data_from_file(self, file_path: str):
        self._load_data_from_file(file_path)
        self.generate_data_from_raw()

    def load_data_from_history(self, directory_path: str):
        self.raw_data = []  # Clear any previous data
        for root, _, files in os.walk(directory_path):
            for file in files:
                if not file.endswith(".json"):
                    continue
                file_path = os.path.join(root, file)
                self._load_data_from_file(file_path)
        self.generate_data_from_raw()

    def plot_data(self):
        if not self._data:
            raise RuntimeError("No data to process. Please load data first.")
        data_counter = Counter(self._data)
        unique_values = list(data_counter.keys())
        frequencies = list(data_counter.values())
        plt.bar(unique_values, frequencies)
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Frequency of Unique Values")
        plt.show()

    def find_gmm(self, n_components=N_COMPONENTS):
        if self.gaussian_list and len(self.gaussian_list) == n_components:
            return self.gaussian_list
        if not self._data:
            raise RuntimeError("No data to process. Please load data first.")

        data_array = np.array(self._data).reshape(-1, 1)
        data_scaled = self.scaler.fit_transform(data_array)

        # Fit Gaussian mixture model with adjusted regularization
        gmm = GaussianMixture(
            n_components=n_components,
            random_state=42,
            reg_covar=1e-4,
        )
        gmm.fit(data_scaled)

        # Reverse scaling to interpret results
        means = self.scaler.inverse_transform(gmm.means_).flatten()
        covariances = gmm.covariances_.flatten() * self.scaler.var_[0]  # Adjust covariances
        weights = gmm.weights_

        self.gaussian_list = list(zip(means, covariances, weights))
        return self.gaussian_list

    def fit_and_plot_gmm(self, n_components=N_COMPONENTS):
        self.find_gmm(n_components)

        print("Fitted GMM Parameters:")
        print(f"{'Mean':>15}{'Covariance':>15}{'Weight':>15}")
        for idx, entry in enumerate(self.gaussian_list):
            print(f"{idx:>3}){entry[0]:>11.2f}{entry[1]:>15.2f}{entry[2]:>15.2f}")

        # Prepare the histogram with frequencies
        data_counter = Counter(self._data)
        unique_values = list(data_counter.keys())
        frequencies = list(data_counter.values())

        # Plot the histogram with frequencies
        bin_width = 1
        plt.bar(unique_values, frequencies, width=bin_width, alpha=0.5, label="Data histogram", color="gray")

        # Generate x values for GMM PDF
        x = np.linspace(min(self._data), max(self._data), 1000).reshape(-1, 1)

        for mean, cov, weight in self.gaussian_list:
            gaussian = (
                    weight * len(self._data) * (1 / np.sqrt(2 * np.pi * cov))
                    * np.exp(-0.5 * ((x - mean) ** 2 / cov))
            )
            plt.plot(x, gaussian, linestyle="--", label=f"Gaussian {mean:6.2f} cov={cov:6.2f}")

        # Improve plot appearance
        plt.title(f"Gaussian Mixture Model (n={n_components})")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.legend()
        plt.show()

        return self.gaussian_list

    def export(self, path):
        with open(path, 'w+') as file:
            file.write(json.dumps(self._data))

    def find_note_thresholds(self, plot=False):
        """
        Finds the decision boundary between note on (mean > 0) and other distributions
        :param plot: shows graph if set to true
        :return: tuple (note_off_bounds, note_on_bounds)
        """
        self.find_gmm()
        bf = BoundaryFinder(self.gaussian_list)
        note_on_bounds = bf.find_note_on_decision_boundary()
        note_off_bounds = bf.find_note_off_decision_boundary()
        if plot:
            print(f"Note On Boundary: {note_on_bounds:.2f}")
            print(f"Note Off Boundary: {note_off_bounds:.2f}")
            self.fit_and_plot_gmm()
        return note_off_bounds, note_on_bounds


def main():
    directory_path = os.path.join(p2m_path.DATA_DIR, "dpf", "Eula Flickering Candlelight.dpf.json")  # Adjust the directory path
    analyser = Analyser()
    analyser.load_data_from_file(directory_path)
    # analyser.plot_data()
    # analyser.fit_and_plot_gmm(3)
    # analyser.fit_and_plot_gmm()
    import time
    start = time.time_ns()
    note_off_bounds, note_on_bounds = analyser.find_note_thresholds()
    print(f"Time used: {(time.time_ns() - start) / 1_000_000_000:.2f}s")
    print(f"Note On Boundary: {note_on_bounds:.2f}")
    print(f"Note Off Boundary: {note_off_bounds:.2f}")
    analyser.fit_and_plot_gmm()
    # plotter.export("dpf_data.json")
    # print(plotter.data.__len__())

if __name__ == '__main__':
    main()