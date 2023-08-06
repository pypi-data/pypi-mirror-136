
import re
import math
from xml.etree import cElementTree
import serial

from . import const

# Const.py

Const = const.Const()


def parse_nmea_line(line):
    break_code = False
    wpt = {}

    msg = re.sub(r'[\n\r]', '', line)
    splitstr = re.split(',', msg)

    # parse waypoints & routes
    if (splitstr and len(splitstr) > 1):
        if splitstr[0] == '$PFEC' and splitstr[1] == 'GPwpl':
            # find description/mark
            mark = re.match('^(\@[a-z]{1})(.+)$', splitstr[8])
            wpt = {
                'name': splitstr[6].strip(),
                'color': Const.colors[int(splitstr[7])] if splitstr[7] and len(splitstr[7]) > 0 and int(
                    splitstr[7]) < len(
                    Const.colors) else Const.defaultColorText,
                'mark': Const.defaultMark,
                'desc': mark.group(2).strip() if mark and mark.group(2).strip() else splitstr[8][2:].strip(),
                'lat': round(float(splitstr[2][2:]) / 60 + float(splitstr[2][:2]), 15) if splitstr[
                    3] == 'N' else round(
                    -float(splitstr[2][2:]) / 60 - float(splitstr[2][:2]), 15),
                'lon': round(float(splitstr[4][3:]) / 60 + float(splitstr[4][:3]), 15) if splitstr[
                    5] == 'E' else round(
                    -float(splitstr[4][3:]) / 60 - float(splitstr[4][:3]), 15)
            }
    return wpt
