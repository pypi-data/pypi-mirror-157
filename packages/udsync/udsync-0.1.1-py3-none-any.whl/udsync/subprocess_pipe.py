#!/usr/bin/env python3

import subprocess
import typing

PIPE = '|'

T = typing.TypeVar('T')

def run_and_pipe(cmds: typing.Sequence[str], *, get_output: bool = False) -> subprocess.CompletedProcess[bytes]:
	# I am not using shell=True because that is platform dependend
	# and shlex is for UNIX like shells only, so it may not work on Windows
	if get_output:
		def run(cmd: typing.Sequence[str], input: typing.Optional[bytes] = None) -> subprocess.CompletedProcess[bytes]:
			return subprocess.run(cmd, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	else:
		def run(cmd: typing.Sequence[str], input: typing.Optional[bytes] = None) -> subprocess.CompletedProcess[bytes]:
			return subprocess.run(cmd, input=input)

	cmd_list = split_list(cmds, PIPE)
	n = len(cmd_list)
	if n == 1:
		return run(cmd_list[0])

	p = subprocess.run(cmd_list[0], stdout=subprocess.PIPE)
	for cmd in cmd_list[1:-1]:
		p = subprocess.run(cmd, input=p.stdout, stdout=subprocess.PIPE)
	return run(cmd_list[-1], input=p.stdout)

def split_list(l: typing.Sequence[T], sep: T) -> typing.Sequence[typing.Sequence[T]]:
	out: typing.List[typing.Sequence[T]] = []
	i0 = 0
	while True:
		try:
			i1 = l.index(sep, i0)
		except ValueError:
			break
		out.append(l[i0:i1])
		i0 = i1 + 1
	out.append(l[i0:])
	return out
