# Script to scan all PDFs in directory for QR codes then rename from QR data
import fitz
import cv2
import numpy as np
import os
from PIL import Image
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode

# run for single pdf file
# pdf_file = "test_scan.pdf"

mat = fitz.Matrix(2, 2)
count = 0
title_count = 0

# Apply to all pdfs in current directory
pdf_files = [filename for filename in os.listdir(
    os.getcwd()) if filename.endswith('.pdf')]

# read the QRCODE image
# img = cv2.imread("site.png")
# images = convert_from_path(pdf_file)

for pdf_file in pdf_files:
    images = fitz.open(pdf_file)
    quiz_title = None
    ocn = None
    image = images.loadPage(0)
    image = image.getPixmap(matrix=mat)
    image_pil = Image.frombytes(
        "RGB", [image.width, image.height], image.samples)
    image = np.array(image_pil)
    #print(image.shape)
    image = image[0:400, 0:1792]
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(grey, 200, 255, cv2.THRESH_BINARY)[1]

    #cv2.imshow(pdf_file, image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #break
    qr_codes = decode(image)
    #initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()
    # if there is a QR code
    if bool(qr_codes) is True:
        for qr_data in qr_codes:
            qr_data_str = str(qr_data.data, 'utf-8')
            #qr_data_str = qr_data_str.replace("b'", "")
            #qr_data_str = qr_data_str.replace("'", "")
            print(qr_data)
            #if "OCN_" in qr_dat:
            if qr_data_str.find("OCN_") != -1:
                ocn = qr_data_str.replace("OCN_", "_")
                print(f"QRCode OCN:", ocn)
            else:
                quiz_title = qr_data_str.replace(" ", "_")
                print(f"QRCode quiz:", quiz_title)
    else:
        print("No QR Code")

        # set new filename
    if quiz_title == None:
        quiz_title = 'Unk'
        #title_count = title_count + 1
    if ocn == None:
        count = count + 1
        ocn = "_" + str(count)

    fname = f"{quiz_title}{ocn}.pdf"

    if os.path.exists(fname):
        i = 0
        while os.path.exists(f"{quiz_title}_{i}{ocn}.pdf"):
            i += 1

        fname = f"{quiz_title}_{i}{ocn}.pdf"

    print("Renaming:", pdf_file, ">>>", fname)
    os.rename(pdf_file, fname)
