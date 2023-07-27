import os
import re
from glob import glob
import openai
from pandas import DataFrame
from concurrent.futures import ThreadPoolExecutor as TP
from sys import argv
from json import load
import xml.etree.ElementTree as ET
from wheel_inspect import inspect_wheel

openai.api_key = 'OPENAI GPT TOKEN HERE'
cache_dir_path = "RELATIVE PATH TO PACKAGES FOLDER"
path_to_append = 'Кеши для сборки/БЛА БЛА БЛА/' # with ending slash!!!
pkgType = 'CLASS PER TYPE - ON OF CLASSES NAME'

def find_contains(pattern, path, typ='files'):
	result = []
	for root, dirs, files in os.walk(path):
		for file in locals()[typ]:
			if pattern in file:
				result.append(os.path.join(root, file))
	return result

def jsonToDict(jsonPath):
	try:
		return load(open(jsonPath))
	except Exception:
		return {}

def isIterable(object):
	try:
		return bool(list(iter(object)))
	except Exception:
		return False

def xmlIterExtractor(object):
	if isIterable(object):
		result = []
		for k in object:
			result.extend(xmlIterExtractor(k))
		return result
	return [object]

def getTagData(elemList, tag):
	for elem in elemList:
		if elem.tag.endswith(tag):
			return elem.text
	return ""

def parse_from_gpt(pkgName, pkgType=''):
	prompt = f"предоставь техническое описание {pkgType} пакета {pkgName}"
	try:
		resp_txt = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=[
				{"role": "user", "content": prompt}
			]
		).choices[0].message.content
		return resp_txt
	except Exception:
	   return parse_from_gpt(pkgName, pkgType) # HOOK: if server overloaded, re-prompt it

class maven:
	pkg_file_list = [y for x in os.walk(cache_dir_path) for y in glob(os.path.join(x[0], '*.pom'))]
	def describer(self, pkg_file):
		pkg_version_dir = os.path.dirname(pkg_file)
		pkg_dir = os.path.dirname(pkg_version_dir)

		pkg_version = os.path.basename(pkg_version_dir)
		pkg_name = os.path.basename(os.path.dirname(pkg_version_dir))
		pkg_legacy_descr = "" # maven has no normal descriptions
		pkg_gpt_descr = parse_from_gpt(pkg_name, 'maven')

		return [path_to_append + pkg_dir, pkg_version, pkg_name, pkg_legacy_descr, pkg_gpt_descr]

class yarn:
	pkg_file_list = glob(os.path.join(cache_dir_path, 'cache/*.zip')) + glob(os.path.join(cache_dir_path, 'unplugged/*'))
	def describer(self, pkgFile):
		try:
			pkgData = os.path.basename(pkgFile).split('.zip')[0].split('-')

			pkgVerArr = []
			while not '.' in pkgData[-1] and len(pkgData[-1]) == 10: # detect commit hashes
				pkgVerArr.append(pkgData.pop())
			if '.' in pkgData[-1]: # it is version
				pkgVer = pkgData.pop()
			else: # it's not version
				pkgVer = '-'.join(pkgVerArr[::-1])

			if pkgData[-1] == 'npm':
				pkgData.pop()

			pkgName = '-'.join(pkgData)
			pkgDescr = '' # yarn descriptions are inside archived node packages
			pkgGptDescr = parse_from_gpt(pkgName, 'npm')
			return [path_to_append + pkgFile, pkgVer, pkgName, pkgDescr, pkgGptDescr]
		except Exception:
			return [path_to_append + pkgFile, '', '', '', '', '']

class npm:
	pkg_file_list = [f for f in find_contains('package.json', cache_dir_path) if 'version' in jsonToDict(f)] # load only main packages, not sub-packages
	def describer(self, pkgFile):
		JSON = jsonToDict(pkgFile)
		pkgPath = os.path.dirname(pkgFile)
		return [path_to_append + pkgPath, JSON['version'], JSON['name'], "" if 'description' not in JSON else JSON['description'], parse_from_gpt(JSON['name'], 'npm')]

class yarn6:
	pkg_file_list = glob(os.path.join(cache_dir_path, 'v6/*/node_modules/*/package.json'))
	def describer(self, pkgFile):
		return npm.describer(npm, pkgFile)

class go:
	pkg_file_list = [d for d in find_contains('@v', cache_dir_path, 'dirs') if not d.startswith('@v') and not 'go/pkg/mod/cache' in d and '@v' in os.path.basename(d)]
	def describer(self, pkgFile):
		rawName = os.path.basename(pkgFile).split('@v')
		if re.match('^v[0-9].*', rawName[0]):
			pkgName = os.path.basename(os.path.dirname(pkgFile))
		elif not '.' in os.path.basename(os.path.dirname(pkgFile)):
			pkgName = os.path.basename(os.path.dirname(pkgFile)) + '/' + rawName[0]
		else:
			pkgName = rawName[0]
		return [path_to_append + pkgFile, rawName[1], pkgName, "", parse_from_gpt(pkgName, 'golang')]

class nuget:
	pkg_file_list = find_contains('.nuspec', cache_dir_path)
	def describer(self, pkgFile):
		tagList = xmlIterExtractor(ET.parse(pkgFile).getroot())
		pkgName = getTagData(tagList, 'title')
		pkgVer = getTagData(tagList, 'version')
		return [path_to_append + os.path.dirname(pkgFile), pkgVer, pkgName if pkgName else getTagData(tagList, 'id'), getTagData(tagList, 'description'), parse_from_gpt(pkgName, 'nuget')]

class pip:
	pkg_file_list = find_contains('.whl', cache_dir_path)
	def describer(self, pkgFile):
		rawName = os.path.basename(pkgFile).split('-')
		return [path_to_append + pkgFile, rawName[1], rawName[0], inspect_wheel(pkgFile)['dist_info']['metadata']['summary'], parse_from_gpt(rawName[0], 'pip')]

if __name__ == '__main__':
	if not pkgType in globals():
		raise Exception(f"Тип пакетов {pkgType} не поддерживается!")
	describerClass = globals()[pkgType]()

	results = []
	with TP(384) as executor:
		results = list(executor.map(describerClass.describer, describerClass.pkg_file_list))
	print("Generation completed!")

	pkg_path_arr = [gptRes[0] for gptRes in results]
	pkg_version_arr = [gptRes[1] for gptRes in results]
	pkg_name_arr = [gptRes[2] for gptRes in results]
	pkg_legacy_descr_arr = [gptRes[3] for gptRes in results]
	pkg_gpt_descr_arr = [gptRes[4] for gptRes in results]

	df = DataFrame({'Relative path': pkg_path_arr, 'Version': pkg_version_arr, 'Package': pkg_name_arr, 'Legacy description': pkg_legacy_descr_arr, 'Description': pkg_gpt_descr_arr})
	df.to_excel(pkgType + '.xlsx', sheet_name='sheet1', index=False)
