import os
import sys
import importlib
import json


__path__ = os.path.dirname(os.path.realpath(__file__))
__json__ = sys.exec_prefix
__settings__=__json__+"\\__setting__.path.json"
file=__json__+"\\_packages_.json"
__author__ = 'Alawi Hussein Adnan Al Sayegh'
__description__ = '''a Personal package for me

automatically append paths to sys.path

mange sys.path package'''
__license__ = """
Copyright 2022 "Alawi Hussein Adnan Al Sayegh"
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
and the names are copyrighted
"""
__version__='0.0.1'

def Paths():
	with open(file) as loader:
		return json.load(loader)

def DumpPaths(data):
	if not isinstance(data,list) and not isinstance(data,str):
		raise ValueError(f"excepted a list or str but get {type(data)}")
	elif isinstance(data,str):
		data = [data]

	loader = Paths()
	[loader.append(item) if item not in loader else None for item in data]
	with open(file,"w") as dumper:
		return json.dump(loader,dumper,indent=4)

def clear(rewrite="[]"):
	with open(file,"a") as cleared:
		pass
	with open(file,"w") as cleared:
		cleared.write(rewrite)

def append(paths):
	for path in paths:
		if path not in sys.paths:
			sys.path.append(path)
	return sys.path
def import_module(module,package=None):
	path        = Paths()
	SYSTEMPATHS = sys.path.copy()
	sys.path    = path
	module      = importlib.import_module(module,package)
	sys.path    = SYSTEMPATHS
	return module
def _import_(*args,**kw):
	return import_module(*args,**kw)
def _imports_(IMPORTS,*args,**kw):
	modules = {}
	for IMPORT in IMPORTS:
		modules[IMPORT] = import_module(IMPORT,*args,**kw)
	return modules

def __start__(output=False):
	sys.path = Paths()
	return None if not output else sys.path
class settings(object):
	def init(**kw):
		auto = kw.get("auto",None)
		data = settings.load()
		data.update(kw)
		settings.dump(kw)
		return data
	def create():
		with open(__settings__,"a") as setting:
			settings.dump({})
	def dump(settings):
		with open(__settings__,"w") as setting:
			json.dump(settings,setting,indent=4)
	def clear(rewrite="{}"):
		with open(file,"a") as cleared:
			pass
		with open(file,"w") as cleared:
			cleared.write(rewrite)
	def load():
		try:
			with open(__settings__,"r") as setting:
				try:
					return json.load(setting)
				except json.decoder.JSONDecodeError as e:
					settings.dump({}) # decode error. reset settings.path.json file
					return json.load(setting)
		except FileNotFoundError as e:
			settings.dump({})
			return settings.load()

	def auto():
		return settings.load().get("auto")
	def exex():
		return settings.load().get("exec")
	def execit():
		return settings.load().get("execit")

