#!/usr/bin/env python3

import os
import shutil
import shlex
import functools
import enum
import collections.abc
import typing

from .base_classes import Logger

VALUE_TRUE = 'true'
VALUE_FALSE = 'false'
VALUE_NONE = 'none'
VALUE_AUTO = 'auto'

ConfigId = typing.NewType('ConfigId', str)

T = typing.TypeVar('T')
T_KEY = typing.TypeVar('T_KEY')
T1 = typing.TypeVar('T1')


def readable_quote(value: str) -> str:
	out = shlex.quote(value)
	if out == value:
		return out

	if '"\'"' in out and '"' not in value:
		return '"' + value + '"'

	return out


class Config(typing.Generic[T]):

	_Self = typing.TypeVar('_Self', bound='Config[T]')

	LIST_SEP = ','

	instances: typing.Dict[str, 'Config[typing.Any]'] = {}

	default_config_id = ConfigId('general')

	def __init__(self,
		key: str,
		default: T, *,
		help: typing.Union[str, typing.Dict[T, str], None] = None,
		parent: typing.Optional['DictConfig[typing.Any, T]'] = None,
		allowed_values: typing.Optional[typing.Sequence[T]] = None,
	):
		'''
		:param key: The name of this setting in the config file
		:param default: The default value of this setting
		:param help: A description of this setting

		:const:`config.T` can be one of:
			* :class:`str`
			* :class:`int`
			* :class:`float`
			* :class:`bool`
			* a subclass of :class:`enum.Enum`
			* a class where :meth:`__str__` returns a string representation which can be passed to the constructor to create an equal object and which may have a str attribute :attr:`type_name`

		:raises ValueError: if key is not unique
		'''
		self._key = key
		self.value = default
		self.type = type(default)
		self.help = help
		self.parent = parent
		self.allowed_values = allowed_values

		if self.type == list:
			if not default:
				raise ValueError('I cannot infer the type from an empty list')
			self.item_type = type(default[0])  # type: ignore [index]  # mypy does not understand that I just checked that default is a list

		cls = type(self)
		if key in cls.instances:
			raise ValueError(f'duplicate config key {key!r}')
		cls.instances[key] = self

	@property
	def key(self) -> str:
		return self._key

	@key.setter
	def key(self, key: str) -> None:
		if key in self.instances:
			raise ValueError(f'duplicate config key {key!r}')
		del self.instances[self._key]
		self._key = key
		self.instances[key] = self


	@typing.overload
	def __get__(self: _Self, instance: None, owner: typing.Any = None) -> _Self:
		pass

	@typing.overload
	def __get__(self, instance: typing.Any, owner: typing.Any = None) -> T:
		pass

	def __get__(self: _Self, instance: typing.Any, owner: typing.Any = None) -> typing.Union[T, _Self]:
		if instance is None:
			return self

		return self.value

	def __set__(self, instance: typing.Any, value: T) -> None:
		self.value = value

	def __repr__(self) -> str:
		return '%s(%s)' % (type(self).__name__, ', '.join(repr(a) for a in (self.key, self.value)))

	def parse_and_set_value(self, config_id: typing.Optional[ConfigId], value: str) -> None:
		if config_id is None:
			config_id = self.default_config_id
		if config_id != self.default_config_id:
			raise ValueError(f'{self.key} cannot be set for specific groups, config_id must be the default {self.default_config_id!r} not {config_id!r}')
		self.value = self.parse_value(value)

	def parse_value(self, value: str) -> T:
		return self.parse_value_part(self.type, value)

	def parse_value_part(self, t: typing.Type[T1], value: str) -> T1:
		''':raises ValueError: if value is invalid'''
		if t == str:
			out = typing.cast(T1, value)
		elif t == int:
			out = typing.cast(T1, int(value, base=0))
		elif t == float:
			out = typing.cast(T1, float(value))
		elif t == bool:
			if value == VALUE_TRUE:
				out = typing.cast(T1, True)
			elif value == VALUE_FALSE:
				out = typing.cast(T1, False)
			else:
				raise ValueError(f'invalid value for {self.key}: {value!r} (should be {self.format_allowed_values_or_type()})')
		elif t == list:
			return typing.cast(T1, [self.parse_value_part(self.item_type, v) for v in value.split(self.LIST_SEP)])
		elif issubclass(t, enum.Enum):
			for enum_item in t:
				if self.format_any_value(typing.cast(T1, enum_item)) == value:
					out = typing.cast(T1, enum_item)
					break
			else:
				raise ValueError(f'invalid value for {self.key}: {value!r} (should be {self.format_allowed_values_or_type()})')
		else:
			try:
				out = t(value)  # type: ignore [call-arg]
			except ValueError:
				raise ValueError(f'invalid value for {self.key}: {value!r} (should be {self.format_allowed_values_or_type()})')

		if self.allowed_values is not None and out not in self.allowed_values:
			raise ValueError(f'invalid value for {self.key}: {value!r} (should be {self.format_allowed_values_or_type()})')
		return out


	def format_allowed_values_or_type(self) -> str:
		out = self.format_allowed_values()
		if out:
			return 'one of ' + out

		out = self.format_type()
		# getting the article right is not so easy, so a user can specify the correct article with type_article
		# this also gives the possibility to omit the article
		# https://en.wiktionary.org/wiki/Appendix:English_articles#Indefinite_singular_articles
		if hasattr(self.type, 'type_article'):
			article = getattr(self.type, 'type_article')
			if not article:
				return out
			assert isinstance(article, str)
			return article + ' ' + out
		if out[0].lower() in 'aeio':
			return 'an ' + out
		return 'a ' + out

	def format_allowed_values(self, t: typing.Optional[typing.Type[typing.Any]] = None) -> str:
		if t is None:
			t = self.type
		allowed_values: typing.Iterable[typing.Any]
		if self.allowed_values is not None:
			allowed_values = self.allowed_values
		elif t == bool:
			allowed_values = (True, False)
		elif issubclass(t, enum.Enum):
			allowed_values = t
		else:
			return ''

		return ', '.join(self.format_any_value(val) for val in allowed_values)


	def wants_to_be_exported(self) -> bool:
		return True

	def format_type(self, t: typing.Optional[typing.Type[typing.Any]] = None) -> str:
		if t is None:
			if self.type is list:
				t = self.item_type
				item_type = self.format_allowed_values(t)
				if not item_type:
					item_type = self.format_type(t)
				return 'comma separated list of %s' % item_type

			t = self.type

		return getattr(t, 'type_name', t.__name__)

	def format_value(self, config_id: typing.Optional[ConfigId]) -> str:
		return self.format_any_value(self.value)

	def format_any_value(self, value: typing.Any) -> str:
		if isinstance(value, enum.Enum):
			return value.name.lower().replace('_', '-')
		if isinstance(value, bool):
			return VALUE_TRUE if value else VALUE_FALSE
		if isinstance(value, list):
			return self.LIST_SEP.join(self.format_any_value(v) for v in value)
		return str(value)


class DictConfig(typing.Generic[T_KEY, T]):

	def __init__(self,
		key_prefix: str,
		default_values: typing.Dict[T_KEY, T], *,
		ignore_keys: typing.Container[T_KEY] = set(),
		help: typing.Optional[str] = None,
		allowed_values: typing.Optional[typing.Sequence[T]] = None,
	) -> None:
		'''
		:param key_prefix:
		:param default:
		:param ignore_keys:
		:param help:

		:raises ValueError: if a key is not unique
		'''
		self._values: typing.Dict[T_KEY, Config[T]] = {}
		self._ignored_values: typing.Dict[T_KEY, T] = {}
		self.allowed_values = allowed_values

		self.key_prefix = key_prefix
		self.help = help
		self.ignore_keys = ignore_keys

		for key, val in default_values.items():
			self[key] = val

	def format_key(self, key: T_KEY) -> str:
		if isinstance(key, enum.Enum):
			key_str = key.name.lower().replace('_', '-')
		elif isinstance(key, bool):
			key_str = VALUE_TRUE if key else VALUE_FALSE
		else:
			key_str = str(key)

		return '%s.%s' % (self.key_prefix, key_str)

	def __setitem__(self, key: T_KEY, val: T) -> None:
		if key in self.ignore_keys:
			self._ignored_values[key] = val
			return

		c = self._values.get(key)
		if c is None:
			self._values[key] = self.new_config(self.format_key(key), val, help=self.help)
		else:
			c.value = val

	def new_config(self, key: str, default: T, *, help: typing.Union[str, typing.Dict[T, str], None]) -> Config[T]:
		return Config(key, default, help=help, parent=self, allowed_values=self.allowed_values)

	def __getitem__(self, key: T_KEY) -> T:
		if key in self.ignore_keys:
			return self._ignored_values[key]
		else:
			return self._values[key].value

	def __repr__(self) -> str:
		return '%s(%r, ignore_keys=%r)' % (type(self).__name__, {key:val.value for key,val in self._values.items()} | {key:val for key,val in self._ignored_values.items()}, self.ignore_keys)

	def __contains__(self, key: T_KEY) -> bool:
		if key in self.ignore_keys:
			return key in self._ignored_values
		else:
			return key in self._values

	def __iter__(self) -> typing.Iterator[T_KEY]:
		yield from self._values
		yield from self._ignored_values

	def iter_keys(self) -> typing.Iterator[str]:
		for key in self._values:
			yield self.format_key(key)


class ConfigTrackingChanges(Config[T]):

	_has_changed = False

	@property  # type: ignore [override]  # This is a bug in mypy https://github.com/python/mypy/issues/4125
	def value(self) -> T:  # type: ignore [override]  # This is a bug in mypy https://github.com/python/mypy/issues/4125
		return self._value

	@value.setter
	def value(self, value: T) -> None:
		self._value = value
		self._has_changed = True

	def save_value(self, new_value: T) -> None:
		self._last_value = self._value
		self._value = new_value
		self._has_changed = False

	def restore_value(self) -> None:
		self._value = self._last_value

	def has_changed(self) -> bool:
		return self._has_changed


# ========== settings which can have different values for different groups ==========

class MultiConfig(Config[T]):

	_Self = typing.TypeVar('_Self', bound='MultiConfig[T]')
	config_ids: typing.List[ConfigId] = []

	@classmethod
	def reset(cls) -> None:
		cls.config_ids.clear()
		for cfg in Config.instances:
			if isinstance(cfg, MultiConfig):
				cfg.values.clear()

	def __init__(self,
		key: str,
		default: T, *,
		help: typing.Union[str, typing.Dict[T, str], None] = None,
		parent: typing.Optional['MultiDictConfig[typing.Any, T]'] = None,
		allowed_values: typing.Optional[typing.Sequence[T]] = None,
	) -> None:
		super().__init__(key, default, help=help, parent=parent, allowed_values=allowed_values)
		self.values: typing.Dict[ConfigId, T] = {}

	# I don't know why this code duplication is necessary,
	# I have declared the overloads in the parent class already.
	# But without copy-pasting this code mypy complains
	# "Signature of __get__ incompatible with supertype Config"
	@typing.overload
	def __get__(self: _Self, instance: None, owner: typing.Any = None) -> _Self:
		pass

	@typing.overload
	def __get__(self, instance: typing.Any, owner: typing.Any = None) -> T:
		pass

	def __get__(self: _Self, instance: typing.Any, owner: typing.Any = None) -> typing.Union[T, _Self]:
		if instance is None:
			return self

		return self.values.get(instance.config_id, self.value)

	def __set__(self, instance: typing.Any, value: T) -> None:
		config_id = instance.config_id
		self.values[config_id] = value
		if config_id not in self.config_ids:
			self.config_ids.append(config_id)

	def parse_and_set_value(self, config_id: typing.Optional[ConfigId], value: str) -> None:
		if config_id is None:
			config_id = self.default_config_id
		if config_id == self.default_config_id:
			self.value = self.parse_value(value)
		else:
			self.values[config_id] = self.parse_value(value)
		if config_id not in self.config_ids:
			self.config_ids.append(config_id)

	def format_value(self, config_id: typing.Optional[ConfigId]) -> str:
		if config_id is None:
			config_id = self.default_config_id
		return self.format_any_value(self.values.get(config_id, self.value))


class MultiDictConfig(DictConfig[T_KEY, T]):

	_Self = typing.TypeVar('_Self', bound='MultiDictConfig[T_KEY, T]')

	@typing.overload
	def __get__(self: _Self, instance: None, owner: typing.Any = None) -> _Self:
		pass

	@typing.overload
	def __get__(self, instance: typing.Any, owner: typing.Any = None) -> 'InstanceSpecificDictMultiConfig[T_KEY, T]':
		pass

	def __get__(self: _Self, instance: typing.Any, owner: typing.Any = None) -> 'typing.Union[InstanceSpecificDictMultiConfig[T_KEY, T], _Self]':
		if instance is None:
			return self

		return InstanceSpecificDictMultiConfig(self, instance.config_id)

	def __set__(self, instance: typing.Any, value: T) -> None:
		raise NotImplementedError()

	def new_config(self, key: str, default: T, *, help: typing.Union[str, typing.Dict[T, str], None]) -> MultiConfig[T]:
		return MultiConfig(key, default, help=help, parent=self, allowed_values=self.allowed_values)

class InstanceSpecificDictMultiConfig(typing.Generic[T_KEY, T]):

	def __init__(self, dmc: 'MultiDictConfig[T_KEY, T]', config_id: ConfigId) -> None:
		self.dmc = dmc
		self.config_id = config_id

	def __setitem__(self, key: T_KEY, val: T) -> None:
		if key in self.dmc.ignore_keys:
			raise TypeError('cannot set value of ignored key %r' % key)

		c = self.dmc._values.get(key)
		if c is None:
			self.dmc._values[key] = MultiConfig(self.dmc.format_key(key), val, help=self.dmc.help)
		else:
			c.__set__(self, val)

	def __getitem__(self, key: T_KEY) -> T:
		if key in self.dmc.ignore_keys:
			return self.dmc._ignored_values[key]
		else:
			return self.dmc._values[key].__get__(self)


# ========== data types ==========

class Path:

	'''
	This is the path as it is stored in the config file.
	It may contain stuff like ~/... and device UUIDs to be mounted.
	In order to use it it needs to be converted with lsblk.mounter.expand_path.
	'''

	type_name = 'path'
	help = '''
	The path to a directory.
	You can use "~/" as an abbreviation for your home directory.
	The path may start with "UUID:.../", then the file system is mounted automatically.
	If the file system is on an encrypted partition you can use "UNLOCK:...,UUID:.../".
	'''

	def __init__(self, value: str) -> None:
		self.raw = value

	def __str__(self) -> str:
		return self.raw

	def __repr__(self) -> str:
		return '%s(%r)' % (type(self).__name__, self.raw)

	def __bool__(self) -> bool:
		return bool(self.raw)


class Regex(str):

	type_name = 'regular expression'
	help = 'https://docs.python.org/3/library/re.html#regular-expression-syntax'


class Command(collections.abc.Sequence[str]):

	type_name = 'command'

	def __init__(self, arg: typing.Iterable[str]) -> None:
		if isinstance(arg, str):
			self.cmd = shlex.split(arg)
		else:
			self.cmd = list(arg)

	# ------- custom methods -------

	def replace(self, wildcard: str, replacement: str) -> 'Command':
		return Command(replacement if word == wildcard else word for word in self.cmd)

	# ------- sequence -------

	@typing.overload
	def __getitem__(self, i: int) -> str:
		pass

	@typing.overload
	def __getitem__(self, i: slice) -> 'Command':
		pass

	def __getitem__(self, i: typing.Union[int, slice]) -> typing.Union[str, 'Command']:
		if isinstance(i, slice):
			return Command(self.cmd[i])
		return self.cmd[i]

	def __len__(self) -> int:
		return len(self.cmd)

	# ------- comparison -------

	def __eq__(self, other: typing.Any) -> bool:
		if isinstance(other, Command):
			return self.cmd == other.cmd
		return NotImplemented

	# ------- to str -------

	def __str__(self) -> str:
		return ' '.join(shlex.quote(word) for word in self.cmd)

	def __repr__(self) -> str:
		return '%s(%s)' % (type(self).__name__, self.cmd)

class CommandWithAlternatives(Command):

	type_name = 'command with alternatives'
	help = '''
	One or more commands separated by ||.
	The first command where the program is installed is executed. The other commands are ignored.
	The command is executed without a shell so setting environment variables and redirection are not possible but piping works anyway.
	If you need a shell write the command to a file, insert an appropriate shebang line, make the file executable and set this value to the file.
	'''

	SEP = '||'

	@property
	def cmd(self) -> typing.Sequence[str]:  # type: ignore [override]  # This is a bug in mypy https://github.com/python/mypy/issues/4125
		for cmd in self.commands:
			if shutil.which(cmd[0]):
				return cmd.cmd

		raise FileNotFoundError('none of the commands is installed: %s' % self)

	def __init__(self, commands: typing.Union[typing.Sequence[typing.Sequence[str]], str]) -> None:
		if isinstance(commands, str):
			self.commands = [Command(cmd) for cmd in commands.split(self.SEP)]
		else:
			self.commands = [Command(cmd) for cmd in commands]

	def __str__(self) -> str:
		return self.SEP.join(str(cmd) for cmd in self.commands)

	def __repr__(self) -> str:
		return '%s(%s)' % (type(self).__name__, self.commands)



@functools.total_ordering
class SortedEnum(enum.Enum):

	def __lt__(self, other: typing.Any) -> bool:
		if self.__class__ is other.__class__:
			l: typing.Sequence['SortedEnum'] = list(type(self))
			return l.index(self) < l.index(other)
		return NotImplemented


# ========== config file ==========

class ParseException(Exception):
	pass

class MultipleParseExceptions(Exception):

	def __init__(self, exceptions: typing.Sequence[ParseException]) -> None:
		super().__init__()
		self.exceptions = exceptions

	def __iter__(self) -> typing.Iterator[ParseException]:
		return iter(self.exceptions)

class ConfigExporter:

	COMMENT = '#'
	COMMENT_PREFIXES = ('"', '#')
	ENTER_GROUP_PREFIX = '['
	ENTER_GROUP_SUFFIX = ']'
	KEY_VAL_SEP = '='

	SET = ('set',)
	INCLUDE = ('include',)

	primitive_types = {str, int, bool, float}


	def __init__(self, logger: Logger, config_instances: typing.Dict[str, Config[typing.Any]] = Config.instances) -> None:
		self.logger = logger
		self.config_instances = config_instances

	# ------- load -------

	def load(self, fn: str) -> None:
		self.config_id: typing.Optional[ConfigId] = None
		self.load_without_resetting_config_id(fn)

	def load_without_resetting_config_id(self, fn: str) -> None:
		with open(fn, 'rt') as f:
			for lnno, ln in enumerate(f, 1):
				self.parse_line(ln, lnno, f.name)

	def parse_line(self, ln: str, lnno: typing.Optional[int] = None, fn: typing.Optional[str] = None) -> None:
		'''
		:param ln: The line to be parsed
		:param lnno: The number of the line, used in error messages
		:param fn: The full name of the file from which ln was read, used in error messages and for relative imports

		Calls :meth:`parse_error` if something goes wrong, e.g. invalid key or invalid value.
		'''
		ln = ln.strip()
		if not ln:
			return
		if self.is_comment(ln):
			return
		if self.enter_group(ln):
			return

		ln_splitted = shlex.split(ln, comments=True)
		self.parse_splitted_line(ln_splitted, ln, lnno, fn)

	def enter_group(self, ln: str) -> bool:
		if ln.startswith(self.ENTER_GROUP_PREFIX) and ln.endswith(self.ENTER_GROUP_SUFFIX):
			self.config_id = typing.cast(ConfigId, ln[len(self.ENTER_GROUP_PREFIX):-len(self.ENTER_GROUP_SUFFIX)])
			return True
		return False

	def parse_splitted_line(self, ln_splitted: typing.Sequence[str], ln: str, lnno: typing.Optional[int] = None, fn: typing.Optional[str] = None) -> None:
		cmd = ln_splitted[0]

		try:
			if cmd in self.SET:
				self.set(ln_splitted)
			elif cmd in self.INCLUDE:
				self.include(fn, ln_splitted)
			else:
				self.unknown_command(ln_splitted, ln, lnno, fn)
		except ParseException as e:
			self.parse_error(str(e), ln, lnno)
		except MultipleParseExceptions as exceptions:
			for exc in exceptions:
				self.parse_error(str(exc), ln, lnno)

	def is_comment(self, ln: str) -> bool:
		for c in self.COMMENT_PREFIXES:
			if ln.startswith(c):
				return True
		return False


	def set(self, cmd: typing.Sequence[str]) -> None:
		if len(cmd) < 2:
			raise ParseException('no settings given')

		if self.KEY_VAL_SEP in cmd[1]:  # cmd[0] is the name of the command, cmd[1] is the first argument
			self.set_multiple(cmd)
		else:
			self.set_with_spaces(cmd)

	def set_with_spaces(self, cmd: typing.Sequence[str]) -> None:
		n = len(cmd)
		if n == 3:
			cmdname, key, value = cmd
			self.parse_key_and_set_value(key, value)
		elif n == 4:
			cmdname, key, sep, value = cmd
			if sep != self.KEY_VAL_SEP:
				raise ParseException(f'seperator between key and value should be {self.KEY_VAL_SEP}, not {sep!r}')
			self.parse_key_and_set_value(key, value)
		elif n == 2:
			raise ParseException(f'missing value or missing {self.KEY_VAL_SEP}')
		else:
			assert n >= 5
			raise ParseException(f'too many arguments given or missing {self.KEY_VAL_SEP} in first argument')

	def set_multiple(self, cmd: typing.Sequence[str]) -> None:
		exceptions = []
		for arg in cmd[1:]:
			if not self.KEY_VAL_SEP in arg:
				raise ParseException(f'missing {self.KEY_VAL_SEP} in {arg!r}')
			key, value = arg.split(self.KEY_VAL_SEP, 1)
			try:
				self.parse_key_and_set_value(key, value)
			except ParseException as e:
				exceptions.append(e)
		if exceptions:
			raise MultipleParseExceptions(exceptions)

	def parse_key_and_set_value(self, key: str, value: str) -> None:
		if key not in self.config_instances:
			raise ParseException(f'invalid key {key!r}')

		instance = self.config_instances[key]
		try:
			self.parse_and_set_value(instance, value)
		except ValueError as e:
			raise ParseException(str(e))

	def parse_and_set_value(self, instance: Config[T], value: str) -> None:
		instance.parse_and_set_value(self.config_id, value)


	def include(self, fn: typing.Optional[str], cmd: typing.Sequence[str]) -> None:
		if len(cmd) != 2:
			raise ParseException('invalid number of arguments, expected exactly one: the file to include')

		fn_imp = cmd[1]
		fn_imp = os.path.expanduser(fn_imp)
		if fn and not os.path.isabs(fn_imp):
			fn_imp = os.path.join(os.path.split(os.path.abspath(fn))[0], fn_imp)

		if os.path.isfile(fn_imp):
			self.load_without_resetting_config_id(fn_imp)
		else:
			raise ParseException(f'no such file {fn_imp!r}')


	def unknown_command(self, ln_splitted: typing.Sequence[str], ln: str, lnno: typing.Optional[int], fn: typing.Optional[str]) -> typing.Optional[typing.NoReturn]:

		raise ParseException('unkown command %r' % ln_splitted[0])


	# ------- save -------

	def save(self,
		fn: str,
		config_instances: typing.Optional[typing.Iterable[typing.Union[Config[typing.Any], DictConfig[typing.Any, typing.Any]]]] = None, *,
		ignore: typing.Optional[typing.Iterable[typing.Union[Config[typing.Any], DictConfig[typing.Any, typing.Any]]]] = None,
		no_multi: bool = False,
		comments: bool = True,
	) -> None:
		'''
		Save the current values of all settings to a file.

		:param fn: The name of the file to write to
		:param config_instances: Do not save all settings but only those given. If this is a :class:`list` they are written in the given order. If this is a :class:`set` they are sorted by their keys.
		:param ignore: Do not write these settings to the file.
		:param no_multi: Do not write several sections. For :class:`MultiConfig` instances write the default values only.
		:param comments: Write comments with allowed values and help.
		'''
		with open(fn, 'wt') as f:
			self.save_to_open_file(f, config_instances, ignore=ignore, no_multi=no_multi, comments=comments)


	def save_to_open_file(self,
		f: typing.TextIO,
		config_instances: typing.Optional[typing.Iterable[typing.Union[Config[typing.Any], DictConfig[typing.Any, typing.Any]]]] = None, *,
		ignore: typing.Optional[typing.Iterable[typing.Union[Config[typing.Any], DictConfig[typing.Any, typing.Any]]]] = None,
		no_multi: bool = False,
		comments: bool = True,
	) -> None:
		'''
		Save the current values of all settings to a file.

		:param f: The file to write to
		:param config_instances: Do not save all settings but only those given. If this is a :class:`list` they are written in the given order. If this is a :class:`set` they are sorted by their keys.
		:param ignore: Do not write these settings to the file.
		:param no_multi: Do not write several sections. For :class:`MultiConfig` instances write the default values only.
		:param comments: Write comments with allowed values and help.
		'''
		self.last_name: typing.Optional[str] = None
		config_keys: typing.Iterable[str]
		if config_instances is None:
			config_keys = self.config_instances.keys()
			config_keys = sorted(config_keys)
		else:
			config_keys = []
			for c in config_instances:
				if isinstance(c, DictConfig):
					config_keys.extend(sorted(c.iter_keys()))
				else:
					config_keys.append(c.key)
			if not isinstance(config_instances, (list, tuple)):
				config_keys = sorted(config_keys)

		if ignore is not None:
			tmp = set()
			for c in tuple(ignore):
				if isinstance(c, DictConfig):
					tmp |= set(c._values.values())
				else:
					tmp.add(c)
			ignore = tmp

		if comments:
			self.write_data_types(f, config_keys, ignore)

		multi_config_keys = []
		for key in config_keys:
			instance = self.config_instances[key]
			if not instance.wants_to_be_exported():
				continue

			if ignore is not None and instance in ignore:
				continue

			if not no_multi and isinstance(instance, MultiConfig):
				multi_config_keys.append(key)
				continue

			if comments:
				self.write_help(f, instance)
			value = self.format_value(instance, None)
			value = readable_quote(value)
			ln = f'{self.SET[0]} {key} = {value}\n'
			f.write(ln)

		if multi_config_keys:
			for config_id in MultiConfig.config_ids:
				f.write('\n')
				f.write(self.ENTER_GROUP_PREFIX + config_id + self.ENTER_GROUP_SUFFIX + '\n')
				for key in multi_config_keys:
					instance = self.config_instances[key]
					value = self.format_value(instance, config_id)
					value = shlex.quote(value)
					if comments:
						self.write_help(f, instance)
					ln = f'{self.SET[0]} {key} = {value}\n'
					f.write(ln)

	def format_value(self, instance: Config[T], config_id: typing.Optional[ConfigId]) -> str:
		return instance.format_value(config_id)

	def write_data_types(self, f: typing.TextIO, config_keys: typing.Iterable[str], ignore: typing.Optional[typing.Iterable[Config[typing.Any]]]) -> None:
		data_types_to_be_explained = set()
		for key in config_keys:
			instance = self.config_instances[key]
			if not instance.wants_to_be_exported():
				continue

			if ignore is not None and instance in ignore:
				continue

			t = instance.type if instance.type != list else instance.item_type

			if t in self.primitive_types:
				continue

			if issubclass(t, enum.Enum):
				continue

			if not hasattr(t, 'help'):
				continue

			data_types_to_be_explained.add(t)

		prefix = self.COMMENT + ' '
		n = '\n'

		if not data_types_to_be_explained:
			return

		name = 'Data types'
		f.write(prefix + name + n)
		f.write(prefix + '-'*len(name) + n)

		for name, t in sorted(((getattr(t, 'type_name', t.__name__), t) for t in data_types_to_be_explained), key=lambda name_type: name_type[0]):
			ln = '- %s' % name
			f.write(prefix + ln + n)
			for ln in self.strip_indentation(t.help.rstrip().lstrip('\n').splitlines()):
				ln = '  ' + ln
				f.write(prefix + ln + n)

	@staticmethod
	def strip_indentation(lines: typing.Iterable[str]) -> typing.Iterator[str]:
		lines = iter(lines)
		ln = next(lines)
		stripped_ln = ln.lstrip()
		yield stripped_ln

		i = len(ln) - len(stripped_ln)
		for ln in lines:
			assert i == 0 or ln[:i].isspace()
			yield ln[i:]

	def write_help(self, f: typing.TextIO, instance: Config[typing.Any]) -> None:
		if instance.parent is not None:
			name = instance.parent.key_prefix
		else:
			name = instance.key
		if name == self.last_name:
			return

		prefix = self.COMMENT + ' '
		n = '\n'

		f.write(n)
		f.write(prefix + name + n)
		f.write(prefix + '-'*len(name) + n)
		f.write(prefix + instance.format_allowed_values_or_type() + n)
		if isinstance(instance.help, dict):
			for key, val in instance.help.items():
				key_name = instance.format_any_value(key)
				val_name = instance.format_any_value(val)
				f.write(prefix + key_name + ': ' + val_name + n)
		elif isinstance(instance.help, str):
			f.write(prefix + instance.help + n)

		self.last_name = name


	# ------- error handling -------

	def parse_error(self, msg: str, ln: str, lnno: typing.Optional[int]) -> None:
		'''
		Is called if something went wrong while trying to load a config file.
		This method compiles the given information into an error message and calls :meth:`Logger.show_error`.

		:param msg: The error message
		:param ln: The line where the error occured
		:param lnno: The number of the line
		'''
		if lnno is not None:
			lnref = 'line %s' % lnno
		else:
			lnref = 'line'
		msg +=  f' while trying to parse {lnref} {ln!r}'
		self.logger.show_error(msg)


if __name__ == '__main__':
	filename = os.path.join('autotest', 'test.conf')
	if not os.path.exists('autotest'):
		os.mkdir('autotest')

	class PrintLogger(Logger):
		def show_error(self, msg: typing.Union[str, BaseException]) -> None:
			print(msg)
		def show_info(self, msg: str) -> None:
			print(msg)

	class Test:
		a = Config('a', 1)
		b = Config('b', 2)
		c = Config('c', 'c')

	t = Test()
	e = ConfigExporter(PrintLogger(), Config.instances)
	print('default values:')
	print('Test.a: %r' % Test.a)
	print('t.a: %r' % t.a)
	print('t.b: %r' % t.b)
	print('t.c: %r' % t.c)

	if os.path.exists(filename):
		e.load(filename)
		print('loaded values:')
		print('Test.a: %r' % Test.a)
		print('t.a: %r' % t.a)
		print('t.b: %r' % t.b)
		print('t.c: %r' % t.c)

	t.a += 1
	print('modified value:')
	print('Test.a: %r' % Test.a)
	print('t.a: %r' % t.a)
	print('t.b: %r' % t.b)
	print('t.c: %r' % t.c)

	e.save(filename)
