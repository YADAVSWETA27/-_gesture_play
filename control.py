import pyautogui

def press_key(key):
    print(f"[KEY PRESS] {key}")
    pyautogui.keyDown(key)

def release_key(key):
    print(f"[KEY RELEASE] {key}")
    pyautogui.keyUp(key)

def release_all_direction_keys():
    release_key("left")
    release_key("right")
