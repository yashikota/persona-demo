import mmap

import cv2
import mediapipe as mp
import numpy as np

from pythonosc import udp_client

# osc
client = udp_client.SimpleUDPClient(address="127.0.0.1", port=5005)

# shared memory
name = "bgImage"
w = 640
h = 360
size = w * h * 4 # RGBA

# create shared memory
mem = mmap.mmap(-1, size, name)
data = np.frombuffer(mem, dtype=np.uint8).reshape(h, w, 4)

# mediapipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_holistic = mp.solutions.holistic

# webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("H", "2", "6", "4"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Empty frame")
        continue

    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    frame.flags.writeable = False

    inpaint_img = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    pose_img = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    hands_img = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    face_img = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    holistic_img = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)

    # selfie segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
        results = selfie_segmentation.process(frame)
        condition = np.stack(
            (results.segmentation_mask,) * 3, axis=-1) > 0.1
        mask = (results.segmentation_mask * 255).astype(np.uint8)

    # inpaint
    inpaint_img = cv2.inpaint(inpaint_img, mask, inpaintRadius=3, flags=cv2.INPAINT_NS)

    # pose
    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(pose_img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # hands
    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
        results = hands.process(frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(hands_img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # face mesh
    with mp_face_mesh.FaceMesh(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        results = face_mesh.process(frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(face_img, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

    # holistic
    with mp_holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        results = holistic.process(frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(holistic_img, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        if results.face_landmarks:
            mp_drawing.draw_landmarks(holistic_img, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(holistic_img, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(holistic_img, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    frame.flags.writeable = True
    cv2.imshow("original", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    cv2.imshow("inpaint", inpaint_img)
    cv2.imshow("pose", pose_img)
    cv2.imshow("hands", hands_img)
    cv2.imshow("face", face_img)
    cv2.imshow("holistic", holistic_img)

    # write to shared memory
    np.copyto(data, cv2.cvtColor(cv2.flip(inpaint_img, 0), cv2.COLOR_BGR2RGBA))

    # DEBUG: show shared memory image
    # cv2.imshow("shared memory", cv2.cvtColor(data, cv2.COLOR_RGBA2BGR))

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
