import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pprint
import toml
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("image_path_str", type=str, help="URL of image to be processed")
# Add the '-point_list_name' flag
# The default parameter sets the default value if the flag is not specified.
parser.add_argument(
    "-point_list_name",
    type=str,
    default="points_to",
    help="Name of the list with measure points",
)

args = parser.parse_args()

local_file_path = args.image_path_str
point_list_name = args.point_list_name

pp = pprint.PrettyPrinter(indent=4)

# Open the TOML file
with open("config.toml", "r") as f:
    # Load the contents of the file into a dictionary
    config = toml.load(f)

image_path = Path(local_file_path)
assert image_path.exists()

points = []

img = cv2.imread(image_path.as_posix(), cv2.IMREAD_UNCHANGED)

location, street, time = image_path.stem.split("_")

print(f"{location=}, {street=}, {point_list_name=}")


# Step 3: Create a mouse callback function
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("X: ", x, "Y: ", y)
        points.append([x, y])
        # cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        # Set the length of each line of the cross.
        line_length = 5

        # Draw horizontal line of the cross
        cv2.line(
            img,
            (x - line_length, y - line_length),
            (x + line_length, y + line_length),
            (0, 0, 255),
            thickness=1,
        )

        # Draw vertical line of the cross
        cv2.line(
            img,
            (x - line_length, y + line_length),
            (x + line_length, y - line_length),
            (0, 0, 255),
            thickness=1,
        )
        cv2.imshow("image", img)


# Step 4: Create a window to display the image
cv2.namedWindow("image")

# Step 5: Set the mouse callback function to the window
cv2.setMouseCallback("image", mouse_callback)

# Step 6: Display the image in the window
cv2.imshow("image", img)

# Step 7: Wait for a key event
while True:
    if cv2.waitKey(0) & 0xFF == ord("q"):
        break

print(f"points {point_list_name}= ", end="")
pp.pprint(points)

if point_list_name in config[location][street].keys():
    prompt = "Array with name {point_list_name} already exists. Overwrite [y/n]?"
    while True:
        user_input = input(prompt).lower()
        if user_input in ["y", "yes"]:
            break
        elif user_input in ["n", "no"]:
            sys.exit()
        else:
            print("Please enter 'y' or 'n'.")


config[location][street][point_list_name] = points

with open("config.toml", "w") as f:
    # Write the dictionary to the file as TOML
    toml.dump(config, f)
# Step 8: Close all windows
cv2.destroyAllWindows()
