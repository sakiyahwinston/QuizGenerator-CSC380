import smtplib
from email.mime.text import MIMEText as mime
import random
from datetime import datetime, timedelta
import os
#import mysql.connector
#want to use https://www.w3schools.com/python/python_mysql_getstarted.asp as a reference

testaddress = 'quizbotverifier@gmail.com'
testpassword = 'xpbu jmcj xmmd gdpl'


EMAIL_ADDR = os.environ.get("EMAIL_ADDR", "quizbotverifier@gmail.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "xpbu jmcj xmmd gdpl")


def sendMessage(address, code):
    msg = mime(f"{code} is your verification code. If this was not you, ignore this email.", "plain")
    msg['Subject'] = "Verification Code"
    msg['From'] = EMAIL_ADDR
    msg['To'] = address

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDR, EMAIL_PASS)
    server.sendmail(EMAIL_ADDR, address, msg.as_string())
    server.quit()
def checkCode(ran,timer_End):
    code = input()
    if datetime.now() < timer_End:
        if code == ran:
            print("Thank you for verifying")
            return True
        elif code == 'quit':
            return False
        else:
            print('Incorrect code. Please enter your code again')
            checkCode(ran,timer_End)
    elif datetime.now() > timer_End:
        print("Code expired please try again")
        return False


def verifyEmail():
    print('Please enter your email address:')
    address = input()
    if address == 'quit': quit()
    else:
        ran = ''.join(random.sample([str(x) for x in range(10)], 4))  # makes a random 4 digit string
        timer_Start = datetime.now()
        timer_End = timer_Start + timedelta(minutes=3)
        sendMessage(address,ran)
        print('Please enter the code that was sent to your email address:')
        success = checkCode(ran,timer_End)
        if success:
            print('Login successful')
            # log in statement
        else:
            print('Login failed')
        quit()


