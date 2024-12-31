import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from pdf2image import convert_from_path
import io
import pickle
import sys

SAVEFILENAME = "numbers.pkl"
FOUNDFILES = "done_recog.txt"

# Set the path to the credentials JSON file (set the environment variable as shown above)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "receipt-id-naming-a5ddc498c7c0.json"

# Initialize the Vision API client
client = vision.ImageAnnotatorClient()

# Function to convert pdf into many images, 1 for each page
def pdf_to_pages(pdf_directory, page_directory):
    for filename in os.listdir(pdf_directory):
        file_path = os.path.join(pdf_directory, filename)

        # Process only image files
        if file_path.lower().endswith(('.pdf')):
            print(f"Processing {filename}...")

            images = convert_from_path(file_path)
            i = 1
            for image in images:
                save_path = os.path.join(page_directory, f"{filename[:-4]}{str(i).zfill(3)}.jpg")
                image.save(save_path)
                i += 1

                print(f"Image saved: {save_path}")
        else:
            print(f"Skipping non-pdf file: {filename}")

# Function to get text content from image file path
def get_content(file_path):
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
            
    # Prepare the image for the Vision API
    image = types.Image(content=content)

    return image

# Gets all 5-digit numbers in a certain string
def get_numbers(text, pagename):
    nums = []
    for i in range(len(text)-5):
        chunk = text[i:i+5]
        if chunk.isdigit() and not text[i-1].isdigit() and not text[i+5].isdigit(): # five-digit number
            # number must be in the range 15000 to 26000
            if True:
            #if 18000 <= int(chunk) <= 26000:
                nums.append((chunk, pagename))
    return nums

# Writes data to pkl file, OVERWRITING existing data
def write_to_pkl(data):
    with open(SAVEFILENAME, "wb") as fhand:
        pickle.dump({"dat": data}, fhand)

# Reads all data from pkl file
def read_from_pkl():
    with open(SAVEFILENAME, "rb") as fhand:
        return pickle.load(fhand)["dat"]

# Function to find all five-digit numbers
def count_occurrences_in_directory(page_directory):
    with open(FOUNDFILES, "r") as fhand:
        found = set([s.strip() for s in fhand.readlines()])
    try:
        nums_dict = read_from_pkl()
    except:
        nums_dict = []

    i = 0
    for filename in os.listdir(page_directory):
        file_path = os.path.join(page_directory, filename)

        # Process only image files
        if file_path.lower().endswith(('.jpg')) and filename not in found:
            print(f"Processing {filename}...")

            image = get_content(file_path)

            # Call the Vision API for text detection (handwritten text detection is also handled here)
            response = client.text_detection(image=image)

            # Check for any errors in the response
            if response.error.message:
                raise Exception(f"API request failed: {response.error.message}")

            # Extract the detected text from the response
            detected_text = response.text_annotations

            # If text is found, return the full detected text (the first item contains all detected text)
            if detected_text:
                #print(detected_text[0].description)
                fivedigits = get_numbers(detected_text[0].description, filename[:-4])
                nums_dict += fivedigits
                print(f"{len(fivedigits)} five-digit numbers found")
                
            with open(FOUNDFILES, "a") as fhand:
                fhand.write(filename+"\n")
            found.add(filename)

        else:
            print(f"Skipping non-image file: {filename}")

        i += 1
        if i % 10 == 0:
            write_to_pkl(nums_dict)
            print("Saving...")
    
    write_to_pkl(nums_dict)
    return nums_dict

# Run the function to rename images in the specified directory
pages_directory = "./pages"
# pages_directory = "./test_again"
pdf_directory = "./pdf"

print("Welcome to the ID number recognition utility!")
if input("Y/N: would you like to convert pdf to pages? ").lower().startswith("y"):
    pdf_to_pages(pdf_directory, pages_directory)
if input("Y/N: would you like to count ID occurrences in a dict and save them to pkl? ").lower().startswith("y"):
    print(count_occurrences_in_directory(pages_directory))
