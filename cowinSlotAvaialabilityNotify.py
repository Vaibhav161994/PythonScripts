import requests
import pyfiglet
import time
import sys
import smtplib
from alive_progress import alive_bar
import urllib

#  Tool Banner
ascii_banner = pyfiglet.figlet_format("CoWin Availability Tool")
print(ascii_banner)

# Date from which you want to search
date = sys.argv[1]

# DistrictID for your District
dist_id = sys.argv[2]

# API URL
URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=" + \
    dist_id+"+&date="+date

# Sending Request to API
header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Cache-Control': 'no-cache'}
r = requests.get(URL, headers=header)

jsonRes = r.json()

# Total Centres
totalResults = len(jsonRes["centers"])


print("Processing {} Centers for next 7 Days Availability from {} :\n".format(
    totalResults, date))

center_list = []

# Convert List to CenterDetails Dictionary
def process_list(list):
    tmplist = []
    for item in list:
        center_details = {"name": None, "address": None, "available_slot": []}
        center_details['name'] = item['name']
        center_details['address'] = item['address']
        for session in item['sessions']:
            center_details['available_slot'].append(
                {"available_capacity": session['available_capacity'], "sdate": session['date']})
        tmplist.append(center_details)
    return tmplist

# Processed Center List
center_list = process_list(jsonRes["centers"])

# Pretty Print Center Details
def printCentreDetails(centrelist):
    print("===============================================================================")
    print("Name                              Address                       Available Slots")
    print("===============================================================================")
    for x in centrelist:
        if x['available_slot'] != []:
            for key, value in x['available_slot']:
                print("{:<10}".format(x['name'])+" " *
                      7+"{:^}".format(x['address']))
        else:
            print("{:<10}".format(x['name'])+" "*7 +
                  "{:^}{:>10}".format(x['address']))

# Printing All Center Details
printCentreDetails(center_list)

print("\n")

with alive_bar(totalResults, bar='blocks') as bar:
    for item in jsonRes["centers"]:
        bar()
        time.sleep(0.1)


minList = []
availList18 = []

# Get Centres for 45+ Vaccination
def get45List(jsonResponse):
    List = []
    for centre in jsonResponse["centers"]:
        for key in centre:
            if key == "sessions":
                for session in centre.get(key):
                    if session['min_age_limit'] == 45:
                        List.append(session)
    return List

# Get Centres for 18+ Vaccination 
def get18List(jsonResponse):
    List = []
    for centre in jsonResponse["centers"]:
        for key in centre:
            if key == "sessions":
                for session in centre.get(key):
                    if session['min_age_limit'] == 18:
                        List.append(session)
    return List

# Get Slot Availability for 18+ Vaccination
def getAvailableSlotsfor18(jsonResponse):
    List = []
    for centre in jsonResponse["centers"]:
        for key in centre:
            if key == "sessions":
                for session in centre.get(key):
                    if session['min_age_limit'] == 18 and session['available_capacity'] > 0:
                        List.append(centre)
    return List

# Get Slot Availability for 45+ Vaccination
def getAvailableSlotsfor45(jsonResponse):
    List = []
    for centre in jsonResponse["centers"]:
        for key in centre:
            if key == "sessions":
                for session in centre.get(key):
                    if session['min_age_limit'] == 45 and session['available_capacity'] > 0:
                        List.append(centre)
    return List

# Basic List Printing 
def printList(list):
    for i in minList:
        print(i)

#SendMail : In case You want to use Mail as notification Service
def sendmail(availList):
    # List of Reciever's Mail Address 
    li = ["test@testmail.com"]
    for dest in li:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        # Login to Gmail using sender's Email 
        s.login("sendersEmailAddress", "sendersPassword")
        listToStr = ' '.join(map(str, availList))
        message = "Available Slots are :"+listToStr
        # Sending Mail using sender's Email
        s.sendmail("sendersEmailAddress", dest, message)
        s.send
        s.quit()

#SendTelegramMessage : This is the method to use Telegram as your Notification Service
def sendTelegramMessage(text):
    telegramAPIUrl = "YOUR-TELEGRAM-API-URL" + \
        urllib.parse.quote(text)
    res = requests.post(telegramAPIUrl, headers=header)
    if res.status_code == 200:
        print("Successfully Sent : ", res.status_code)
    else:
        print("Unable to Send Telegram Message : ",res.status_code)

# Formating the Response for Telegram
def processMsgforTele(plist):
    teststr = ""
    for item in plist:
        teststr = teststr+item['name']+" \n"+item['address']
        if item['available_slot'] != []:
            for slot in item['available_slot']:
                if slot['available_capacity'] > 0:
                    teststr = teststr + " \nSlots_Avail ==> " + \
                        str(slot['available_capacity']) + \
                        " on " + str(slot['sdate']) + "\n"
    return teststr


minList = get18List(jsonRes)

availList18 = getAvailableSlotsfor18(jsonRes)


if len(availList18) != 0:
    print("\n<=== 18+ Vaccine Centre are Available ===> \n")

if len(availList18) == 0:
    oops_banner = pyfiglet.figlet_format("Oops !!\n")
    print(oops_banner)
    print(":( No Slots Available for 18+ Vaccination")
    print("\n")
else:
    print("\nSending Available Vaccination Centre's details on Telegram => \n\n")
    
    # sendmail(availList18)
    
    resultList = []
    # Processing the availabilityList for 18+
    resultList = process_list(availList18)
    # Sending Message to Telegram with proper Formatting
    sendTelegramMessage(processMsgforTele(resultList))
    
    print("\n\n")
