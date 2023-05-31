## Script to scan all PDFs in directory for grades
## Assumes that pdf_ocn_rename already run so file name is formeted: assessment_OCN.pdf
## v2 - uses pandas and sorts grades by OCN
import fitz
import cv2
import numpy as np
import pandas as pd
import os
from PIL import Image
# from pdf2image import convert_from_path
import imutils
from imutils.perspective import four_point_transform
# from imutils import contours


# Uncomment to run for single pdf file when testing
# pdf_file = "test_scan.pdf"

mat = fitz.Matrix(2, 2)

# Apply to all pdfs in current directory
pdf_files = [filename for filename in os.listdir(
    os.getcwd()) if filename.endswith('.pdf')]

#grades = np.empty((0, 3), dtype=str)
grades = pd.DataFrame({'OCN' : []})
grades = grades.set_index('OCN')

for pdf_file in pdf_files:
    images = fitz.open(pdf_file)
    quiz_title = None
    ocn_quiz = None
    ocn_quiz = str(pdf_file[len(pdf_file)-8:len(pdf_file)-4])
    quiz_title = str(pdf_file[0:len(pdf_file)-9])
    image = images.loadPage(0)
    image = image.getPixmap(matrix=mat)
    image_pil = Image.frombytes(
        "RGB", [image.width, image.height], image.samples)
    image = np.array(image_pil)
    # print(image.shape)

    ## crop image and convert to black and white with threshold
    image = image[100:280, 300:950]
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_black = cv2.threshold(grey, 150, 255, cv2.THRESH_BINARY)[1]
    # cv2.imshow(pdf_file, image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # break

    blurred = cv2.GaussianBlur(grey, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # cv2.imshow(pdf_file, edged)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # break

    ## find contours in the edge map, then initialize
    ## the contour that corresponds to the document
    cnts = None
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None
    # ensure that at least one contour was found
    if len(cnts) > 0:
        # sort the contours according to their size in
        # descending order
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        # loop over the sorted contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # if our approximated contour has four points,
            # then we can assume we have found the paper
            if len(approx) == 4:
                docCnt = approx
                break

    # apply a four point perspective transform to both the
    # original image and grayscale image to obtain a top-down
    # birds eye view of the paper
    try:
        paper = four_point_transform(image, docCnt.reshape(4, 2))
    except AttributeError:
        print("No grades in", pdf_file)
        continue

    warped = four_point_transform(grey, docCnt.reshape(4, 2))
    crop = 3
    y1 = paper.shape[0]
    x1 = paper.shape[1]
    paper = paper[crop:y1-crop, crop:x1-crop]
    y1 = warped.shape[0]
    x1 = warped.shape[1]
    warped = warped[crop:y1-crop, crop:x1-crop]

    # cv2.imshow(pdf_file, warped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # break

    # apply Otsu's thresholding method to binarize the warped
    # piece of paper
    thresh = cv2.threshold(
        warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # find contours in the thresholded image, then initialize
    # the list of contours that correspond to questions
    try:
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except AttributeError:
        print("No grade in", pdf_file)
        continue
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    questionCnts = []
    largest = cnts[0]
    # cv2.drawContours(paper, cnts[0], -1, (0, 0, 255), thickness=5)

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour, then use the
        # bounding box to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1
        if w >= 30 and h >= 30 and ar >= 0.8 and ar <= 1.6:
            questionCnts.append(c)
            largest = c

    # loop over the contours
    # for c in questionCnts:
        # compute the center of the contour
    M = cv2.moments(largest)
    if M["m00"] == 0:
        continue
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # draw the contour and center of the shape on the image
    cv2.drawContours(paper, [largest], -1, (0, 255, 0), 2)
    cv2.circle(paper, (cX, cY), 7, (128, 0, 0), -1)
    cv2.putText(paper, "center", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 0), 2)
    ## show the image
    # cv2.imshow("Image", paper)
    # cv2.waitKey(0)
    (x, y, w, h) = cv2.boundingRect(largest)
    ar = w / float(h)

    if w <= 30 and h <= 30 and ar <= 0.8 and ar <= 1.4:
        grade = "x"
    elif cX >= 360 and cX <= 390:
        grade = "U"
    elif cX >= 240 and cX <= 300:
        grade = "P"
    elif cX >= 180 and cX <= 210:
        grade = "E"
    else:
        grade = "x"
    print(ocn_quiz, cX, cY, grade)

#test if column and ocn exists, if not then add them
    if quiz_title not in grades.columns:
        grades[quiz_title] = ""
    if ocn_quiz not in grades.index:
        new_ocn = pd.DataFrame(columns = grades.columns, index = [ocn_quiz])
        #new_ocn['OCN'] = [ocn_quiz]
        pd.concat([grades, new_ocn])

    #ocn_index = grades.index[grades['OCN']==ocn_quiz]
    grades.at[ocn_quiz, quiz_title] = grade
    cv2.imshow(str(pdf_file + '    ' + grade), paper)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # break

grades_out = grades.sort_index()
grades_out.to_csv('grades.csv')

print(grades_out)

## Fill grades into gradebook
#grades = pd.read_csv('grades.csv', index_col="OCN")
#grades.head()
#gradebook = pd.read_csv('../gradebook.csv', index_col="OCN")
#gradebook.head()
#for rows in grades:
