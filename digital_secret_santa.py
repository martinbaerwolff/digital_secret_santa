import PySimpleGUI as sg
import pathlib
from PIL import Image, ImageTk
import io
import random


FOLDER_PEOPLE = r"C:\Users\Baerwolff\Desktop\code\digital_secret_santa\people"
FOLDER_WRAPS = r"C:\Users\Baerwolff\Desktop\code\digital_secret_santa\wraps"
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
wraps_images_paths = []
gifts_images_paths = []
people_images = []
wraps_images = []
dice_images = []

people_images_paths = all_file_paths_in_folder(FOLDER_PEOPLE)
wraps_images_paths = all_file_paths_in_folder(FOLDER_WRAPS)
gifts_images_paths = all_file_paths_in_folder(FOLDER_GIFTS)
wrap_status = [False] * len(people_images_paths)

"""
# Elements: Folder browsing
dummy_people_path_input = sg.Input(
    key="dummy_people_path_input", visible=False, enable_events=True
)
dummy_wraps_path_input = sg.Input(
    key="dummy_wraps_path_input", visible=False, enable_events=True
)
browse_people_button = sg.FolderBrowse(
    button_text="Browse people",
    key="browse_people_button",
    target="dummy_people_path_input",
)
browse_wraps_button = sg.FolderBrowse(
    button_text="Browse wraps",
    key="browse_wraps_button",
    target="dummy_wraps_path_input",
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
for j, wrap_image_path in enumerate(wraps_images_paths):
    wrap_image = sg.Image(
        data=get_img_data(wrap_image_path, first=True),
        key="wrap_image_" + str(j),
        enable_events=True,
    )
    wraps_images.append(wrap_image)


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
button_change = sg.Button(
    "Lets change wraps!", key="change", font="Any 20", visible=False
)
dummy_text_1 = sg.Text()
dummy_text_2 = sg.Text()

# Define layout
layout = [
    [*dice_images],
    [*people_images],
    [*wraps_images],
    [dummy_text_1],
    [button_roll_dice],
    [text_dice_score],
    [dummy_text_2],
    [button_change],
]

next = starter
perform = False
game_state = "roll dice"

# Build Window
window = sg.Window("Digital Secret Santa", layout, size=(300, 200), resizable=True)

# Run event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "dummy_people_path_input" and values["dummy_people_path_input"] != "":
        people_images_paths = all_file_paths_in_folder(
            values["dummy_people_path_input"]
        )
    elif event == "dummy_wraps_path_input" and values["dummy_wraps_path_input"] != "":
        wraps_images_paths = all_file_paths_in_folder(values["dummy_people_path_input"])
    elif game_state == "swap part 1" and event.startswith("wrap_image_"):
        print("swap 1")
        key_1 = event
        game_state = "swap part 2"
    elif game_state == "swap part 2" and event.startswith("wrap_image_"):
        print("swap 2")
        key_2 = event
        key_1_nr = int(key_1[len("wrap_image_") :])
        key_2_nr = int(key_2[len("wrap_image_") :])
        wraps_images_paths[key_1_nr], wraps_images_paths[key_2_nr] = (
            wraps_images_paths[key_2_nr],
            wraps_images_paths[key_1_nr],
        )
        swap_2 = False
        game_state = "perform"
    elif game_state == "roll dice" and event == "button_roll_dice":
        score = roll_dice()
        print(score)
        if score == 1:
            # Unwrap gift in front of you (if not already done)
            print("Unwrap gift in front of you")
            window["text_dice_score"].update(
                str(score)
                + " - Unwrap gift in front of you (for yourself or anyone else; if not done yet)"
            )
            window["change"].update(
                "Unwrapped? Update image and next Player!", visible=True
            )
            print(str(gifts_images_paths[next - 1].resolve))
            if "gift" in str(gifts_images_paths[next - 1].resolve):
                wraps_images_paths[next - 1] = gifts_images_paths[next - 1]
            game_state = "wait for perform button"
        elif score == 2:
            # Swap wraps with person of your choice
            game_state = "swap part 1"
            print("Swap wraps with person of your choice")
            window["text_dice_score"].update(
                str(score) + " - Swap wraps with person of your choice!"
            )
        elif score == 3:
            # Everyone passes wraps to the left
            wraps_images_paths = wraps_images_paths[1:] + [wraps_images_paths[0]]
            game_state = "wait for perform button"
            print("Everyone passes wraps to the left")
            window["text_dice_score"].update(
                str(score) + " - Everyone passes wraps to the left!"
            )
            window["change"].update("Pass wraps to the left!", visible=True)
        elif score == 4:
            # Everyone passes wraps to the right
            wraps_images_paths = [wraps_images_paths[-1]] + wraps_images_paths[:-1]
            game_state = "wait for perform button"
            print("Everyone passes wraps to the right")
            window["text_dice_score"].update(
                str(score) + " - Everyone passes wraps to the right!"
            )
            window["change"].update("Pass wraps to the right!", visible=True)
        elif score == 5:
            # The two people sitting next to you must swap their wraps
            game_state = "swap part 1"
            print("The two people sitting next to you must swap their wraps")
            window["text_dice_score"].update(
                str(score)
                + " - The two people sitting next to you must swap their wraps!"
            )
        elif score == 6:
            # Two people of your choice must swap their wraps
            game_state = "swap part 1"
            print("Two people of your choice must swap their wraps")
            window["text_dice_score"].update(
                str(score) + " - Two people of your choice must swap their wraps!"
            )
    elif event == "change":
        game_state = "perform"
    if game_state == "perform":
        for j, wrap_image_path in enumerate(wraps_images_paths):
            window["wrap_image_" + str(j)].update(
                data=get_img_data(wrap_image_path, first=True)
            )
        if next < len(wraps_images_paths):
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
        window["change"].update("Currently no actions to perform!", visible=False)
        window["text_dice_score"].update("")
        game_state = "roll dice"

window.close()


# To Dos
# - Width of images should be forced to the same for all "columns"
# - auto full screen
# - folder browser as prequisite
# - currently folderfor gifts images has to have the name "gifts"