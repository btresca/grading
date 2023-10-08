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
# req_table = pandas.read_csv(req_list)
quiz_list = np.loadtxt(req_list, dtype='U', delimiter=',', max_rows=1)
print(quiz_list)
req_table = np.loadtxt(req_list, dtype='l', delimiter=',', skiprows=1)
print(req_table[:3, :])
# proceed = input("Is this correct (y/n): ")
# print(proceed)
# exit()

print("Is this correct? If not, enter stop.")
ocn_title = input("Otherwise, enter column title for class codes: ")
print(ocn_title)
if ocn_title == 'stop':
    exit(0)

quiz_list = quiz_list[1:]
ocn_list = req_table[:, 0]
ocn_list = ocn_list.flatten()

print(ocn_list)

# exit()

IMG_DIR = 'qr_imgs'
SHEET_DIR = list_title
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
    #img = img.resize((81, 81))
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
        file_merge.insert_pdf(file_handle)
        file_handle.close()

    # file_merge.save(f'{SHEET_DIR}/{output_file}')

    # break

    # retrieve the first page of the PDF
    # file_handle = fitz.open(f'{SHEET_DIR}/{output_file}')

    for page in file_merge:
        output_file = ocn_str + "_qr.pdf"

        first_page = page

        # define position and size then add qr image
        # minimum readable size = 60 pts square
        image_rectangle = fitz.Rect(
            first_page.rect.x0 + 505, first_page.rect.y0 + 20, first_page.rect.x0 + 585, first_page.rect.y0 + 100)
        first_page.insert_image(image_rectangle, filename=f'{IMG_DIR}/{qr_out}')
        image_rectangle = fitz.Rect(
            first_page.rect.x0 + 505, first_page.rect.y0 + 100, first_page.rect.x0 + 585, first_page.rect.y0 + 115)
        first_page.insert_textbox(
            image_rectangle, ocn_str, fontsize=10, fontname="Helvetica", fontfile=None, align=0)

        #save the modified pdf as a new file
        first_page.clean_contents()

    file_merge.save(f'{SHEET_DIR}/{output_file}')

    # break
