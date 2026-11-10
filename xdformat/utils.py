"""Small filename/date helpers and stderr logging for xdformat."""

import datetime
import os
import re
import sys
from collections import namedtuple


def info(s):
    print("INFO: %s" % s, file=sys.stderr)


def warn(s):
    print("WARNING: %s" % s, file=sys.stderr)


def error(s):
    print("ERROR: %s" % s, file=sys.stderr)


def parse_pathname(path):
    # Fix to proper split names like file.xml.1
    ext = os.extsep + os.extsep.join(os.path.basename(path).split(os.extsep)[1:])
    path, fn = os.path.split(path)
    ext = ext if fn else ''
    base = os.path.splitext(fn)[0]
    nt = namedtuple('Pathname', 'path base ext filename')
    return nt(path=path, base=base, ext=ext, filename=fn)


# An xdid is its publication's id (pubid) followed by a date or a number:
#   dated        <pubid><YYYY>-<MM>-<DD>[suffix]   nyt1955-01-01, lat2019-10-11a
#   year, issue  <pubid><YYYY>-<label>             cc1992-av09 (the label starts with a letter)
#   numbered     <pubid>-<number>                  beq-0001, club72-0001, nytpack-16023
# A pubid is letters and digits. It can't end in a four-digit year (`tpfa2024`),
# which the first two forms would read as part of the date.
_XDID_DATED = re.compile(r"([A-Za-z0-9]+?)\d{4}-\d{2}-\d{2}")
_XDID_YEAR_ISSUE = re.compile(r"([A-Za-z0-9]+?)(?:18|19|20)\d{2}-[A-Za-z]")
_XDID_NUMBERED = re.compile(r"([A-Za-z0-9]+)-")
_PUBID_GUESS = re.compile(r"[A-Za-z0-9][A-Za-z]*")


def parse_pubid(fn):
    """The pubid of an xdid, an .xd filename or a source filename.

    An xdid or .xd file (`club72-0001`, `x/nyt1955-01-01.xd`, an `.xd.stub`)
    is read by the xdid forms above, so a pubid may contain digits. Any other
    filename is a source file (`usun230101-data.xml`), whose name is only a
    hint: a full date in it still marks where the pubid ends; otherwise the
    guess is the first character and the letters after it.
    """
    name = os.path.basename(fn)
    base = parse_pathname(fn).base
    m = _XDID_DATED.match(base)
    if not m and ("." not in name or name.lower().endswith((".xd", ".xd.stub"))):
        m = _XDID_YEAR_ISSUE.match(base) or _XDID_NUMBERED.match(base)
    if not m:
        m = _PUBID_GUESS.match(base)
    return m.group(0 if m.re is _PUBID_GUESS else 1).lower() if m else None


def construct_date(y, m, d):
    thisyear = datetime.datetime.today().year
    year, mon, day = int(y), int(m), int(d)

    if year > 1900 and year <= thisyear:
        pass
    elif year < 100:
        if year >= 0 and year <= thisyear - 2000:
            year += 2000
        else:
            year += 1900
    else:
        return None

    if mon < 1 or mon > 12:
        return None

    if day < 1 or day > 31:
        return None

    return datetime.date(year, mon, day)


# from original filename
def parse_date_from_filename(fn):
    base = parse_pathname(fn).base
    m = re.search(r"(\d{2,4})-?(\d{2})-?(\d{2})", base)
    if m:
        g1, g2, g3 = m.groups()
        # try YYMMDD first, then MMDDYY
        return construct_date(g1, g2, g3) or construct_date(g3, g1, g2)
