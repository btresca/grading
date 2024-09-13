import sys
import fitz
import qrcode

# test for quiz title as argument
if len(sys.argv) < 2:
    print("Usage: python3 insert_qr.py <quiz_title>")
    exit(0)

# read quiz title from command lines
quiz_title = sys.argv[1]

# qr image output file name
qr_out = quiz_title + "_qr.png"
# generate qr code
img = qrcode.make(
    quiz_title, error_correction=qrcode.constants.ERROR_CORRECT_L)
# save img to a file
img.save(qr_out)

# quiz pdf input and outputs
input_file = quiz_title + ".pdf"
output_file = quiz_title + "_qr.pdf"

# retrieve the first page of the PDF
file_handle = fitz.open(input_file)
first_page = file_handle[0]

# define position and size then add qr image
# minimum readable size = 60 pts square
image_rectangle = fitz.Rect(first_page.rect.x0 + 30,
                            first_page.rect.y0 + 55,
                            first_page.rect.x0 + 110,
                            first_page.rect.y0 + 135)
first_page.insert_image(image_rectangle, filename=qr_out)

#save the modified pdf as a new file
first_page.clean_contents()
file_handle.save(output_file)
