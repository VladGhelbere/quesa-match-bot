import os
import cv2
import numpy as np
import pyautogui
from PIL import Image
import time

# Function to capture the screenshot
def capture_screenshot(filename="current_screenshot.png"):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return cv2.imread(filename)

# Function to find an image on the screen
def find_image_on_screen(target_image_path, threshold=0.6):
    screenshot = capture_screenshot()
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    target_image = cv2.imread(target_image_path, 0)
    result = cv2.matchTemplate(gray_screenshot, target_image, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    points = list(zip(*locations[::-1]))
    
    return points

# Function to load card images from a folder
def load_card_images(card_images_folder):
    card_images = {}
    for filename in os.listdir(card_images_folder):
        if filename.endswith(".png"):  # Assuming the card images are in PNG format
            card_name = os.path.splitext(filename)[0]
            card_image = cv2.imread(os.path.join(card_images_folder, filename), 0)
            card_images[card_name] = card_image
    return card_images

def find_card_positions(screenshot, card_images, threshold=0.8, min_distance=10):
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    card_positions = {}

    for card_name, card_image in card_images.items():
        result = cv2.matchTemplate(gray_screenshot, card_image, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        filtered_positions = []

        for pt in zip(*locations[::-1]):
            # Check if the position is far enough from existing positions
            too_close = any(
                abs(pt[0] - fp[0]) < min_distance and abs(pt[1] - fp[1]) < min_distance
                for fp in filtered_positions
            )
            if not too_close:
                filtered_positions.append(pt)

        if filtered_positions:  # Only add non-empty positions to card_positions
            card_positions[card_name] = filtered_positions

    return card_positions

# Function to automate clicks on the card pairs
def click_pairs(card_positions):
    def click(x, y):
        pyautogui.moveTo(x, y)
        pyautogui.click()
    
    # Click on the pairs
    for card_name, positions in card_positions.items():
        if len(positions) < 2:
            continue
        # Ensure there are at least two positions to form a pair before clicking
        elif len(positions) >= 2:
            for i in range(0, len(positions), 2):
                if i + 1 < len(positions):
                    (x1, y1), (x2, y2) = positions[i], positions[i+1]
                    click(x1, y1)
                    time.sleep(0.1)  # Adjust the delay as needed
                    click(x2, y2)
                    time.sleep(0.2) # Adjust the delay as needed

# Main function to run the game bot
def main():
    start_image_path = "./start2.png"
    start2_image_path = "./match2.png"
    card_images_folder = "./cards"
    old_positions = []

    # Load card images
    card_images = load_card_images(card_images_folder)
    
    while True:
        # Check for the start image on the screen
        points = find_image_on_screen(start_image_path)
        if points:
            print("Start image found on screen. Proceeding with the game...")
            screenshot = capture_screenshot("game_screenshot.png")
            card_positions = find_card_positions(screenshot, card_images)
            print(card_positions)

            if len(old_positions) < len(card_positions):
                print("Finding best match...")
                old_positions = card_positions
            elif len(old_positions) > len(card_positions):
                print("Found best match")
                print(old_positions)
                points = find_image_on_screen(start2_image_path)
                if points:
                    click_pairs(old_positions)
                    old_positions = []
                else:
                    time.sleep(0.2)
            # break  # Remove break to continuously check and play
        time.sleep(4)  # Adjust the delay as needed

if __name__ == "__main__":
    main()
