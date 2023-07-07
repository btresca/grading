import os
import shutil
import sys

import fitz
import numpy as np
import pandas
import qrcode
from PIL import Image, ImageDraw, ImageFont

title_font = ImageFont.truetype('/System/Library/Fonts/NewYork.ttf', size=14)

# test for quiz title as argument
if len(sys.argv) < 2:
    print("Usage: python3 onc_qr_sheet.py <gradebook.csv>")
    exit(0)

# quiz pdf input and outputs
input_file = "ocn_sheet.pdf"

# read quiz title from command lines
gradebook = sys.argv[1]

if gradebook.find(".csv") == -1:
    print("Is your gradebook a csv? If yes, try changing extension to .csv")
    exit(0)

# import gradebook and print first 5 lines to confirm correct
gradebook = pandas.read_csv(gradebook)
print(gradebook.loc[[0, 1, 2, 3, 4, 5]])
# proceed = input("Is this correct (y/n): ")
# print(proceed)
print("Is this correct? If not, enter stop.")
ocn_title = input("Otherwise, enter column title for class codes: ")
print(ocn_title)
if ocn_title == 'stop':
    exit(0)

gradebook[ocn_title] = gradebook[ocn_title].apply(
    lambda x: '{0:0>4}'.format(x))

ocn_list = gradebook[ocn_title]

print(ocn_list)

IMG_DIR = 'qr_imgs'
SHEET_DIR = 'qr_sheets'
# Delete folder if exists and create it again
try:
    shutil.rmtree(IMG_DIR)
    os.mkdir(IMG_DIR)
except FileNotFoundError:
    os.mkdir(IMG_DIR)
try:
    shutil.rmtree(SHEET_DIR)
    os.mkdir(SHEET_DIR)
except FileNotFoundError:
    os.mkdir(SHEET_DIR)

for index, ocn in ocn_list.items():
    # print(ocn) #uncomment for troubleshooting
    ocn_str = 'OCN_' + str(ocn)
    # qr image output file name
    qr_out = ocn_str + "_qr.png"
    output_file = ocn_str + "_qr.pdf"
    # generate qr code
    img = qrcode.make(
        ocn_str, error_correction=qrcode.constants.ERROR_CORRECT_L)
    # save img to a file
    img = img.resize((75, 75))
    img.save(f'{IMG_DIR}/{qr_out}')

    # create pixmap from qr picture
    src = fitz.Pixmap(f'{IMG_DIR}/{qr_out}')
    col = 6                                  # tiles per row
    lin = 8                                  # tiles per column

    # create target pixmap
    #tar_pix = fitz.Pixmap(src.colorspace, (0, 0, 612, 792), src.alpha)
    #tar_pix.set_rect(tar_pix.irect, (255,))

    # retrieve the first page of the PDF
    file_handle = fitz.open(input_file)
    first_page = file_handle[0]

    # now fill target with the tiles
    for i in range(col):
        for j in range(lin):
            # define pattern for image carpet, adjust values to fit template
            width = (90 * i) + 45
            height = (90 * j) + 45
            #image_rectangle = fitz.Rect(first_page.rect.tl + width, first_page.rect.tl + height)
            #first_page.insertImage(image_rectangle, filename=f'{IMG_DIR}/{qr_out}')
                        # define pattern for image carpet, adjust values to fit template
            src.set_origin(width, height)
            first_page.insert_image(src.irect, pixmap=src)  # copy input to new loc
            width2 = width - 2
            height2 = height - 2
            src.set_origin(width2, height2)
            first_page.insert_textbox(src.irect, ocn_str, fontsize=8, fontname="Helvetica", fontfile=None, align=1)


    sheet_out = str(f'{SHEET_DIR}/{output_file}')
    file_handle.save(sheet_out)

    #first_page.insert_text((300, 18), ocn_str, fill="black", font=title_font)
    file_handle.save(sheet_out)

    #save the modified pdf as a new file
    first_page.clean_contents()
    file_handle.save(sheet_out)


    #exit(0)  # uncomment for testing and troubleshooting

print("All finished")
