import os

root = os.path.dirname(__file__)
data_folder = os.path.join(root, "data")
persistence_folder = os.path.join(root, "persistence")

os.makedirs(persistence_folder, exist_ok=True)


