import random
import time

import psycopg2
import datetime

import requests

creat_table_query= """CREATE TABLE IF NOT EXISTS  events (
     id SERIAL PRIMARY KEY,
 timestamp TIMESTAMP NOT NULL,
 num_persons INTEGER NOT NULL,
 attention_score NUMERIC(4,2) NOT NULL
 );"""


# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="localhost", port="5432")

# Create a cursor object
cursor = conn.cursor()
cursor.execute("SELECT version();")
cursor.execute(creat_table_query)

creat_user_analytics_table_query = """CREATE TABLE IF NOT EXISTS  user_analytics (
     id SERIAL PRIMARY KEY,
 timestamp TIMESTAMP NOT NULL,
 dominant_gender TEXT,
 dominant_race TEXT,
 age TEXT
 );"""

cursor.execute(creat_user_analytics_table_query)
# Define the SQL query for inserting the event record

# Get the current timestamp

attention_score = 0.8
num_persons = 5
def add_event(attention_score, num_persons):
    cursor = conn.cursor()
    query = "INSERT INTO events (timestamp, num_persons, attention_score) VALUES (%s, %s, %s)"
    timestamp = datetime.datetime.now().utcnow()
    # Execute the SQL query with the timestamp, number of persons, and attention score as parameters
    cursor.execute(query, (timestamp, num_persons, attention_score))
    conn.commit()

# Close the cursor and connection
    cursor.close()
    try:
        requests.post("http://localhost:5000/sensor", json={"count": num_persons})
    except:
        print('error while posting to sensor')
        pass

def add_user_analytics_event(dominant_gender, dominant_race, age):
    cursor = conn.cursor()
    query = "INSERT INTO user_analytics (timestamp, dominant_gender, dominant_race, age) VALUES (%s, %s, %s, %s)"
    timestamp = datetime.datetime.now().utcnow()
    # Execute the SQL query with the timestamp, number of persons, and attention score as parameters
    cursor.execute(query, (timestamp, dominant_gender, dominant_race, age))
    conn.commit()
    cursor.close()

# conn.close()

# while True:
#     persons = random.randint(0,5)
#     add_event(attention_score, persons)
#     time.sleep(5*random.random())


from facenet_pytorch import MTCNN
import torch
import numpy as np
import mmcv, cv2
from PIL import Image, ImageDraw
from deepface import DeepFace

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))


mtcnn = MTCNN(keep_all=True, device=device)

cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0


while True:
    ret, frame = cam.read()
    frame_analysis = DeepFace.analyze(img_path=frame, enforce_detection=False, actions=("age", "gender", "race"),
                                      align=False)
    frame = Image.fromarray(frame)
    boxes, _ = mtcnn.detect(frame)

    # Draw faces
    frame_draw = frame.copy()
    draw = ImageDraw.Draw(frame_draw)
    attention_score=0
    if boxes is not None and boxes.shape[0]:
        i = 0
        for box in boxes:
            draw.rectangle(box.tolist(), outline=(255, 0, 0), width=6)
            if len(frame_analysis) > i:
                face_obj = frame_analysis[i]
                draw.text(xy=box.tolist(),
                          text="{}:{}:{}".format(face_obj['dominant_gender'], face_obj['dominant_race'], face_obj['age']))
        gender = list()
        race = list()
        age = list()
        for frame in frame_analysis:
            gender.append(frame['dominant_gender'])
            race.append(frame['dominant_race'])
            age.append(str(frame['age']))
        if len(gender) > 0:
            add_user_analytics_event(",".join(gender), ",".join(race), ",".join(age))

        add_event(attention_score, len(boxes))
    else:
        add_event(attention_score, 0)
    cv2.imshow("test",  np.asarray(frame_draw))
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()
