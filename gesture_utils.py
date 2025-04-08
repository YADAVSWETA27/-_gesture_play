import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7):
        self.max_hands = max_hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=self.max_hands,
            min_detection_confidence=detection_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return img

    def find_position(self, img, hand_no=0):
        lm_list = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(hand.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
        return lm_list

    def fingers_up(self, lm_list):
        if not lm_list:
            return []

        fingers = []

        # Thumb
        fingers.append(1 if lm_list[4][1] > lm_list[3][1] else 0)

        # Other fingers
        tips = [8, 12, 16, 20]
        pip_joints = [6, 10, 14, 18]

        for tip, pip in zip(tips, pip_joints):
            if lm_list[tip][2] < lm_list[pip][2] - 10:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def get_hand_position(self, lm_list, frame_width):
        if not lm_list:
            return "none"

        cx = lm_list[9][1]
        if cx < frame_width // 3:
            return "left"
        elif cx > 2 * frame_width // 3:
            return "right"
        else:
            return "center"

    def get_index_finger_tip(self, lm_list):
        if len(lm_list) >= 9:
            return lm_list[8][1], lm_list[8][2]  # x, y of index fingertip
        return None

    def is_pinch(self, lm_list, threshold=40):
        """Detect pinch gesture (index tip close to thumb tip)."""
        if len(lm_list) < 9:
            return False
        x1, y1 = lm_list[4][1], lm_list[4][2]   # Thumb tip
        x2, y2 = lm_list[8][1], lm_list[8][2]   # Index tip
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance < threshold

    def is_right_click(self, lm_list, threshold=40):
        """Detect right-click gesture (thumb tip + pinky tip)."""
        if len(lm_list) < 21:
            return False
        x1, y1 = lm_list[4][1], lm_list[4][2]   # Thumb tip
        x2, y2 = lm_list[20][1], lm_list[20][2] # Pinky tip
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance < threshold

    def is_drag(self, lm_list, threshold=40):
        """Detect drag gesture: pinch maintained (same as is_pinch)."""
        return self.is_pinch(lm_list, threshold)
