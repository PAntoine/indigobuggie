#!/usr/bin/env python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------
#
#                    ,--.
#                    |  |-.  ,---.  ,---. ,--.--.,--,--,
#                    | .-. '| .-. :| .-. ||  .--'|      \
#                    | `-' |\   --.' '-' '|  |   |  ||  |
#                     `---'  `----' `---' `--'   `--''--'
#
#    file: config
#    desc: Configuration.
#
#          This function simply will read/write a simple config file. It does less
#          things than the std library config reader, but it is part of the library
#          and needs no external support and is too simple a beasty to worry about
#          it being the same.
#
#          It will return a config item, that is a set of dictionaries with config
#          items in them.
#
#  author: Peter Antoine
#    date: 25/07/2015
#---------------------------------------------------------------------------------
#                     Copyright (c) 2015 Peter Antoine
#                           All rights Reserved.
#                      Released Under the MIT Licence
#---------------------------------------------------------------------------------

from collections import OrderedDict


class Config(object):
	@staticmethod
	def toBool(value):
		if type(value) == bool:
			return value
		elif type(value) == int:
			return value != 0
		else:
			return value == 'True' or value == 'true'

	""" Beorn Config Class

		This class handles the Configuration files.

		This handles configuration items in the following ways. For the [..] items
		it is added to the config dictionary with the string between the [] as the
		key. If there is more then one item with the same string then the item is
		removed and the item is replaced with a list item, but is keyed with the
		same name, both dictionary items are added to the list. Any subsequent items
		with the same name are added to the list.

		i.e.

		[item]
		name = somehting
		time = 5435435345
		[list]
		name = fdsfsdf
		xxx = fdsfsdfsd

		Will produce:
		 config = {'item':{'name':'something', 'time':5435435345}, 'list',{'name':'..','xxx':...}}

	    But after it finds, the following:

		[list]
		name = vvvvvvv
		xxx = fdsfsdfsd
		[list]
		name = fffffff
		xxx = fdsfsdfsd

		It will produce:

		 config = {'item':{'name':'something', 'time':5435435345},
		           'list',[{'name':'fdsfsdf','xxx':'fdsfsdfsd'},
				           {'name':'vvvvvvv','xxx':'fdsfsdfsd'},
				           {'name':'vvvvvvv','xxx':'fdsfsdfsd'}]}

		Obviously each config item does not need to have the same items and the config
		class does not check or care in anyway.

		The config items are stored in an ordered dict so that when writing back the configuration
		it does not change the order, so that changes can be diff'ed in an SCM as that will be
		backed by one (more that likely).
	"""
	def __init__(self, filename, config=None):
		""" Init the Config Class """
		if config is None:
			self.sections = OrderedDict()

		elif type(config) == dict:
			self.sections = OrderedDict(config)

		elif type(config) == OrderedDict:
			self.sections = config

		self.filename = filename

	def load(self):
		""" This function will load the configuration """
		if self.filename is None:
			result = ERROR_NO_FILENAME_SPECIFIED

		else:
			try:
				# now open the project file
				with open(self.filename) as f:
					items = f.read().splitlines()

				result = self._parseConfigItems(items)

			except IOError:
				self.filename = None
				result = ERROR_FAILED_TO_READ_FROM_FILE

		return result

	def save(self):
		""" Save Configuration

			load(filename) -> result_code

			This function will load the project. It will expect the file to exist and be
			in the correct format as produced by the Project.save() function. This will load the
			project from the given file, also it will remember the filename and will use this name
			for updating the project later.
		"""
		result = True

		if self.filename is None:
			result = ERROR_NO_FILENAME_SPECIFIED

		else:
			try:
				proj_file = open(self.filename, 'w')

				for line in self.export():
					proj_file.write("%s\n" % line)

				proj_file.close()

			except IOError:
				result = ERROR_FAILED_TO_WRITE_TO_FILE

		return result

	def export(self):
		""" Export Config

			This will produce a list of strings containing the configuration.
		"""
		result = []

		for key in self.sections:
			if type(self.sections[key]) == list:
				for list_item in self.sections[key]:
					result.append("[%s]" % key)
					self._dump_complex(result, '', list_item)
			else:
				result.append("[%s]" % key)
				self._dump_complex(result, '', self.sections[key])

		return result

	def find(self, section, item=None):
		""" Find

			This function will return the item(s) that match the search criteria.
			If the item parameter is None, then it will return the whole section
			that matches the section that the name matches. If the item is given
			then it will return the item that matches the given name.

			If the section is a list then it will return all the items that match
			the section. It the item is not None it will return all the item from
			the section that has the specified item.

			If value is supplied it will check if the item as the value, and only
			return items that have the value.
		"""
		result = None

		if section in self.sections:
			if item is None:
				result = self.sections[section]
			else:
				if type(item) != list:
					item = [ item ]

				result = self.sections[section]

				for key in item[:-1]:
					if key in result:
						result = result[key]
					else:
						result = None
						break

				if result is not None and item[-1] in result:
					result = result[item[-1]]
				else:
					result = None

		return result

	def setValue(self, section, item, value=None):
		""" Find

			This function will return the item(s) that match the search criteria.
			If the item parameter is None, then it will return the whole section
			that matches the section that the name matches. If the item is given
			then it will return the item that matches the given name.

			If the section is a list then it will return all the items that match
			the section. It the item is not None it will return all the item from
			the section that has the specified item.

			If value is supplied it will check if the item as the value, and only
			return items that have the value.
		"""
		result = None

		if section not in self.sections:
			self.sections[section] = OrderedDict()

		if type(item) != list:
			item = [ item ]

		result = self.sections[section]

		for key in item[:-1]:
			if key not in result:
				result[key] = OrderedDict()
			result = result[key]

		result[item[-1]] = value

	def addDictionary(self, section, item=None):
		""" Add Item or Section to config

			This function will add an entry to the configuration.
		"""
		new_section = OrderedDict(item)
		self._addNewSection(section, new_section)

	def move(self, section, item_key, to):
		""" Add Item or Section to config

			This function will add an entry to the configuration.
		"""
		if item_key is None:
			to.sections[section] = self.sections[section]
			del self.sections[section]
		else:
			parent = self.sections[section]
			current = self.sections[section]

			types = []

			for key in item_key:
				if key in current:
					types.append(type(current[key]))
					parent = current
					current = current[key]
				else:
					types = None
					break

			if section not in to.sections:
				to.sections[section] = OrderedDict()

			to_current = to.sections[section]

			for index,key in enumerate(item_key[:-1]):
				if key in to_current:
					to_current = to_current[key]

				else:
					if type(to_current) == OrderedDict:
						to_current[key] = types[index]()
						to_current = to_current[key]
					else:
						to_current.append(types[index]())
						to_current = to_current[-1]

			if type(to_current) == list:
				to_current.append(parent[item_key[-1]])
			else:
				to_current[item_key[-1]] = parent[item_key[-1]]

			del parent[item_key[-1]]

	def remove(self, section, item=None):
		""" Remove

			This function will remove all the items that match the search. it uses
			the same search as the ind.
		"""
		result = False
		current = None

		if item is None:
			if section in self.sections:
				del self.sections[section]
				result = True

		elif section in self.sections:
			if type(item) != list:
				item = [ item ]

			current = self.sections[section]

			for key in item[:-1]:
				if key in current:
					current = current[key]
				else:
					current = None
					break

			if item[-1] in current:
				del current[item[-1]]
				result = True

		return result

	def _dump_complex(self, result, name, item):
		if isinstance(item, dict):
			for key in item:
				if name == '':
					self._dump_complex(result, key, item[key])
				else:
					self._dump_complex(result, name + '#' + key, item[key])

		elif isinstance(item, list):
			for index, x in enumerate(item):
				if name == '':
					self._dump_complex(result, str(index), x)
				else:
					self._dump_complex(result, name + '%' + str(index), x)
		else:
			result.append(name + ' = ' + str(item))

	def _addNewSection(self, current_key, current_section):
		""" This de-duplicates adding a new item to the config """
		# Ok, deal with the old item
		if current_key in self.sections:
			if type(self.sections[current_key]) == list:
				self.sections[current_key].append(current_section)

			else:
				temp = self.sections[current_key]
				self.sections[current_key] = [temp, current_section]
		else:
			self.sections[current_key] = current_section

	def _insertItem(self, section, path, value):
		""" Insert the items from the path into the section.
			It will add all the new dicts and lists as it finds new ones.
		"""
		current = section

		for item in path:
			if (type(current) == list and item[0] < len(current)) or item[0] in current:
				current = current[item[0]]
			else:
				if item[1] == 0:
					if type(current) == list:
						current.append(OrderedDict())
					else:
						current[item[0]] = OrderedDict()
					current = current[item[0]]
				else:
					current[item[0]] = []
					current = current[item[0]]

		if type(current) == list:
			current.append(value[1])
		else:
			current[value[0]] = value[1]

	def _parseConfigItems(self, items):
		""" This """
		result = True
		current_key = None
		current_section = OrderedDict()

		for item in items:
			if item[0] == '[':
				if current_section != {}:
					self._addNewSection(current_key, current_section)

					# clear down for the next go
					current_section = OrderedDict()
					current_key = None

				# now start the new item
				if item[-1] == ']':
					current_key = item[1:-1]

			elif len(item) > 0 and item[0] != '#':
				# Ok, it's not just a blank line or a comment.
				value = None
				looking_for_dict = -1
				looking_for_list = -1
				parts = []

				for index in range(len(item)-1, -1, -1):
					if item[index] == '#':
						if looking_for_dict != -1:
							parts.insert(0,(item[index+1:looking_for_dict],0))
						elif looking_for_list != -1:
							parts.insert(0,(item[index+1:looking_for_list],1))

						if value is None:
							value = item[index+1:].split(' = ')

						looking_for_list = -1
						looking_for_dict = index

					elif item[index] == '%':
						if looking_for_dict != -1:
							parts.insert(0,(int(item[index+1:looking_for_dict]),0))
						elif looking_for_list != -1:
							parts.insert(0,(int(item[index+1:looking_for_list]),1))

						if value is None:
							bits = item[index+1:].split(' = ')
							value = (int(bits[0]), bits[1])

						looking_for_list = index
						looking_for_dict = -1

				if looking_for_dict != -1:
					parts.insert(0,(item[index:looking_for_dict],0))
				elif looking_for_list != -1:
					parts.insert(0,(item[index:looking_for_list],1))

				if value is None:
					value = item.split(' = ')

				self._insertItem(current_section, parts, value)

		if current_section != {}:
			self._addNewSection(current_key, current_section)

		return result

# vim: ts=4 sw=4 noexpandtab nocin ai
