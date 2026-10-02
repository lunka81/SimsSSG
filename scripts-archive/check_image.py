import io
import pandas as pd
from PIL import Image

df = pd.read_parquet("data/celeba-spoof/data/test-00000-of-00010.parquet")

for i in range(6):
    row = df.iloc[i]
    img = Image.open(io.BytesIO(row["cropped_image"]["bytes"]))
    print(i, row["labelNames"], img.size)
    img.save(f"sample_{i}_{row['labelNames']}.jpg")

print("Saved six samples, open them and look")