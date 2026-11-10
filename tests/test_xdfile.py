"""Core .xd parse/serialize tests."""

import datetime
import os

from xdformat.utils import parse_pathname, parse_date_from_filename
from xdformat.xdfile import xdfile as XDFile
import xdformat

test_selection = 'nyt1955-01-01.xd'


def test_filename():
    base = parse_pathname(test_selection).base
    assert base == 'nyt1955-01-01'


def test_parse_date():
    date = parse_date_from_filename(test_selection)
    assert isinstance(date, datetime.date)
    assert date.strftime('%a %b %d %Y') == 'Sat Jan 01 1955'


SAMPLE_XD = """\
Title: Test Puzzle
Author: Test Author
Date: 2024-01-01


ABC
D#E
FGH


A1. First across ~ ABC
A3. Second across ~ FGH

D1. First down ~ ADF
D2. Second down ~ CEH
"""


def test_no_blank_clue_on_roundtrip():
    """Parsing and re-emitting an .xd file should not add blank clues."""
    xd = XDFile(SAMPLE_XD, filename='test2024-01-01.xd')
    for pos, clue, answer in xd.clues:
        assert pos != ('', ''), "Blank clue entry should not be added during parsing"
        assert answer != '', "Every clue should have an answer"


def test_roundtrip_stable():
    """Parsing and re-emitting an .xd file should produce identical output."""
    xd = XDFile(SAMPLE_XD, filename='test2024-01-01.xd')
    output = xd.to_unicode()
    xd2 = XDFile(output, filename='test2024-01-01.xd')
    output2 = xd2.to_unicode()
    assert output == output2, "Round-trip should be stable"


def test_to_unicode_collapses_newlines_in_clues():
    """to_unicode() must collapse newlines in clue text so output is valid .xd."""
    xd = XDFile(SAMPLE_XD, filename='test2024-01-01.xd')
    # Inject a clue with embedded newlines (simulating converter output)
    xd.clues[0] = (('A', 1), '"He got up in his rings\nand fancy ___"', 'ABC')
    output = xd.to_unicode()
    for line in output.splitlines():
        if line.startswith('A1.'):
            assert 'rings and fancy' in line
            assert '\n' not in line
            break
    else:
        assert False, "A1 clue not found in output"
    # Verify the output parses cleanly
    xd2 = XDFile(output, filename='test2024-01-01.xd')
    assert xd2.get_answer('A1') == 'ABC'


def test_answers_from_grid():
    xd = XDFile(SAMPLE_XD, filename='test2024-01-01.xd')
    answers = {d + str(n): answer for d, n, answer in xd.iteranswers()}
    assert answers == {'A1': 'ABC', 'A3': 'FGH', 'D1': 'ADF', 'D2': 'CEH'}


def test_no_filename_ok():
    """A puzzle needs no filename, and its date is its Date header."""
    xd = XDFile(SAMPLE_XD)
    assert xd.get_header('Title') == 'Test Puzzle'
    assert xd.date() == '2024-01-01'


def test_date_is_not_read_from_the_filename():
    """The format knows nothing about a collection's file naming."""
    xd = XDFile(SAMPLE_XD.replace('Date: 2024-01-01\n', ''), filename='nyt1955-01-01.xd')
    assert not xd.date()
    assert not hasattr(xd, 'xdid') and not hasattr(xd, 'publication_id')


def test_fixture_rebus_roundtrip():
    """The 1955 NYT rebus puzzle from the spec parses, expands rebus answers,
    and round-trips stably."""
    fn = os.path.join(os.path.dirname(__file__), 'nyt1955-01-01.xd')
    xd = xdformat.parse(fn)
    assert xd.size() == (15, 15)
    assert xd.rebus() == {'1': 'HEART', '2': 'DIAMOND', '3': 'SPADE', '4': 'CLUB'}
    answers = {d + str(n): answer for d, n, answer in xd.iteranswers()}
    assert answers['A1'] == 'HEARTACHE'
    assert answers['D1'] == 'HEARTBEAT'

    out = xd.to_unicode()
    xd2 = XDFile(out, filename=fn)
    assert xd2.to_unicode() == out
