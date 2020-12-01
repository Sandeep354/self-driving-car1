# Here we will set the connection btw model and simulator

from flask import Flask # We will install 'flask' to create a web application
import socketio #to perform real-time communication btw client and server
import eventlet
from keras.models import load_model #to load the model.h5
import base64 #to decode the images
from io import BytesIO #to make a dummy image data so as to preprocess it further if necessary
from PIL import Image
import numpy as np
import cv2

sio = socketio.Server()

#initialize our application
app = Flask(__name__) #'__main__'
speed_limit = 10

# Copy paste the preprocessing function from colab
def img_preprocess(img):
  img = img[60:135, :, :]
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3, 3), 0)
  img = cv2.resize(img, (200, 66))
  img = img/255
  return img

@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed']) #instantaneous speed (conveyed by the simulator to us)
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    # Convert data(image) to array
    image = np.asarray(image)
    image = img_preprocess(image)
    # This return array of dim=3 but the model needs 4-dim array
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print ("{} {} {}".format(steering_angle, throttle, speed))
    # Now, send the steering angle to the simulator
    send_control(steering_angle, throttle)

# Event handler - @
@sio.on('connect')
def connect(sid, environ):
    print ('Connected')
    send_control(0, 0) #starting from 0 angle to drive straight

def send_control(steering_angle, throttle):
    sio.emit('steer', data = {
        'steering_angle' : steering_angle.__str__(),
        'throttle' : throttle.__str__()
    })

if __name__ == '__main__':

    model = load_model('model.h5')

    # app.run(port=3000) #app listen to any connection on port - 3000 (localhost:3000)
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
