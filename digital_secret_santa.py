import PySimpleGUI as sg
import pathlib
from PIL import Image, ImageTk
import io
import random
import time


FOLDER_PEOPLE = r"C:\Users\Baerwolff\Desktop\code\digital_secret_santa\people"
FOLDER_GIFTS = r"C:\Users\Baerwolff\Desktop\code\digital_secret_santa\gifts"
DICE_IMAGE_PATH = r"dice.jpg"
TRANSPARENT_IMAGE_PATH = r"transparent.png"
WHITE_IMAGE_PATH = r"white.png"
MAX_SIZE = 100
swap_1 = False
swap_2 = False


def all_file_paths_in_folder(folder_path):
    folder = pathlib.Path(folder_path)
    file_paths = []
    for file_path in folder.iterdir():
        file_paths.append(file_path)
    return file_paths


def get_img_data(f, maxsize=(MAX_SIZE, MAX_SIZE), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:  # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def roll_dice():
    score = random.randint(1, 6)
    return score


# Add your new theme colors and settings
sg.LOOK_AND_FEEL_TABLE["MyNewTheme"] = {
    "BACKGROUND": "white",
    "TEXT": "black",
    "INPUT": "#c7e78b",
    "TEXT_INPUT": "#000000",
    "SCROLL": "#c7e78b",
    "BUTTON": ("white", "#709053"),
    "PROGRESS": ("#01826B", "#D0D0D0"),
    "BORDER": 1,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
}


# Switch to use your newly created theme
sg.theme("MyNewTheme")


# empty lists
people_images_paths = []
gifts_images_paths = []
people_images = []
gifts_images = []
dice_images = []

people_images_paths = all_file_paths_in_folder(FOLDER_PEOPLE)
gifts_images_paths = all_file_paths_in_folder(FOLDER_GIFTS)


"""
# Elements: Folder browsing
dummy_people_path_input = sg.Input(
    key="dummy_people_path_input", visible=False, enable_events=True
)
dummy_gifts_path_input = sg.Input(
    key="dummy_gifts_path_input", visible=False, enable_events=True
)
browse_people_button = sg.FolderBrowse(
    button_text="Browse people",
    key="browse_people_button",
    target="dummy_people_path_input",
)
browse_gifts_button = sg.FolderBrowse(
    button_text="Browse gifts",
    key="browse_gifts_button",
    target="dummy_gifts_path_input",
)
"""


# Elements: Images

for i, people_image_path in enumerate(people_images_paths):
    people_image = sg.Image(
        data=get_img_data(people_image_path, first=True),
        key="people_image_" + str(i),
        enable_events=True,
    )
    people_images.append(people_image)
for j, gift_image_path in enumerate(gifts_images_paths):
    gift_image = sg.Image(
        data=get_img_data(gift_image_path, first=True),
        key="gift_image_" + str(j),
        enable_events=True,
    )
    gifts_images.append(gift_image)


# Elements: Roll the dice
starter = random.randint(1, len(people_images_paths))
for k in range(len(people_images_paths)):
    if k == starter - 1:
        dice_image_path = DICE_IMAGE_PATH
    else:
        dice_image_path = WHITE_IMAGE_PATH
    dice_image = sg.Image(
        data=get_img_data(dice_image_path, first=True),
        key="dice_image_" + str(k),
        enable_events=True,
    )
    dice_images.append(dice_image)
text_dice_score = sg.Text(
    "No score so far!",
    key="text_dice_score",
    enable_events=True,
    size=(250, 1),
    justification="left",
    font="Any 20",
)
button_roll_dice = sg.Button("Roll the dice!", key="button_roll_dice", font="Any 20")
button_perform = sg.Button("Perform action!", key="button_perform")

# Define layout
layout = [
    [*dice_images],
    [*people_images],
    [*gifts_images],
    [button_roll_dice, text_dice_score],
]

next = starter
perform = False

# Build Window
window = sg.Window("Digital Secret Santa", layout, size=(300, 200), resizable=True)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "dummy_people_path_input" and values["dummy_people_path_input"] != "":
        people_images_paths = all_file_paths_in_folder(
            values["dummy_people_path_input"]
        )
    elif event == "dummy_gifts_path_input" and values["dummy_gifts_path_input"] != "":
        gifts_images_paths = all_file_paths_in_folder(values["dummy_people_path_input"])
    elif swap_1 and event.startswith("gift_image_"):
        print("swap 1")
        key_1 = event
        swap_1 = False
        swap_2 = True
    elif swap_2 and event.startswith("gift_image_"):
        print("swap 2")
        key_2 = event
        key_1_nr = int(key_1[len("gift_image_") :])
        key_2_nr = int(key_2[len("gift_image_") :])
        gifts_images_paths[key_1_nr], gifts_images_paths[key_2_nr] = (
            gifts_images_paths[key_2_nr],
            gifts_images_paths[key_1_nr],
        )
        swap_2 = False
        perform = True
    elif not swap_1 and not swap_2 and event == "button_roll_dice":
        score = roll_dice()
        print(score)
        if score == 1:
            # No action
            window["text_dice_score"].update("A " + str(score) + " - No action!")
        elif score == 2:
            # Swap gifts with person of your choice
            swap_1 = True
            print("Swap gifts with person of your choice")
            window["text_dice_score"].update(
                str(score) + " - Swap gifts with person of your choice!"
            )
        elif score == 3:
            # Everyone passes gifts to the left
            gifts_images_paths = gifts_images_paths[1:] + [gifts_images_paths[0]]
            perform = True
            print("Everyone passes gifts to the left")
            window["text_dice_score"].update(
                str(score) + " - Everyone passes gifts to the left!"
            )
        elif score == 4:
            # Everyone passes gifts to the right
            gifts_images_paths = [gifts_images_paths[-1]] + gifts_images_paths[:-1]
            perform = True
            print("Everyone passes gifts to the right")
            window["text_dice_score"].update(
                str(score) + " - Everyone passes gifts to the right!"
            )
        elif score == 5:
            # The two people sitting next to you must swap their gifts
            swap_1 = True
            print("The two people sitting next to you must swap their gifts")
            window["text_dice_score"].update(
                str(score)
                + " - The two people sitting next to you must swap their gifts!"
            )
        elif score == 6:
            # Two people of your choice must swap their gifts
            swap_1 = True
            print("Two people of your choice must swap their gifts")
            window["text_dice_score"].update(
                str(score) + " - Two people of your choice must swap their gifts!"
            )
    if perform:
        time.sleep(1)
        for j, gift_image_path in enumerate(gifts_images_paths):
            window["gift_image_" + str(j)].update(
                data=get_img_data(gift_image_path, first=True)
            )
        if next < len(gifts_images_paths):
            next += 1
        else:
            next = 1
        for k in range(len(people_images_paths)):
            if k == next - 1:
                dice_image_path = DICE_IMAGE_PATH
            else:
                dice_image_path = WHITE_IMAGE_PATH
            window["dice_image_" + str(k)].update(
                data=get_img_data(dice_image_path, first=True)
            )
        perform = False

window.close()
