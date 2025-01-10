# -*- coding: utf-8 -*-
"""combind_b.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AUTKFUY4XLjsk1XzA7SPA9YwYOMR3QUS
"""

import os
import numpy as np
import pandas as pd

# Folder paths
value_folder = "C:\\Users\\user\\Desktop\\vscode\\MLHW2\\modeltxt"  # Replace with the folder path containing value files
classification_folder = "C:\\Users\\user\\Desktop\\vscode\\MLHW2\\classmodeltxt"  # Replace with the folder path containing classification result files

# Evaluation data paths
eval_y = "C:\\Users\\user\\Desktop\\vscode\\MLHW2\\y.csv"
eval_w = "C:\\Users\\user\\Desktop\\vscode\\MLHW2\\y_w.csv"

# Utility function to read files
def read_file(filepath):
    with open(filepath, "r") as file:
        data = np.array([float(line.strip()) for line in file])  # Read numbers and convert to numpy array
    return data

# Read files in the folder
def load_files(folder_path):
    files_data = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith("_predictions.txt"):  # Filter files
            model_name = "_".join(file_name.split("_")[:2])  # Extract model name (e.g., xgb_0, lgb_4)
            files_data[model_name] = read_file(os.path.join(folder_path, file_name))
    return files_data

# Load value files and classification files
value_data = load_files(value_folder)
classification_data = load_files(classification_folder)

for key, array in classification_data.items():
    classification_data[key] = np.where(array == 0, -1, array)

# Step 1: Combine classes
combined_classes = np.sign(
    np.array([classification_data['cbt_0'], classification_data['lgb_0'], classification_data['xgb_0']]).sum(axis=0)
)
class_result = {'combined': combined_classes}

# Step 2: Average values by model group
value_result = {}
for model_prefix in ['cbt', 'lgb', 'xgb']:
    values = np.mean(
        np.array([value for key, value in value_data.items() if key.startswith(model_prefix)]),
        axis=0
    )
    value_result[model_prefix] = values

# Step 3: Weighted output based on class_result and value_result agreement
final_output = []
for i in range(len(combined_classes)):
    weights = [0.33, 0.33, 0.33]  # Default weights if all disagree
    matched_models = [key for key in value_result.keys() if np.sign(value_result[key][i]) == combined_classes[i]]

    if len(matched_models) == 3:
        weights = [1/3] * 3
    elif len(matched_models) == 2:
        weights = [0.4 if model in matched_models else 0.2 for model in value_result.keys()]
    elif len(matched_models) == 1:
        weights = [0.5 if model in matched_models else 0.25 for model in value_result.keys()]

    weighted_value = sum(weights[j] * value_result[list(value_result.keys())[j]][i] for j in range(3))
    final_output.append(weighted_value)

final_output = np.array(final_output)

"""# Performance Evaluation"""

def r2(y_true, y_pred, sample_weight):
    r2 = 1 - np.average((y_pred - y_true) ** 2, weights=sample_weight) / (np.average((y_true) ** 2, weights=sample_weight) + 1e-38)
    return r2

data1 = pd.read_csv(eval_y)
data2 = pd.read_csv(eval_w)

r2 = 1 - np.average((final_output - data1['responder_6'].values) ** 2, weights=data2['weight'].values) / (np.average((data1['responder_6'].values) ** 2, weights=data2['weight'].values) + 1e-38)

r2