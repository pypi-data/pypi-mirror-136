from xml.etree import cElementTree
import re
import math
from . import const

# Const.py

Const = const.Const()


def read_file(path_of_file):
    try:
        root = cElementTree.parse(path_of_file).getroot()
    except:
        print("Could not open input file!")
    return root


def extract_wpt(node):
    # find waypoint
    lon = float(node.attrib["lon"])
    furuno_lon = round(
        math.floor(abs(lon)) * 100 + ((abs(lon) - math.floor(abs(lon))) * 60), 3
    )
    lat = float(node.attrib["lat"])
    furuno_lat = round(
        math.floor(abs(lat)) * 100 + ((abs(lat) - math.floor(abs(lat))) * 60), 3
    )
    tmp_wpt = {
        "lon": "%09.3f" % furuno_lon,
        "NS": "S" if lon > 0 else "N",
        "lat": "%08.3f" % furuno_lat,
        "EW": "W" if lat > 0 else "E",
        "name": "",
        "desc": "",
        "color": Const.defaultColor,
        "mark": Const.defaultMark,
    }
    for wpt in node:
        if re.search("\}name", wpt.tag) and wpt.text:
            tmp_wpt["name"] = wpt.text.strip().upper()
        if re.search("\}desc", wpt.tag) and wpt.text:
            tmp_wpt["desc"] = wpt.text.strip().upper()
        if re.search("\}sym", wpt.tag) and wpt.text:
            splitSym = re.split(",", wpt.text)
            if len(splitSym) == 2:
                foundmark = [
                    f for f in Const.marks if (Const.marks[f] == splitSym[0].strip())
                ]
                tmp_wpt["mark"] = (
                    foundmark[0] if len(foundmark) > 0 else Const.defaultMark
                )
                tmp_wpt["color"] = (
                    Const.colors.index(splitSym[1].strip())
                    if splitSym[1].strip() in Const.colors
                    else Const.defaultColor
                )
            else:
                foundmark = [
                    f for f in Const.marks if (Const.marks[f] == wpt.text.strip())
                ]
                tmp_wpt["mark"] = (
                    foundmark[0] if len(foundmark) > 0 else Const.defaultMark
                )
    return tmp_wpt


def extract_route(node):
    tmpRoute = {"name": "", "desc": "", "track": []}
    for rte in node:
        if re.search("\}name$", rte.tag) and rte.text:
            tmpRoute["name"] = rte.text.strip().upper()
            # take only 8 first symbols in route name  for furuno 32 version compatible!
            tmpRoute["name"] = (
                tmpRoute["name"] if len(tmpRoute["name"]) <= 8 else tmpRoute["name"][:8]
            )

        if re.search("\}desc$", rte.tag) and rte.text:
            tmpRoute["desc"] = rte.text.strip().upper()
        if (
            re.search("\}rtept$", rte.tag)
            and ("lon" in rte.attrib)
            and ("lat" in rte.attrib)
        ):
            lon = float(rte.attrib["lon"])
            furuno_lon = round(
                math.floor(abs(lon)) * 100 + ((abs(lon) - math.floor(abs(lon))) * 60), 3
            )
            lat = float(rte.attrib["lat"])
            furuno_lat = round(
                math.floor(abs(lat)) * 100 + ((abs(lat) - math.floor(abs(lat))) * 60), 3
            )
            tmpRoute["track"].append(
                {
                    "lon": "%09.3f" % furuno_lon,
                    "NS": "S" if lon > 0 else "N",
                    "lat": "%08.3f" % furuno_lat,
                    "EW": "W" if lat > 0 else "E",
                    "name": "",
                    "desc": "",
                    "color": Const.defaultColor,
                    "mark": Const.defaultMark,
                }
            )
            routesTrackCounter = len(tmpRoute["track"]) - 1
            for rtept in rte:
                if re.search("\}name", rtept.tag) and rtept.text:
                    tmpRoute["track"][routesTrackCounter][
                        "name"
                    ] = rtept.text.strip().upper()
                if re.search("\}desc", rtept.tag) and rtept.text:
                    tmpRoute["track"][routesTrackCounter][
                        "desc"
                    ] = rtept.text.strip().upper()
                if re.search("\}sym", rtept.tag) and rtept.text:
                    splitSym = re.split(",", rtept.text)
                    if len(splitSym) == 2:
                        foundmark = [
                            f
                            for f in Const.marks
                            if (Const.marks[f] == splitSym[0].strip())
                        ]
                        tmpRoute["track"][routesTrackCounter]["mark"] = (
                            foundmark[0] if len(foundmark) > 0 else Const.defaultMark
                        )
                        tmpRoute["track"][routesTrackCounter]["color"] = (
                            Const.colors.index(splitSym[1].strip())
                            if splitSym[1].strip() in Const.colors
                            else Const.defaultColor
                        )
                    else:
                        foundmark = [
                            f
                            for f in Const.marks
                            if (Const.marks[f] == rtept.text.strip())
                        ]
                        tmpRoute["track"][routesTrackCounter]["mark"] = (
                            foundmark[0] if len(foundmark) > 0 else Const.defaultMark
                        )
    return tmpRoute


def parse_gpx(gpx):
    try:
        parseWaypoints = {}
        parseRoutes = {}
        waypointsCounter = 0
        routesCounter = 0

        list_name_longer_than_6 = []
        list_wpt_in_double = []

        for child in gpx:
            if (
                re.search("\}wpt$", child.tag)
                and ("lon" in child.attrib)
                and ("lat" in child.attrib)
            ):
                # extract_wpt(child)
                wpt = extract_wpt(child)

                if (
                    wpt["name"] in parseWaypoints.keys()
                    and wpt["name"] not in list_wpt_in_double
                ):
                    list_wpt_in_double.append(wpt["name"])

                if len(wpt["name"]) > 6:
                    list_name_longer_than_6.append(wpt["name"])

                parseWaypoints[wpt["name"]] = wpt
                waypointsCounter += 1

            if re.search("\}rte$", child.tag):
                parseRoutes[routesCounter] = extract_route(child)
                routesCounter += 1

        error = [list_name_longer_than_6, list_wpt_in_double]

        return (parseWaypoints, parseRoutes, error)
    except:
        print("Error parsing GPX")


def get_nmea_from_parsed_gpx(wpt_parsed, rte_parsed):
    putData = []
    for _, value in wpt_parsed.items():

        lat = value["lat"]
        ns = value["NS"]
        lon = value["lon"]
        ew = value["EW"]
        name = value["name"]
        color = value["color"]
        desc = str(value["mark"]) + str(value["desc"])

        putData.append(
            f"$PFEC,GPwpl,{lat},{ns},{lon},{ew},{name:6.6},{color},{desc:18.18},A,,,,"
        )

    route_num = 0
    for _, value in rte_parsed.items():
        # print(value)
        if value["track"] and len(value["track"]) > 0:
            route_num += 1
            sentence_num = math.ceil(len(value["track"]) / 8)
            sentence_count = 1
            inner_sentence_count = 1
            line = f"$GPRTE,{sentence_num},{sentence_count},C,{route_num:02d}"

            for x in range(0, len(value["track"])):
                name = value["track"][x]["name"]
                line += f", {name:6}"
                if inner_sentence_count == 8 or x == len(value["track"]) - 1:
                    inner_sentence_count = 1
                    sentence_count += 1
                    putData.append(line)
                    line = f"$GPRTE,{sentence_num},{sentence_count},C,{route_num:02d}"
                else:
                    inner_sentence_count += 1

            # name track
            route_num = route_num
            name = value["name"]
            putData.append(f"$PFEC,GPrtc,{route_num:02d},{name:16.16}")

    putData.append("$PFEC,GPxfr,CTL,E")
    return putData


def get_nmea_from_file(gpx_file):
    gpx = read_file(gpx_file)
    wpts, rtes, error = parse_gpx(gpx)
    if len(error[0]) > 0 or len(error[1]) > 0:
        print("error in parsing")
    print(f"\nThere are {len(wpts)} waypoints and {len(rtes)} routes to export")
    return get_nmea_from_parsed_gpx(wpts, rtes)


if __name__ == "__main__":
    test_file = "test2.gpx"
    get_nmea_from_file(test_file)
