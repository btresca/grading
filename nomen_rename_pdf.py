# Script rename all PDFs in directory with OCN from image
import os
import sys
import fitz
import cv2
import numpy as np
from PIL import Image


mat = fitz.Matrix(1, 1)

# run for single pdf file
# pdf_file = "test_scan.pdf"

# test for quiz title as argument
if len(sys.argv) < 2:
    print("Usage: python3 nomen_rename_pdf.py <new_quiz_title>")
    exit(0)

# read new quiz title from command lines
quiz_title = sys.argv[1]

# Apply to all pdfs in current directory
pdf_files = [filename for filename in os.listdir(
    os.getcwd()) if filename.endswith('.pdf')]

for pdf_file in pdf_files:
    images = fitz.open(pdf_file)
    image = images.loadPage(0)
    image = image.getPixmap(matrix=mat)
    image_pil = Image.frombytes(
        "RGB", [image.width, image.height], image.samples)
    image = np.array(image_pil)
    cv2.imshow(pdf_file, image)
    cv2.waitKey(1)

    ocn_quiz = None
    # ocn_quiz = str(pdf_file[len(pdf_file)-8:len(pdf_file)-4])

    ocn_title = input("Enter student codes: ")
    print(ocn_title)
    if ocn_title == 'stop':
        exit(0)

    ocn_quiz = ocn_title

    fname = f"{quiz_title}_{ocn_quiz}.pdf"

    if os.path.exists(fname):
        i = 0
        while os.path.exists(f"{quiz_title}_{i}_{ocn_quiz}.pdf"):
            i += 1
        fname = f"{quiz_title}_{i}_{ocn_quiz}.pdf"

    print("Renaming:", pdf_file, ">>>", fname)
    os.rename(pdf_file, fname)
    cv2.destroyAllWindows()
