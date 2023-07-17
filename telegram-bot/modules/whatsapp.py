import requests
import json

class Master:
	def __init__(self, server):
		self.baseServer = server
		self.updateGroupList()

	def updateGroupList(self):
		self.groupList = {}
		tempList = requests.get(self.baseServer + '/user/my/groups').json()
		for group in tempList['results']['data']:
			self.groupList[group['Name']] = group['JID']

	def sendToGroup(self, groupName, message):
		# rise reliability
		requests.get(self.baseServer + '/app/reconnect')

		# foolproof
		if groupName not in self.groupList:
			print("You aren't member of specified group!")
			return False

		# form data for message request
		form_data = {
			'phone': self.groupList[groupName],
			'message': message
		}

		# send message!
		sendingReport = requests.post(self.baseServer + '/send/message', data=form_data).json()
		if 'code' not in sendingReport or sendingReport['code'] != 'SUCCESS':
			print('Something went wrong, saving debug data')
			debug = open('debug.log', 'w')
			json.dump(sendingReport, debug)
			debug.close()
			return False
		return True

sharer = None # to be initialized class

def shareToWhatsApp(msg, bot, **kwargs):
	global sharer
	if not sharer:
		sharer = Master('http://127.0.0.1:3000')

	msgLines = msg.text.splitlines()
	command = msgLines.pop(0)
	city = msgLines.pop(0).replace('ё', 'е')

	citiesGroupsFile = open('configs/groups.json', 'r')
	citiesGroups = json.load(citiesGroupsFile)
	resultMsg = '\n'.join(msgLines)
	citiesGroupsFile.close()

	if city not in citiesGroups:
		return False

	for group in citiesGroups[city]:
		print(group)
		sharer.sendToGroup(group, resultMsg)
		sleep(0.5)
	return True

def addNewGroup(msg, bot, **kwargs):
	global sharer
	if not sharer:
		sharer = Master('http://127.0.0.1:3000')

	jsonFileRead = open('configs/groups.json', 'r')
	groups = json.load(jsonFileRead)
	jsonFileRead.close()

	msgLines = msg.text.splitlines()
	command = msgLines.pop(0)
	city = msgLines.pop(0).replace('ё', 'е')
	group = msgLines.pop(0)

	if city not in groups:
		groups[city] = []
	if group not in groups[city]:
		groups[city].append(group)

	jsonFileWrite = open('configs/groups.json', 'w')
	json.dump(groups, jsonFileWrite)
	jsonFileWrite.close()
	return True

def deleteGroup(msg, bot, **kwargs):
	global sharer
	if not sharer:
		sharer = Master('http://127.0.0.1:3000')
	jsonFileRead = open('configs/groups.json', 'r')
	groups = json.load(jsonFileRead)
	jsonFileRead.close()

	msgLines = msg.text.splitlines()
	command = msgLines.pop(0)
	group = msgLines.pop(0)

	for city in groups:
		if group in groups[city]:
			groups[city].remove(group)
			break

	jsonFileWrite = open('configs/groups.json', 'w')
	json.dump(groups, jsonFileWrite)
	jsonFileWrite.close()
	return True

def patchSelenData(msg, bot, **kwargs):
	selenDataFile = open('.buller-data', 'w')

	msgLines = msg.text.splitlines()
	command = msgLines.pop(0)

	selenData = '\n'.join(msgLines)
	selenDataFile.write(selenData)
	selenDataFile.close()

	system('restarter')
	return True
