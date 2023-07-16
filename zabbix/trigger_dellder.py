#!/usr/bin/python3
# -*- coding: utf-8 -*-

### EXAMPLES ###
# python3 zbx_trigger_linker.py -Z http://192.168.56.200/zabbix -U Admin -P zabbix -R linker_rules.json

import json
import psycopg2
from pyzabbix import ZabbixAPI
import re
from argparse import ArgumentParser

class ZbxTriggerLinker:
	args = None
	rules = None
	zapi = None
	debug_mode = False

	# constructor
	def __init__(self, debug_mode=False):
		self.debug_mode = debug_mode
		parser = ArgumentParser()
		parser.add_argument('-Z', '--zabbix_api', default='', required=True)
		parser.add_argument('-U', '--user', default='', required=True)
		parser.add_argument('-P', '--password', default='', required=True)
		parser.add_argument('-R', '--rules_json', default='', required=True)
		self.args = parser.parse_args()

		# login to Zabbix
		self.zapi = ZabbixAPI(self.args.zabbix_api)
		self.zapi.login(self.args.user, self.args.password)
		# You can also authenticate using an API token instead of user/pass with Zabbix >= 5.4
		# zapi.login(api_token='xxxxx')
		self.debug_echo("Connected to Zabbix API Version %s" % self.zapi.api_version())

		# load linking rules
		# ATTETION: if match_groups are incorrect, some triggers may be lost!
		with open(self.args.rules_json, encoding='utf-8') as f:
			self.rules = json.load(f)
			self.debug_echo("Correlation rules:\n%s" % json.dumps(self.rules, indent=2))

		# envalid rules
		self.envalid_rules()

	# print only when debug mode enabled
	def debug_echo(self, *args, **kwargs):
		if self.debug_mode:
			print('[DBG]', *args, **kwargs)

	# envalid rules - raise KeyError if rules are invalid - TODO
	def envalid_rules(self):
		pass

	# get list of host groups which matches regular expression
	def get_group_by_regexp(self, group_regexp):
		pattern = re.compile(group_regexp)
		result = []
		for group in self.zapi.hostgroup.get(output=["name", "groupid"]):
			if pattern.match(group["name"]):
				result.append(group)
		return result

	# get list of hosts which matches regular expression
	def get_host_by_regexp(self, groups, host_regexp):
		pattern = re.compile(host_regexp)
		groupids = [groups[k] for k in groups]
		result = []
		for host in self.zapi.template.get(output=["name", "templateid"], groupids=groupids):
			if pattern.match(host["name"]):
				result.append(host)
		return result

	# get list of triggers which matches regular expression
	# extract their special unique IDs from description using match groups
	# and generate dict with pairs {"uniqueID": "triggerid"}
	def get_trigger_by_regexp(self, trigger_regexp, match_groups):
		pattern = re.compile(trigger_regexp)
		result = {}
		for trigger in self.zapi.trigger.get(output=["triggerid", "description", "status"], expandDescription=True):
			if pattern.match(trigger['description']) and int(trigger['status']) == 0: # check only enabled triggers!
				self.debug_echo("trigger matched: {}".format(trigger['description']))
				matches = pattern.search(trigger['description'])
				result["-".join([matches.group(grp) for grp in match_groups])] = trigger['triggerid']
		return result

	# create clone of trigger (without dependencies), return its triggerid and disable origin
	def clone_and_disable_trigger(self, triggerid):
		# get origin
		origin = self.zapi.trigger.get(triggerids=triggerid, output="extend", expandDescription=True, expandComment=True, expandExpression=True)[0]
		# change origin name
		origin['description'] += ' [cloned]'
		# disbale origin
		self.zapi.trigger.update(triggerid=int(triggerid), status=1)
		# remove read-only and empty keys from received trigger
		del origin['triggerid']
		del origin['value']
		del origin['lastchange']
		del origin['flags']
		del origin['error']
		del origin['state']
		del origin['templateid']
		for pole in ['url', 'uuid']:
			if origin[pole] == '':
				del origin[pole]
		# HOOK: specific for MKS: patch expression
		for s in ['expression', 'recovery_expression']:
			s1 = re.findall(r'\[.*?\]', origin[s])[0]
			log_path = re.findall(r'\".*?\"', s1)[0].replace('"', '')
			new_expr = origin[s].replace(log_path, '{$LOG_PATH}')
			origin[s] = new_expr
		# create clone
		return self.zapi.trigger.create(origin)['triggerids'][0]

	# debug function: print all triggers
	def get_trigger(self):
		trigger_list = self.zapi.trigger.get(output=["description"], expandDescription=True)
		for trigger in trigger_list:
			self.debug_echo("trigger: {}".format(trigger['description']))

	# desctructor
	def __del__(self):
		self.zapi.do_request('user.logout')

def main():
	# init Zabbix connection and load linker rules
	linker = ZbxTriggerLinker(debug_mode=True)

	# print all triggers if debug mode is enabled
	linker.get_trigger()

	# get pairs of "hardware unique ID" and triggerid from two trigger groups for linking
	pairs_a = linker.get_trigger_by_regexp(linker.rules['trigger_a']['trigger_selector']['expression'], linker.rules['trigger_a']['trigger_match_groups'])
	pairs_b = linker.get_trigger_by_regexp(linker.rules['trigger_b']['trigger_selector']['expression'], linker.rules['trigger_b']['trigger_match_groups'])
	linker.debug_echo(pairs_a, pairs_b, sep='\n')

	# export list of all triggers
	all_triggers = linker.zapi.trigger.get(output=['dependencies'], selectDependencies=['triggerid'])

	# make triggers from B dependent on triggers from A
	for uid in pairs_b:
		# if we're normal people without LLD we do this
		#linker.zapi.trigger.update(triggerid=int(pairs_b[uid]), dependencies=[{"triggerid": pairs_a[uid]}])
		#linker.debug_echo("Trigger {} made dependent on {}!".format(pairs_b[uid], pairs_a[uid]))

		# but we're IT workers with LLD so we do this
		# step 1: detect all matching triggers which are LLD, disable and clone them to no-LLD state
		origin_id = pairs_b[uid]
		if int(linker.zapi.trigger.get(triggerids=origin_id, output=['flags'])[0]['flags']) != 4:
			linker.debug_echo("Trigger {} is handmade, not LLD, skipping...".format(origin_id))
			continue
		try:
			clone_id = linker.clone_and_disable_trigger(origin_id)
		except Exception:
			linker.debug_echo("Trigger {} already cloned and done, skipping...".format(origin_id))
			continue

		# step 2: make cloned trigger dependent on trigger from A
		linker.zapi.trigger.update(triggerid=int(clone_id), dependencies=[{"triggerid": pairs_a[uid]}])
		linker.debug_echo("Trigger {} cloned from {} made dependent on {}!".format(clone_id, origin_id, pairs_a[uid]))

		# step 3: clone all modules dependent on origin and make clones dependent on clone
		for trigger in all_triggers:
			if trigger['dependencies'] and trigger['dependencies'][0]['triggerid'] == origin_id:
				module_clone_id = linker.clone_and_disable_trigger(trigger['triggerid'])
				linker.zapi.trigger.update(triggerid=int(module_clone_id), dependencies=[{"triggerid": clone_id}])
				linker.debug_echo("Trigger {} which is module of {} and cloned from {} made dependent on {}!".format(module_clone_id, origin_id, trigger['triggerid'], clone_id))
	return 0

if __name__ == "__main__":
	main()
