import pickle
import logging
import pandas as pd

SAVEFILE_NAME = "numbers.pkl"
WRITEFILE_NAME = "numbers.xlsx"

logger = logging.Logger("loader")

# Print welcome message for the user
print("Welcome to the pickle loader and CSV writer utility!")

# Reads list of tuples from numbers.pkl
logger.info("Reading from pickle...")
with open(SAVEFILE_NAME, "rb") as fhand:
    numbers = pickle.load(fhand)["dat"]

# sort the list
logger.info("Sorting...")
numbers.sort()

# convert the list to a Pandas DataFrame for easier writing
df = pd.DataFrame(numbers, columns=["ID", "Page"])

print(f"There are {len(numbers)} five-digit numbers detected")

# Writes dataframe into Excel file
logger.info("Writing to Excel...")
df.to_excel(WRITEFILE_NAME)

# with open(WRITEFILE_NAME, "w") as fhand:
#     # insert header
#     fhand.write("id,page\n")
#     # insert sorted data, row by row
#     for num, page in numbers:
#         fhand.write(f"{num},{page}\n")