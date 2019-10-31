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

def send_report_complete_email(user, story, report_uid):
    
    msg = Message('Fluency Box Report Complete',
                  sender=('Fluency Box', 'fluencybox19@gmail.com'),
                  recipients=[user.email_address])
    msg.body = f'''Dear {user.first_name}, 
    
    We have completed our analysis of the story you completed ({ story.name }).
    Kindly log into your Fluency Box account to view your report.
   
'''
    mail.send(msg)

