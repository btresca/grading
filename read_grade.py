## Script to scan all PDFs in directory for grades
## Assumes that pdf_ocn_rename already run so file name is formeted: assessment_OCN.pdf
## v2 - uses pandas and sorts grades by OCN
## v3 - fixed four_point_transform error, reads five grade levels A-F

import os
import cv2
import fitz
import imutils
import numpy as np
import pandas as pd
from PIL import Image

# Uncomment to run for single pdf file when testing
# pdf_file = "test_scan.pdf"

mat = fitz.Matrix(2, 2)

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

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
    image = images.load_page(0)
    image = image.get_pixmap(matrix=mat)
    image_pil = Image.frombytes(
        "RGB", [image.width, image.height], image.samples)
    image = np.array(image_pil)
    #print(image.shape)

    ## crop image and convert to black and white with threshold
    image = image[1300:1580, 100:1220]
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #image_black = cv2.threshold(grey, 150, 255, cv2.THRESH_BINARY)[1]
    #cv2.imshow(pdf_file, image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #break

    blurred = cv2.GaussianBlur(grey, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    #cv2.imshow(pdf_file, edged)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #break

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

## Fixed four_point_transform crop error by def func above
    warped = four_point_transform(grey, docCnt.reshape(4, 2))
    crop = 3
    y1 = paper.shape[0]
    x1 = paper.shape[1]
    paper = paper[crop:y1-crop, crop:x1-crop]
    y1 = warped.shape[0]
    x1 = warped.shape[1]
    warped = warped[crop:y1-crop, crop:x1-crop]

    #cv2.imshow(pdf_file, paper)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #cv2.imshow(pdf_file, warped)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #break

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
    elif cX >= 810 and cX <= 870:
        grade = "F"
    elif cX >= 700 and cX <= 760:
        grade = "D"
    elif cX >= 575 and cX <= 635:
        grade = "C"
    elif cX >= 465 and cX <= 525:
        grade = "B"
    elif cX >= 350 and cX <= 410:
        grade = "A"
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
