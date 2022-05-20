from tracemalloc import start
import requests
import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import time

if os.getenv('TIME_REQUIREMENT') is not None:
    time_requirement = os.environ['TIME_REQUIREMENT']
else: 
    time_requirement = False

if os.getenv('CHECK_ONLY') is not None:
    check_only = os.environ['CHECK_ONLY']
else: 
    check_only = False
   
appointment_created = False

def send_email(message):
    msg = MIMEText(message)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = os.environ['EMAIL_ADDRESS_SUBJECT']
    msg['From'] = os.environ['EMAIL_ADDRESS_FROM']
    msg['To'] = os.environ['EMAIL_ADDRESS_TO']

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    try:
        s = smtplib.SMTP_SSL(
            os.environ['EMAIL_SMTP_SERVER'], os.environ['EMAIL_SERVER_PORT'])
        s.login(os.environ['EMAIL_ADDRESS_FROM'], os.environ['EMAIL_PASSWORD'])
        s.sendmail(os.environ['EMAIL_ADDRESS_FROM'], [
                   os.environ['EMAIL_ADDRESS_TO']], msg.as_string())
        s.quit()
        print("Successfully sent email")
    except smtplib.SMTPResponseException:
        print(smtplib.SMTPResponseException.smtp_error)


def create_appointment(date, startTime, endTime, key):
    
    
    json_result = {}
    
    bookable_slot = {"key": key, "date": date, "startTime":startTime, "endTime": endTime, "parts":1, "booked": False}
    appointment = {"productKey": "DOC", "date": date, "startTime":startTime, "endTime": endTime, "email": os.environ['EMAIL_ADDRESS_TO'], "phone": os.environ['PHONE_NUMBER'], "language":"nl" }
    customers = [{"vNumber": os.environ['USER_VNUMBER'], "firstName": os.environ['USER_FIRST_NAME'], "lastName": os.environ['USER_LAST_NAME']}]
    
    response = requests.post('https://oap.ind.nl/oap/api/desks/' + os.getenv('IND_LOCATION') + '/slots/' + key, json=bookable_slot)
    json_result['bookableSlot'] = bookable_slot
    appointment['customers'] = customers
    json_result['appointment'] = appointment

    response = requests.post('https://oap.ind.nl/oap/api/desks/DB/appointments/', json=json_result)

    if (response.status_code == 200):
        response = response.text.replace(")]}',", "")
        response_for_email = json.loads(response)
        send_email("An appointment has been created. \n\nDate: " + date_option['date'] + '. \nTime: ' + date_option['startTime'] + '. \nCancellation URL: https://oap.ind.nl/oap/nl/#/cancel/' + response_for_email['data']['key'] +'. \nAppointment Code: ' + response_for_email['data']['code'])
        print("Successfully created an appointment")

while appointment_created is False:
    
    r = requests.get(
        'https://oap.ind.nl/oap/api/desks/' + os.getenv('IND_LOCATION') + '/slots/?productKey=' + os.getenv('IND_APPOINTMENT_TYPE') + '&persons=1')
    response = r.text.replace(")]}',", "")
    result = json.loads(response)

    #Loop through the retrieved dates
    for date_option in result['data']:

        # get all the data coming back from the server
        first_date_option_str = date_option['date'] + \
            " " + date_option['startTime']
        first_date_option_obj = datetime.strptime(
            first_date_option_str, '%Y-%m-%d %H:%M')
        first_date_option_obj_month = first_date_option_obj.month
        
        # check for any requirements, if nothing, just continue
        if (time_requirement):
            # do the check here, this below should be dynamic TODO
            if(first_date_option_obj_month == 5 or first_date_option_obj_month == 6):
                # then send email
                if(check_only): 
                    send_email('There is a slot: ' + first_date_option_str)
                else:
                    create_appointment(date_option['date'], date_option['startTime'], date_option['endTime'], date_option['key'])
                    appointment_created = True
                break
        else:
            #create the appointment directly once we get the first date available
            appointment_created = False 
    time.sleep(60)

print("Appointment has been created, the job is done.")

    
