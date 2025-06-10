import cv2
import pytesseract
import pandas as pd
import numpy as np


# Load the image
image_path = "c26eeb8f-e8e9-47b0-a3ea-d2e4f2bf2e1f.png"
img = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Optional: Remove grid lines to help OCR
gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                             cv2.THRESH_BINARY_INV, 15, 10)

# OCR to extract each cell with bounding box
custom_config = r'--oem 3 --psm 6'  # Assume uniform blocks of text
details = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=custom_config)

# Collect rows
rows = []
row = []
last_top = 0

for i in range(len(details['text'])):
    word = details['text'][i].strip()
    if word == "":
        continue

    top = details['top'][i]
    if abs(top - last_top) > 15:  # New row threshold
        if row:
            rows.append(row)
        row = [word]
        last_top = top
    else:
        row.append(word)

# Add last row
if row:
    rows.append(row)

# Fix any rows with misaligned columns (optional: pad/crop to 7 columns)
cleaned_rows = []
for r in rows:
    if len(r) >= 7:
        cleaned_rows.append(r[:7])
    else:
        r += [""] * (7 - len(r))  # pad with blanks
        cleaned_rows.append(r)

# Convert to DataFrame
df = pd.DataFrame(cleaned_rows[1:], columns=cleaned_rows[0])
print(df)
