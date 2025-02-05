import cv2
import mediapipe as mp
from plyer import notification
import math
import time
#--------------------------------------------------#
# Initialize MediaPipe Face Mesh                                                
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

mp_drawing = mp.solutions.drawing_utils

# Open the camera
cap = cv2.VideoCapture(0)

# Blink detection variables
blink_count = 0
blink_rate = 0
SUM_blink = 0
left_eye_closed = False
right_eye_closed = False

# Blink rate calculation variables
start_time = time.time()
run_time = 1

# Screen time variables
screen_start_time = None

elapsed_time = 0

show_blink = False

executed_once = True

True_cooldown = 0
cooldown = 0

cl_time = 0

sp_time = 0

All_time = 0

get_one_time_cooldown = True

Tired_eyes = False

cout_of_time = 0

No_makrks = False

After_cooldown = False

cout_of_time_20 = 1

face_is_true = False
hand_is_true = False

if_No_face_Yes_hand = False
some_time_No_face_Yes_hand = False
#--------------------------------------------------#

#INPUT---------------------------------------------#
alert_duration = 20 * 60 # in seconds
Time_cooldown = 20 # in seconds
Time_of_blink_rate = 10 # in seconds
EAR_THRESHOLD = 0.24
#INPUT---------------------------------------------#

# Function to calculate Euclidean distance between two points
def euclidean_distance(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

# Function to calculate EAR (Eye Aspect Ratio) for blink detection
def calculate_ear(landmarks, eye_indices):
    eye_top = euclidean_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    eye_bottom = euclidean_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    eye_width = euclidean_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    ear = (eye_top + eye_bottom) / (2.0 * eye_width)
    return ear

# Indices for left and right eyes
left_eye_indices = [362, 385, 387, 263, 373, 380]
right_eye_indices = [33, 160, 158, 133, 153, 144]

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Unable to read from camera.")
        break

    # Convert the image to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face landmarks
    resultface = face_mesh.process(frame_rgb)
    resultshands = hands.process(frame_rgb)

    # If faces are detected
    if resultface.multi_face_landmarks:
        face_is_true = True
        for face_landmarks in resultface.multi_face_landmarks:
            # Draw the landmarks and mesh
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1))

            # Calculate EAR for left and right eyes
            left_ear = calculate_ear(face_landmarks.landmark, left_eye_indices)
            right_ear = calculate_ear(face_landmarks.landmark, right_eye_indices)

            # Detect blinking
            if left_ear < EAR_THRESHOLD:
                if not left_eye_closed:
                    left_eye_closed = True
            else:
                if left_eye_closed:
                    blink_count += 1
                    SUM_blink += 1
                    left_eye_closed = False

            if right_ear < EAR_THRESHOLD:
                if not right_eye_closed:
                    right_eye_closed = True
            else:
                if right_eye_closed:
                    right_eye_closed = False

            # Calculate Blink Rate
            elapsed_time = time.time() - start_time
            #print("run_time : " + str(elapsed_time))
            if elapsed_time - (cout_of_time * 60) >= Time_of_blink_rate:  # If one minute has passed
                blink_rate = blink_count
                if blink_count < 10:
                    Tired_eyes = True
                blink_count = 0  # Reset blink count for next minute
                show_blink = True
                cout_of_time += 1
            elif elapsed_time >= 20 * 60 * cout_of_time_20:
                blink_count = 0  # Reset blink count for next minute
                Tired_eyes = True
                cout_of_time_20 += 1

            # Start screen timer
            if No_makrks == True or After_cooldown == True:
                start_time += int(cl_time)
                No_makrks = False
                After_cooldown = False
            All_time = time.time()
            if screen_start_time is None:
                screen_start_time = time.time()
            if True_cooldown > 0:
                sp_time = time.time() - screen_start_time
    else:
        face_is_true = False
        cooldown += sp_time
        sp_time = 0
        cl_time = time.time() - All_time
        No_makrks = True
        if True_cooldown > 0:
            screen_start_time = None

    if resultshands.multi_hand_landmarks:
        hand_is_true = True
        for hand_landmarks in resultshands.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=5))
            if face_is_true == False or True_cooldown > 0:
                if No_makrks == True or After_cooldown == True:
                    start_time += int(cl_time)
                    No_makrks = False
                    After_cooldown = False
                All_time = time.time()
                if screen_start_time is None:
                    screen_start_time = time.time()
                if True_cooldown > 0:
                    sp_time = time.time() - screen_start_time
    else:
        hand_is_true = False

    # Check if the user has been looking at the screen for too long
    if screen_start_time is not None and True_cooldown <= 0:
        time_on_screen = time.time() - screen_start_time - cl_time
        cv2.putText(frame, f'time: {int(elapsed_time // 60)} M {int(elapsed_time % 60)} S', (380, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Blink Count: {blink_count}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Blink Rate: {blink_rate}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if show_blink == True:
            cv2.putText(frame, f'Minute : {int(elapsed_time // 60)} Blink Count: {blink_rate}', (30, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if (time_on_screen >= alert_duration and executed_once == True) or Tired_eyes == True:
            executed_once = False
            notification.notify(
            title = "คําเตือน",
            message="ดูเหมือนคุณอยู่หน้าจอคอมมากเกินไปแล้ว พักประมาณ 20 วินาทีก่อน" ,
            app_name="CVS",
            )
            True_cooldown = Time_cooldown
            Tired_eyes = False
        elif time_on_screen < 1:
            executed_once = True
    elif True_cooldown > 0 or screen_start_time is None:
        cv2.putText(frame, f'cooldown {int(True_cooldown)}', (30, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if screen_start_time is None and True_cooldown > 0:
            if get_one_time_cooldown == True:
                cooldown = Time_cooldown + time.time()
                get_one_time_cooldown = False
            TimeCool = cooldown - time.time()
            True_cooldown = TimeCool
        elif True_cooldown < 0:
            get_one_time_cooldown = True
    else:
        After_cooldown = True
            
    # Display the processed image
    cv2.imshow('Computer vision syndrome', frame)

    # Press 'ecs' to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break
# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()