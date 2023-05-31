# Test script to scan all PDFs in directory for QR codes then rename
# from QR data
import os
import sys

# run for single pdf file
# pdf_file = "test_scan.pdf"

# test for quiz title as argument
if len(sys.argv) < 2:
    print("Usage: python3 exam_rename_pdf.py <new_quiz_title>")
    exit(0)


# read new quiz title from command lines
quiz_title = sys.argv[1]

# Apply to all pdfs in current directory
pdf_files = [filename for filename in os.listdir(
    os.getcwd()) if filename.endswith('.pdf')]

for pdf_file in pdf_files:
    ocn_quiz = None
    ocn_quiz = str(pdf_file[len(pdf_file)-8:len(pdf_file)-4])

    fname = f"{quiz_title}_{ocn_quiz}.pdf"

    if os.path.exists(fname):
        i = 0
        while os.path.exists(f"{quiz_title}_{i}_{ocn_quiz}.pdf"):
            i += 1

        fname = f"{quiz_title}_{i}_{ocn_quiz}.pdf"

    print("Renaming:", pdf_file, ">>>", fname)
    os.rename(pdf_file, fname)
