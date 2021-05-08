import requests,json,pyfiglet,time,sys
from alive_progress import alive_bar

ascii_banner = pyfiglet.figlet_format("CoWin Availability Tool")
print(ascii_banner)

date = sys.argv[1]

pincode = sys.argv[2]
                    
URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode="+pincode+"&date="+date
header = { 'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
r = requests.get(URL,headers=header)
jsonRes = r.json()

totalResults = len(jsonRes["centers"])

print("Processing {} Centers for next 7 Days Availability from {} :\n".format(totalResults,date))

center_list = []


def process_list(list):
	tmplist=[]
	for item in list:
		center_details = {"name":None,"address":None,"available_slot":None}
		center_details['name']=item['name']
		center_details['address']=item['address']
		center_details['available_slot'] = item['sessions'][0]['available_capacity']
		tmplist.append(center_details)
	return tmplist
	
center_list = process_list(jsonRes["centers"])

def printCentreDetails(centrelist):
	print("===============================================================================")
	print("Name                              Address                       Available Slots")
	print("===============================================================================")
	for x in centrelist:
		print("{:<10}".format(x['name'])+" "*7+"{:^}{:>10}".format(x['address'],x['available_slot']))		

printCentreDetails(center_list)

print("\n")
with alive_bar(totalResults, bar='blocks') as bar:
    for item in jsonRes["centers"]:               
        bar()
        time.sleep(0.1) 


minList=[]
availList18=[]

def get45List(jsonResponse):
	List=[]
	for centre in jsonResponse["centers"]:
		for key in centre:
			if key == "sessions":
				for session in centre.get(key):
					if session['min_age_limit'] == 45:
						List.append(session)
	return List				

def get18List(jsonResponse):
	List=[]
	for centre in jsonResponse["centers"]:
		for key in centre:
			if key == "sessions":
				for session in centre.get(key):
					if session['min_age_limit'] == 18:
						List.append(session)
	return List

def getAvailableSlotsfor18(jsonResponse):
	List=[]
	for centre in jsonResponse["centers"]:
		for key in centre:
			if key == "sessions":
				for session in centre.get(key):
					if session['min_age_limit'] == 18 and session['available_capacity'] > 0:
						List.append(centre)
	return List

def getAvailableSlotsfor45(jsonResponse):
	List=[]
	for centre in jsonResponse["centers"]:
		for key in centre:
			if key == "sessions":
				for session in centre.get(key):
					if session['min_age_limit'] == 45 and session['available_capacity'] > 0:
						List.append(centre)
	return List	

def printList(list):
	for i in minList:
    		print(i)

minList = get18List(jsonRes)

availList18 = getAvailableSlotsfor18(jsonRes)


if len(availList18) != 0:
	print("<=== All 18+ Vaccine Centre in Meerut ===> \n")
	printList(minList)
	
if len(availList18) == 0:
	oops_banner = pyfiglet.figlet_format("Oops !!\n")
	print(oops_banner)
	print(":( No Slots Available for 18+ Vaccination")
	print("\n")
else:
	print("\n Available Vaccination Centre's are => \n")
	resultList = []
	resultList = process_list(availList18)
	printCentreDetails(resultList)		
	print("\n\n")


