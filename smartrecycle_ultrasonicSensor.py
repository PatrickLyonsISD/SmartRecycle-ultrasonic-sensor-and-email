import firebase_admin
from firebase_admin import credentials, db
import RPi.GPIO as GPIO
import time
import argparse
import smtplib
from email.message import EmailMessage

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 4
GPIO_ECHO = 17
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Firebase Admin Initialization
cred = credentials.Certificate('/home/patrick/tflite1/smartrecycle-a0d95-firebase-adminsdk-40ju5-4382d2b40e.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartrecycle-a0d95-default-rtdb.firebaseio.com'
})

def measure_distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start_time = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
    elapsed = stop_time - start_time
    distance = (elapsed * 34300) / 2
    return distance

def send_email(to_email):
    """Send an email notification."""
    msg = EmailMessage()
    msg.set_content("Bin is full please use smart recycle app to update bin status.")
    msg['From'] = 'patricklyonslit@gmail.com'
    msg['To'] = to_email
    msg['Subject'] = 'Bin Full Notification'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('patricklyonslit@gmail.com', 'tuap sqff whyb pcjh')
        server.send_message(msg)
        print('Email sent to', to_email)

def update_database(object_name):
    ref = db.reference('objects/' + object_name)
    current_count = ref.get()
    if current_count is None:
        current_count = 0
    ref.set(current_count + 1)
    print(f"Updated database for {object_name} to count {current_count + 1}")
    time.sleep(2.5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('object_name', help="The name of the object detected")
    args = parser.parse_args()

    full_start_time = None
    notification_threshold = 10  

    try:
        while True:
            distance = measure_distance()
            print(f"Measured Distance = {distance:.1f} cm")
            if distance < 2.5:
                if full_start_time is None:
                    full_start_time = time.time()
                elif time.time() - full_start_time > notification_threshold:
                    send_email('patricklyonsit1gti@gmail.com')
                    full_start_time = None  # Reset timer after sending email
            else:
                full_start_time = None  # Reset timer if condition is not met
            
            if distance < 10:
                update_database(args.object_name)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

