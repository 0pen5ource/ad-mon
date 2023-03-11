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
conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="192.168.64.2", port="5432")

# Create a cursor object
cursor = conn.cursor()
cursor.execute("SELECT version();")
cursor.execute(creat_table_query)

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
from IPython import display

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))


mtcnn = MTCNN(keep_all=True, device=device)

cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0


while True:
    ret, frame = cam.read()
    frame = Image.fromarray(frame)
    boxes, _ = mtcnn.detect(frame)

    # Draw faces
    frame_draw = frame.copy()
    draw = ImageDraw.Draw(frame_draw)
    attention_score=0
    if boxes is not None and boxes.shape[0]:
        for box in boxes:
            draw.rectangle(box.tolist(), outline=(255, 0, 0), width=6)
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
