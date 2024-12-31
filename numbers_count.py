import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from pdf2image import convert_from_path
import time
from tenacity import retry
import io

PHRASE = "签收人"
SAVEFILENAME = "done.txt"

# Set the path to the credentials JSON file (set the environment variable as shown above)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "receipt-id-naming-a5ddc498c7c0.json"

# Initialize the Vision API client
client = vision.ImageAnnotatorClient()

# Function to convert pdf into many images, 1 for each page
def pdf_to_pages(pdf_directory, page_directory):
    count = 0
    for filename in os.listdir(pdf_directory):
        file_path = os.path.join(pdf_directory, filename)

        # Process only image files
        if file_path.lower().endswith(('.pdf')) and "7" in filename:
            print(f"Processing {filename}...")

            images = convert_from_path(file_path)
            for image in images:
                save_path = os.path.join(page_directory, f"temp{count}.jpg")
                image.save(save_path)
                count += 1

                print(f"Image saved: {save_path}")
        else:
            print(f"Skipping non-pdf file: {filename}")

# Function to get text content from image file path
@retry
def get_content(file_path):
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
            
    # Prepare the image for the Vision API
    image = types.Image(content=content)

    return image

# Function to find the number of occurrences of a phrase
def count_occurrences_in_directory(page_directory):
    # place old value here
    ans = 2330
    with open(SAVEFILENAME, "r") as fhand:
        found = set([s.strip() for s in fhand.readlines()])
    for filename in os.listdir(page_directory):
        file_path = os.path.join(page_directory, filename)

        # Process only image files
        if file_path.lower().endswith(('.jpg')) and filename not in found:
            print(f"Processing {filename}...")
            #print(found)

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
                num = detected_text[0].description.count(PHRASE)
                ans += num
                print(f"{num} occurrences of {PHRASE} found, {ans} cumulative")
            with open(SAVEFILENAME, "a") as fhand:
                fhand.write(filename+"\n")
            found.add(filename)
                

        else:
            print(f"Skipping non-image file: {filename}")
    
    return ans

# Run the function to rename images in the specified directory
pdf_directory = './pdf'
pages_directory = "./pages"

#pdf_to_pages(pdf_directory, pages_directory)
print(count_occurrences_in_directory(pages_directory))