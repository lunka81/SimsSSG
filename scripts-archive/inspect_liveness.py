import os
import shutil
import onnxruntime as ort
from huggingface_hub import list_repo_files, hf_hub_download

REPO = "garciafido/minifasnet-v2-anti-spoofing-onnx"

files = list_repo_files(REPO)
print("Files in the repository:")
for f in files:
    print("  ", f)

onnx_files = [f for f in files if f.endswith(".onnx")]

if not onnx_files:
    print("No .onnx file found")
    exit()

name = onnx_files[0]
path = hf_hub_download(repo_id=REPO, filename=name)

os.makedirs("models", exist_ok=True)
local = os.path.join("models", "minifasnet_v2.onnx")
shutil.copy(path, local)
print("\nSaved to", local)

session = ort.InferenceSession(local, providers=["CPUExecutionProvider"])

print("\nInputs:")
for i in session.get_inputs():
    print("  name:", i.name, " shape:", i.shape, " type:", i.type)

print("\nOutputs:")
for o in session.get_outputs():
    print("  name:", o.name, " shape:", o.shape, " type:", o.type)