import smtplib
from email.mime.text import MIMEText as mime
import random
from datetime import datetime, timedelta
#import mysql.connector
#want to use https://www.w3schools.com/python/python_mysql_getstarted.asp as a reference

testaddress = 'quizbotverifier@gmail.com'
testpassword = 'xpbu jmcj xmmd gdpl'

def sendMessage(address,ran):
    try:
        msg = mime(ran + " Is your varification code. If this is not for you, then we sincerely apologise!", 'plain')
        msg['Subject'] = "Verification Code" #header
        msg['From'] = testaddress #where the email is sent from
        msg['To'] = address #where the email is going
        server = smtplib.SMTP('smtp.gmail.com', 587) #what service the program will use, in this case it is gmail
        server.starttls() #starts the email process
        server.login(testaddress, testpassword) #logs in to my personal email using an app password located on my laptop
        server.sendmail(testaddress, address, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        #Errors when login fails (should never be thrown but if it happens then this exists)
        print('Authentication error')
        quit()
    except smtplib.SMTPRecipientsRefused:
        #Errors when the address receiving the message is no good
        print('Recipient refused')
        quit()
    except smtplib.SMTPSenderRefused:
        print('Sender refused')
        #Errors when the address sending the message is no good (should also never be thrown, but you know)
        quit()

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
