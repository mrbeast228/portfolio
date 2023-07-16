import requests
import json
from argparse import ArgumentParser
from sys import argv

class Exporter:
	def __init__(self):
		# parse data from command line
		parser = ArgumentParser()

		parser.add_argument('-c', '--config', default='config.json', required=False) # config.json must have hostname, username, password and default header
		parser.add_argument('-t', '--template', default='', required=True) # zabbix template name
		parser.add_argument('--items') # filename for saving exported items from template
		parser.add_argument('--triggers') # filename for saving exported triggers from template
		parser.add_argument('--macros') # filename for saving exported macros from template
		self.args = parser.parse_args()

		# load data from JSON file to dictionary
		try:
			configfile = open(self.args.config, 'r')
			self.constants = json.load(configfile)
			configfile.close()
		except Exception as e:
			print('Cannot parse specified config file!\n')
			raise e from None

		# check connection to server
		try:
			self.zabbix_api_request(None, 'apiinfo.version', {})
		except Exception as e:
			print('Cannot get access to specified server:', self.constants['hostname'] + '\n')
			raise e from None

		# create auth data
		self.auth()

		# create default file names
		self.itemsFileName = 'items.csv' if self.args.items is None else self.args.items
		self.triggersFileName = 'triggers.csv' if self.args.triggers is None else self.args.triggers
		self.macrosFileName = 'macros.txt' if self.args.macros is None else self.args.macros

		# get required template ID
		self.get_template_id()

	def zabbix_api_request(self, token, method, params):
		# generic request to zabbix api with adjustable parameters
		url = 'http://' + self.constants['hostname'] + '/zabbix/api_jsonrpc.php'
		request = {
			'jsonrpc': '2.0',
			'method': method,
			'id': 1,
			'params': params
		}

		# sometimes we mustn't use auth token
		if token != None:
			request['auth'] = token

		# if server accesible but request incorrect - raise exception
		response = requests.post(url, headers=self.constants['headers'], json=request).json()
		if 'result' not in response:
			raise NameError('Cannot make this request to API: error code ' +
					str(response['error']['code']) + '. ' + response['error']['message']
					+ ' ' + response['error']['data'])
		return response['result']

	def auth(self):
		# get authentication token by
		params = {
			'user': self.constants['username'],
			'password': self.constants['password']
		}
		self.token = self.zabbix_api_request(None, 'user.login', params)

	def get_template_id(self):
		# store template ID in class object using template name from configuration
		params = {
			'output': ['templateid'],
			'filter': {
				'name': [self.args.template]
			}
		}
		self.templateIds = self.zabbix_api_request(self.token, 'template.get', params)

	def export_zabbix_template(self):
		# check if template exists
		if len(self.templateIds) == 0:
		        raise NameError("Specified template doesn't exist!")

		# export template configuration by template ID
		zabbix_request_params = {
			'options': {
				'templates': [self.templateIds[0]['templateid']]
			},
			'format': 'json'
		}
		self.template = json.loads(self.zabbix_api_request(self.token, 'configuration.export', zabbix_request_params))['zabbix_export']

	def debug_save_template_as_json(self, jsonFileName):
		# we can save Zabbix response in JSON format to debug if something would went wrong
		output = open(jsonFileName, 'w')
		json.dump(self.template, output)
		output.close()

	def save_template_to_csv(self):
		# save items if exist
		with open(self.itemsFileName, 'w') as output:
			print('Name,Key,Interval,Type,Tags,LLD,Discovery', file=output)
			self.parselist1 = []
			self.parselist2 = []
			if 'items' in self.template['templates'][0]:
				self.parselist1.extend(self.template['templates'][0]['items'])
			if 'discovery_rules' in self.template['templates'][0]:
				for rule in self.template['templates'][0]['discovery_rules']:
					if 'item_prototypes' in rule:
						self.parselist2.extend(rule['item_prototypes'])

			for item in self.parselist1 + self.parselist2:
				self.lld = 'False,'
				if 'discovery_rules' in self.template['templates'][0]:
					for rule in self.template['templates'][0]['discovery_rules']:
						if item['key'] == rule['master_item']['key'] or item in self.parselist2:
							self.lld = 'True,' + rule['name']

				print(item['name'], '"' + item['key'].replace('"', '""') + '"',
					  '1m' if 'delay' not in item else item['delay'],
					  'ZABBIX' if 'type' not in item else item['type'],
					  '' if 'tags' not in item else item['tags'],
					  self.lld, sep=',', file=output)

		# save triggers if exist
		with open(self.triggersFileName, 'w') as output:
			print('Severity,Name,Expression,LLD,Discovery', file=output)
			if 'triggers' in self.template:
				for t in self.template['triggers']:
					print(t['priority'].capitalize(), t['name'], '"' + t['expression'].replace('\r\n', ' ').replace('"', '""') + '"',
					      'False,', sep=',', file=output)
			for item in self.parselist1 + self.parselist2:
				self.lld = 'False,'
				if 'discovery_rules' in self.template['templates'][0]:
					for rule in self.template['templates'][0]['discovery_rules']:
						if item['key'] == rule['master_item']['key'] or item in self.parselist2:
							self.lld = 'True,' + rule['name']

				for k in ['triggers', 'trigger_prototypes']:
					if k in item:
						for t in item[k]:
							print(t['priority'].capitalize(), t['name'], '"' + t['expression'].replace('\r\n', ' ').replace('"', '""') + '"',
							      self.lld, sep=',', file=output)
		# save macros if exist
		with open(self.macrosFileName, 'w') as output:
			print('Name,Value', file=output)
			if 'macros' in self.template['templates'][0]:
				for macro in self.template['templates'][0]['macros']:
					print(macro['macro'], '' if 'value' not in macro else macro['value'].replace('"', '""'), sep=',', file=output)

if __name__ == "__main__":
	exporter = Exporter()
	exporter.export_zabbix_template()
	exporter.save_template_to_csv()
