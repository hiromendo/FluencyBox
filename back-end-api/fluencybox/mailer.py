from flask import url_for

from flask_mail import Message
from fluencybox import app, mail
from fluencybox.models import User

#Sending email for reseting the password
def send_reset_email(user):
    token = user.get_reset_token()
    
    msg = Message('Fluency Box Password Reset Request',
                  sender=('Fluency Box', 'fluencybox19@gmail.com'),
                  recipients=[user.email_address])
    msg.body = f'''We have received a password reset request for your Fluency Box account.
To reset your password, please visit the below link:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
