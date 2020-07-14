import os
import sys


root = os.path.dirname(__file__)
data_folder = os.path.join(root, "data")
persistence_folder = os.path.join(root, "persistence")

os.makedirs(persistence_folder, exist_ok=True)
os.makedirs(data_folder, exist_ok=True)

src_folder = os.path.join(root, "src")
sys.path.append(src_folder)




