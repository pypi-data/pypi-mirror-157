#!/usr/bin/env python3

import os
import io
import typing

import appdirs

from . import config
from . import urwid_multi_key_support
from .base_classes import Logger

class Exporter:

	APP_NAME = 'udsync'
	CONFIG_FILE_NAME = 'config'

	COMMENT = '#'
	UNDERLINE = '='

	def __init__(self,
		logger: Logger,
		command_maps: typing.Dict[str, urwid_multi_key_support.SubCommandMap],
		reference_command_map: urwid_multi_key_support.SubCommandMap = urwid_multi_key_support.SubCommandMap(),
	) -> None:
		self.config_exporter = config.ConfigExporter(logger)
		self.key_map_exporter = urwid_multi_key_support.CommandMapExporter(logger, command_maps, reference_command_map)
		self.config_exporter.unknown_command = self.key_map_exporter.parse_splitted_line  # type: ignore [assignment]  # This is a bug in mypy https://github.com/python/mypy/issues/2427


	# ------- load -------

	def load(self, fn: typing.Optional[str] = None) -> None:
		if fn is None:
			fn = self.get_filename_to_read()
			if fn is None:
				return

		self.config_exporter.load(fn)


	# ------- save -------

	def save(self, fn: typing.Optional[str] = None, *,
		key_maps: bool = True,
		settings: typing.Optional[typing.Iterable[typing.Union[config.Config[typing.Any], config.DictConfig[typing.Any, typing.Any]]]] = None,
		ignore: typing.Optional[typing.Iterable[typing.Union[config.Config[typing.Any], config.DictConfig[typing.Any, typing.Any]]]] = None,
		no_multi: bool = False,
		comment_out: bool = False,
	) -> str:
		if fn is None:
			fn = self.get_filename_to_write()

		path = os.path.split(fn)[0]
		os.makedirs(path, exist_ok=True)

		with open(fn, 'wt') as f:
			self.save_to_open_file(f, key_maps=key_maps, settings=settings, ignore=ignore, no_multi=no_multi, comment_out=comment_out)

		return fn

	def save_to_open_file(self, f: typing.TextIO, *,
		key_maps: bool = True,
		settings: typing.Optional[typing.Iterable[typing.Union[config.Config[typing.Any], config.DictConfig[typing.Any, typing.Any]]]] = None,
		ignore: typing.Optional[typing.Iterable[typing.Union[config.Config[typing.Any], config.DictConfig[typing.Any, typing.Any]]]] = None,
		no_multi: bool = False,
		comment_out: bool = False,
	) -> None:
		if comment_out:
			f = CommentedFile(f, self.COMMENT)
		self.write_heading(f, 'settings')
		self.config_exporter.save_to_open_file(f, settings, ignore=ignore, no_multi=no_multi)

		if key_maps:
			self.write_sep(f)
			self.write_heading(f, 'key mappings')
			self.key_map_exporter.save_to_open_file(f)

	def write_heading(self, f: typing.TextIO, header: str) -> None:
		prefix = self.COMMENT + ' '
		print(prefix + header, file=f)
		print(prefix + self.UNDERLINE*len(header), file=f)

	def write_sep(self, f: typing.TextIO) -> None:
		print('', file=f)


	# ------- find file -------

	@classmethod
	def get_filename_to_read(cls) -> typing.Optional[str]:
		out = os.path.join(appdirs.user_config_dir(cls.APP_NAME), cls.CONFIG_FILE_NAME)
		if os.path.isfile(out):
			return out

		out = os.path.join(appdirs.user_config_dir(cls.APP_NAME), cls.CONFIG_FILE_NAME)
		if os.path.isfile(out):
			return out

		return None

	@classmethod
	def get_filename_to_write(cls) -> str:
		return os.path.join(appdirs.user_config_dir(cls.APP_NAME), cls.CONFIG_FILE_NAME)


class CommentedFile(io.StringIO):

	'''
	A wrapper around a writable file object
	which inserts :attr:`prefix` in front of every non-empty line
	'''

	def __init__(self, f: typing.TextIO, prefix: str) -> None:
		self.f = f
		self.prefix = prefix
		self.vmode = True

	def write(self, text: str) -> int:
		out = 0
		lines = text.split('\n')
		for ln in lines[:-1]:
			if self.vmode and ln:
				ln = self.prefix + ln
			ln += '\n'
			self.vmode = True
			self.f.write(ln)
			out += len(ln)

		ln = lines[-1]
		if ln:
			if self.vmode:
				ln = self.prefix + ln
			self.vmode = False
			self.f.write(ln)
			out += len(ln)

		return out


if __name__ == '__main__':
	class PrintLogger(Logger):
		def show_error(self, msg: typing.Union[str, BaseException]) -> None:
			print(msg)
		def show_info(self, msg: str) -> None:
			print(msg)

	e = Exporter(PrintLogger(), {'default' : urwid_multi_key_support.SubCommandMap()})
	print(e.get_filename_to_write())
	print(e.get_filename_to_read())
