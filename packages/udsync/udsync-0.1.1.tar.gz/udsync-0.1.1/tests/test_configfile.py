#!/usr/bin/env pytest -s

import io

from udsync import configfile as sut


def test__commented_file__no_linebreaks() -> None:
	mock = io.StringIO()
	f = sut.CommentedFile(mock, '#')

	assert f.write('a') == 2
	assert f.write('b') == 1
	assert f.write('c') == 1

	assert mock.getvalue() == '#abc'

def test__commented_file__one_line_per_write() -> None:
	mock = io.StringIO()
	f = sut.CommentedFile(mock, '#')

	lines = ('hello world', 'nice weather today', 'did I greet you already?')
	for ln in lines:
		assert f.write(ln + '\n') == len(ln) + 2

	assert mock.getvalue().splitlines() == ['#'+ln for ln in lines]
	assert mock.getvalue()[-1] == '\n'

def test__commented_file__multiple_lines_per_write() -> None:
	mock = io.StringIO()
	f = sut.CommentedFile(mock, '//')

	assert f.write('abc\ndef\n') == 8 + 4
	assert f.write('ghi\njkl\nmno') == 11 + 6

	assert mock.getvalue().split('\n') == [
		'//abc',
		'//def',
		'//ghi',
		'//jkl',
		'//mno',
	]

def test__commented_file__dont_prefix_empty_lines() -> None:
	mock = io.StringIO()
	f = sut.CommentedFile(mock, '#')

	assert f.write('\n') == 1
	assert f.write('\n') == 1
	assert f.write('abc\n') == 4 + 1
	assert f.write('\n') == 1
	assert f.write('') == 0
	assert f.write('\n') == 1
	assert f.write('def\n\nghi') == 8 + 2

	assert mock.getvalue().split('\n') == [
		'',
		'',
		'#abc',
		'',
		'',
		'#def',
		'',
		'#ghi',
	]
