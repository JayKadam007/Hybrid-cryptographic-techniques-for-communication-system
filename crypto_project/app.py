from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import pymysql.cursors
import random
import string
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Define the global dictionary
room_keywords = {}

# Connect to the database
try:
    connection = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        db=os.environ.get('DB_NAME'),
        port=int(os.environ.get('DB_PORT')),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        connect_timeout=5
    )
    print("Connected to the database")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    exit()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_mail')
def send_mail(data):
    room=data['room']
    email=data['email']
    # Set up the SMTP server details
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587  # TLS Port
    # Email account details
    sender_email = 'prathamesh4141lohakare@gmail.com'
    sender_password = 'hmlwxzaptyngddjh'
    # Recipient email details
    recipient_email = email
    # Create a multipart message container
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'This Email Send By Your Friend'
    # Add body to the email
    body = 'Room Id :- '+room
    message.attach(MIMEText(body, 'plain'))
    try:
        # Create a secure TLS connection with the SMTP server
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        # Login to the email account
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print('Error: Unable to send email.')
        print(e)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    # Check if the room exists in the dictionary
    if room in room_keywords:
        # Use the existing keyword
        keyword = room_keywords[room]['keyword']
        # Add the user to the list of users for that room
        room_keywords[room]['users'].append(username)
        print(f"Room found. Using existing keyword: {keyword}")
    else:
        # Generate a new keyword
        length = 12
        characters = string.ascii_letters
        random_string = ''.join(random.choice(characters) for i in range(length))
        keyword = random_string
        # Store the new keyword and the user in the dictionary
        room_keywords[room] = {'keyword': keyword, 'users': [username]}
        print(f"Room not found. Generated keyword: {keyword}")
    join_room(room)
    emit('join_room', {'username': username, 'room': room, 'keyword': keyword}, room=room)



@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    print(username)
    if room in room_keywords and 'users' in room_keywords[room] and username in room_keywords[room]['users']:
        # Remove the user from the list of users for the room
        room_keywords[room]['users'].remove(username)
        # If there are no more users in the room, delete the room from the dictionary
        if not room_keywords[room]['users']:
            del room_keywords[room]
    leave_room(room)
    emit('leave_room', {'username': username, 'room': room}, room=room)



@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    room = data.get('room')
    message = data.get('message')
    dateString = data.get('dateString')
    timeString = data.get('timeString')
    message_key = data.get('key')

    with connection.cursor() as cursor:
        try:
            sql = "INSERT INTO records (username, room, message, dateString, timeString, message_key) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, room, message, dateString, timeString, message_key))
            connection.commit()
        except Exception as e:
            print(f"Failed to insert message into the database: {e}")
    emit('message', {'username': username, 'message': message, 'timeString': timeString, 'key': message_key}, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=os.environ.get('SERVICE_PORT'), debug=False)
