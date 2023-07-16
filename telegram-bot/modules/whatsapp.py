import requests
import json

class Sharer:
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

