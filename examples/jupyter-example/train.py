import torch
import imblearn
import os, sys


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            fp = os.path.join(root, f)
            print('{}{}:{}'.format(subindent, os.path.getsize(fp), f))

print("Hello from valohai")
print(torch.cuda.is_available())
print("bye")
print("other log again...")

print("size", os.path.getsize("/valohai/inputs/training/train.csv"))

with open("/valohai/outputs/somefile_output_example.txt", "w") as f:
    f.write("hey hey\n")
