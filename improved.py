import os
from google.cloud import vision
from google.cloud.vision_v1 import types
import io
import pickle

# Set the path to the credentials JSON file (set the environment variable as shown above)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "receipt-id-naming-a5ddc498c7c0.json"

WRITTEN_PATH = "taken_names.pkl"
taken = [0]*30000

# Initialize the Vision API client
client = vision.ImageAnnotatorClient()

# Function to extract handwritten text from an image using Google Vision API
def extract_text_from_image(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    # Prepare the image for the Vision API
    image = types.Image(content=content)

    # Call the Vision API for text detection (handwritten text detection is also handled here)
    response = client.text_detection(image=image)

    # Check for any errors in the response
    if response.error.message:
        raise Exception(f"API request failed: {response.error.message}")

    # Extract the detected text from the response
    detected_text = response.text_annotations

    # If text is found, return the full detected text (the first item contains all detected text)
    if detected_text:
        return detected_text[0].description
    else:
        return None

# Function to rename images in the directory based on extracted ID
def rename_images_in_directory(image_directory):
    for filename in os.listdir(image_directory):
        file_path = os.path.join(image_directory, filename)

        # Process only image files
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {filename}...")
            if filename.split(".")[0].isdigit() and len(filename.split(".")[0]) == 5:
                continue

            # Extract text from the image
            extracted_text = extract_text_from_image(file_path)
            
            #print(extracted_text)
            if extracted_text:
                # Assuming the ID is numeric and extract it from the detected text
                id_number = ''.join(filter(str.isdigit, extracted_text))
                # remove the last digit because it's a 3 and has nothing to do with the id
                id_number = id_number[:len(id_number)-1]
                # take only the last 5 digits
                id_number = id_number[-5:]

                # ID number must be between 15000 and 26000
                if not 15000 < int(id_number) < 26000:
                    id_number = input(f"{filename} requires manual labelling")
                if id_number:
                    # Rename the file with the extracted ID number
                    new_filename = f"{id_number}.jpg"  # Modify the file extension as needed
                    new_file_path = os.path.join(image_directory, new_filename)
                    # Rename the file
                    os.rename(file_path, new_file_path)
                    print(f"Renamed to {new_filename}")
                    
            else:
                print(f"No text found in image: {filename}")
        else:
            print(f"Skipping non-image file: {filename}")

# Run the function to rename images in the specified directory
image_directory = './images'
rename_images_in_directory(image_directory)
