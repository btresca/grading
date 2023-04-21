# grading
Python library for grading assessments.

# author
Blake Tresca, Kalamazoo College.

# How to
1) Install Anaconda on your local computer https://www.anaconda.com/ 
2) Donwload and install teaching.yml in Anaconda 
3) Create your teaching folder on local computer and download all of the .py files there.
4) Open terminal app or start a python window within Anaconda.
5) Activate Teaching environment
    `conda activate teaching`
6) Navigate to teaching folder
    `cd ~/usr/../teaching`
7) Run student QR sheet generator
    `python OCN_sheet.py classlist.csv`
    Note: Save your classlist to teaching folder as csv, must have at least two columns with titles in first row.
8) Follow prompts in python to generate QR sheets
9) Prepare a quiz and insert QR code
9b) Optional: Make reassessment packs with student QR codes added
10) Scan complete assessments into individual pdf, one page per file
11) Use rename script to read assessment and student codes
12) Read grades from assessments
