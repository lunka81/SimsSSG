import pandas as pd

path = "data/celeba-spoof/data/test-00000-of-00010.parquet"

df = pd.read_parquet(path)

print("Rows in this file:", len(df))
print()
print("Columns:")
for c in df.columns:
    print("  ", c, " type:", df[c].dtype)
print()
print("First row, one field at a time:")
row = df.iloc[0]
for c in df.columns:
    value = row[c]
    text = str(value)
    if len(text) > 120:
        text = text[:120] + "  ... (truncated, length " + str(len(text)) + ")"
    print("  ", c, "=", text)
print()
for c in df.columns:
    if df[c].dtype == "object" and not isinstance(row[c], (bytes, dict)):
        continue
print("Label counts, if a label column exists:")
for c in df.columns:
    if df[c].nunique() < 20:
        print("  ", c)
        print(df[c].value_counts())

from PIL import Image
import io

img_field = row["cropped_image"]
if isinstance(img_field, dict):
    img = Image.open(io.BytesIO(img_field["bytes"]))
else:
    img = img_field

print("Image size:", img.size)
img.save("sample_from_dataset.jpg")
print("Saved sample_from_dataset.jpg, open it and look")