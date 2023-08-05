#!/usr/bin/env python3

import abc
import typing

class Logger(abc.ABC):

	@abc.abstractmethod
	def show_info(self, msg: str) -> None:
		pass

	@abc.abstractmethod
	def show_error(self, msg: typing.Union[str, BaseException]) -> None:
		pass
