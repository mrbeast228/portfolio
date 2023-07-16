# WARNING: this isn't independent module, it must be used only from bot!
import json
from time import sleep
from os import system

def shareToWhatsApp(msg, bot, **kwargs):
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
