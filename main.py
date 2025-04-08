import cv2
import pyautogui
import pyttsx3
from gesture_utils import HandDetector
from control import press_key, release_key, release_all_direction_keys

dragging = False  # Global drag flag

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def main():
    global dragging

    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    prev_action = {"gesture": "", "direction": ""}

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = detector.find_hands(frame)
        lm_list = detector.find_position(frame)

        gesture = "None"
        direction = "none"

        if lm_list:
            fingers = detector.fingers_up(lm_list)
            frame_width = frame.shape[1]
            direction = detector.get_hand_position(lm_list, frame_width)

            print("Finger States:", fingers)

            # === Cursor Control ===
            if fingers == [0, 1, 0, 0, 0]:  # Only index finger
                index_tip = detector.get_index_finger_tip(lm_list)
                if index_tip:
                    screen_w, screen_h = pyautogui.size()
                    frame_h, frame_w, _ = frame.shape
                    x = int(index_tip[0] / frame_w * screen_w)
                    y = int(index_tip[1] / frame_h * screen_h)
                    pyautogui.moveTo(x, y)
                    gesture = "Cursor Move"

                    # Dragging logic
                    if detector.is_drag(lm_list):
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                            speak("Dragging started")
                            print("[MOUSE] Drag Start")
                    else:
                        if dragging:
                            pyautogui.mouseUp()
                            dragging = False
                            speak("Dragging ended")
                            print("[MOUSE] Drag End")

            # === Left Click ===
            elif detector.is_pinch(lm_list):
                pyautogui.click()
                gesture = "Left Click"
                speak("Left click")
                print("[MOUSE] Left Click")

            # === Right Click ===
            elif detector.is_right_click(lm_list):
                pyautogui.rightClick()
                gesture = "Right Click"
                speak("Right click")
                print("[MOUSE] Right Click")

            # === Game Gesture Controls ===
            elif fingers == [1, 1, 1, 1, 1]:
                gesture = "Open Hand - Accelerate"
                if gesture != prev_action["gesture"]:
                    press_key("up")
                    release_key("down")
                    speak("Accelerating")
                    prev_action["gesture"] = gesture
                    print("[ACTION] Accelerating")

            elif fingers.count(1) <= 1:
                gesture = "Fist - Brake"
                if gesture != prev_action["gesture"]:
                    release_key("up")
                    press_key("down")
                    speak("Braking")
                    prev_action["gesture"] = gesture
                    print("[ACTION] Braking")

            else:
                gesture = "Other"
                if gesture != prev_action["gesture"]:
                    release_key("up")
                    release_key("down")
                    prev_action["gesture"] = gesture
                    print("[ACTION] Idle")

            # === Directional Controls ===
            if direction != prev_action["direction"]:
                release_all_direction_keys()
                if direction == "left":
                    press_key("left")
                    speak("Turning left")
                    print("[DIRECTION] Turning Left")
                elif direction == "right":
                    press_key("right")
                    speak("Turning right")
                    print("[DIRECTION] Turning Right")
                prev_action["direction"] = direction

            # Display Info
            cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Direction: {direction}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False
                speak("Drag cancelled")
                print("[MOUSE] Drag Cancelled")

        cv2.imshow("GesturePlay", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Cleanup
    release_key("up")
    release_key("down")
    release_all_direction_keys()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
