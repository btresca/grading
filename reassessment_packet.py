import qrcode
import numpy as np
import os
import fitz
import sys
import shutil

# test for reassessment requests as argument
if len(sys.argv) < 2:
    print("Usage: python3 reassessments_packet.py <requests.csv>")
    exit(0)

# read spreadsheet title from command lines
req_list = sys.argv[1]

if req_list.find(".csv") == -1:
    print("Is your spreadsheet a csv? If yes, try changing extension to .csv")
    exit(0)

list_title = req_list.replace('.csv', '')

# import gradebook and print first 5 lines to confirm correct
quiz_list = np.loadtxt(req_list, dtype='U', delimiter=',', max_rows=1)
print(quiz_list)
req_table = np.loadtxt(req_list, dtype='l', delimiter=',', skiprows=1)
print(req_table[:3, :])

# check the csv loaded correctly
proceed = input("Is this correct (y/n): ")
print(proceed)
if proceed == 'n':
    exit(0)

quiz_list = quiz_list[1:]
ocn_list = req_table[:, 0]
ocn_list = ocn_list.flatten()

print(ocn_list)

IMG_DIR = 'qr_imgs'
SHEET_DIR = list_title

# ask whether to print OCN on final pdf
title_opt = input("Print OCN on (first/each/none) page: ")
print(title_opt)

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

for ocn in ocn_list:
    # print(ocn) #uncomment for troubleshooting
    ocn_str = 'OCN_' + str(ocn).zfill(4)
    # qr image output file name
    qr_out = ocn_str + "_qr.png"
    # generate qr code
    img = qrcode.make(
        ocn_str, error_correction=qrcode.constants.ERROR_CORRECT_L)
    # save img to a file
    # img = img.resize((81, 81))
    img.save(f'{IMG_DIR}/{qr_out}')

for req in req_table:
    ocn = req[0]
    ocn_str = 'OCN_' + str(ocn).zfill(4)
    qr_out = ocn_str + "_qr.png"
    ocn_req = req[1:]
    ocn_req = ocn_req == 1
    print(ocn_req)

    quiz_req = quiz_list[ocn_req]
    print(quiz_req)
    # break

    file_merge = fitz.open()

    for quiz in quiz_req:

        input_file = quiz + "_qr.pdf"
        output_file = ocn_str + ".pdf"

        file_handle = fitz.open(input_file)
        if title_opt == 'first':
            first_page = file_handle[0]
            # insert qr code of OCN
            image_rectangle = fitz.Rect(
                        first_page.rect.x0 + 490,
                        first_page.rect.y0 + 59,
                        first_page.rect.x0 + 570,
                        first_page.rect.y0 + 139)
            first_page.insertImage(
                image_rectangle, filename=f'{IMG_DIR}/{qr_out}')
            # insert text of OCN above QR code
            for page in file_handle:
                image_rectangle = fitz.Rect(
                            page.rect.x0 + 510,
                            page.rect.y0 + 50,
                            page.rect.x0 + 570,
                            page.rect.y0 + 65)
                page.insertTextbox(
                            image_rectangle, ocn_str, fontsize=10,
                            fontname="Helvetica", fontfile=None, align=0)
                page.clean_contents()

        if title_opt == 'each':
            for page in file_handle:
                image_rectangle = fitz.Rect(
                        page.rect.x0 + 490,
                        page.rect.y0 + 59,
                        page.rect.x0 + 570,
                        page.rect.y0 + 139)
                page.insertImage(
                    image_rectangle, filename=f'{IMG_DIR}/{qr_out}')
                image_rectangle = fitz.Rect(
                            page.rect.x0 + 510,
                            page.rect.y0 + 50,
                            page.rect.x0 + 570,
                            page.rect.y0 + 65)
                page.insertTextbox(
                                image_rectangle, ocn_str, fontsize=10,
                                fontname="Helvetica", fontfile=None, align=0)
                page.cleanContents()

        file_merge.insertPDF(file_handle)
        file_handle.close()

    file_merge.save(f'{SHEET_DIR}/{output_file}')

    file_merge.close()
