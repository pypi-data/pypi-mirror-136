import serial
import os
from . import furuno_read
from . import furuno_write
import re
import pandas as pd
import time
from datetime import datetime
from . import const


def write_raw_nmea(file_name, data):
    _time = str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
    with open(f"{file_name}_{_time}.nmea", "w") as outfile:
        outfile.write("\n".join(data))
    print(f"Raw nmea saved as {file_name}_{_time}.nmea")


def write_raw_gpx(file_name, data):
    _time = str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
    with open(f"{file_name}_{_time}.gpx", "w") as outfile:
        outfile.write("\n".join(data))


def write_parsed_nmea(file_name, data):
    _time = str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))

    df = pd.DataFrame.from_dict(data)
    df.to_csv(f"{file_name}_{_time}.csv", index=False)


def searchcom():
    # chose an implementation, depending on os
    # ~ if sys.platform == 'cli':
    # ~ else:
    if os.name == "nt":  # sys.platform == 'win32':
        from serial.tools.list_ports_windows import comports
    elif os.name == "posix":
        from serial.tools.list_ports_posix import comports
    # ~ elif os.name == 'java':
    else:
        raise ImportError(
            "Sorry: no implementation for COM ports \
                for your platform ('{}') available".format(
                os.name
            )
        )
    iterator = sorted(comports())
    return [data[0].strip() for data in iterator]


def save_raw_nmea(filename, nmea_flag=False, port="/dev/ttyUSB0"):
    com_port = port
    baud_rate = 4800
    ser = serial.Serial(
        com_port,
        baud_rate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=True,
    )

    if ser.is_open:
        ser.close()
        time.sleep(2)

    raw_nmea = []

    ser.open()
    while True:
        line = str(ser.readline().decode("utf-8").strip())
        if "PFEC" in line:
            raw_nmea.append(line)
            if "GPxfr" not in line:
                print("Received waypoint: " + re.split(",", line)[6])

        if "GPxfr" in line:
            ser.close()
            break

    print(f"{len(raw_nmea)} waypoints exported.")
    ser.close()

    if nmea_flag:
        write_raw_nmea(file_name=filename, data=raw_nmea)
    return raw_nmea


def save_all_waypoints(
    filename,
    port,
    nmea_flag=False,
    csv_flag=False,
    debug=False,
):
    if debug:
        with open("raw_nmea.nmea", "r") as nmea:
            rwa_nmea = nmea.readlines()
            rwa_nmea = list(map(str.strip, rwa_nmea))
    else:
        rwa_nmea = save_raw_nmea(filename=filename, port=port, nmea_flag=nmea_flag)

    list_wpts = []

    for line in rwa_nmea:
        wpt = furuno_read.parse_nmea_line(line)
        if wpt:
            list_wpts.append(wpt)

    if csv_flag:
        write_parsed_nmea(filename, list_wpts)

    return list_wpts


def write_to_gpx(list_wpts, file_name="test_gpx", debug=False):
    Const = const.Const()
    if debug:
        save_all_waypoints(filename=file_name, debug=True)
    gpx_wpt = []
    gpx_wpt.append(Const.header)
    gpx_wpt.append(
        Const.metadata.format(
            time=str(datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"))
        )
    )

    for v in list_wpts:
        gpx_wpt.append(
            Const.waypoint.format(
                desc=v["desc"],
                mark=v["mark"],
                color=v["color"],
                name=v["name"],
                lat=v["lat"],
                lon=v["lon"],
            )
        )
    gpx_wpt.append(Const.footer)
    write_raw_gpx(file_name, gpx_wpt)


def save_gps_to_gpx(port, filename="GP32_test.gpx", nmea_flag=False, csv_flag=False):
    wpts = save_all_waypoints(
        filename=filename, nmea_flag=nmea_flag, csv_flag=csv_flag, port=port
    )
    write_to_gpx(wpts, filename)


def write_to_gps(list_nmea, port="/dev/ttyUSB0"):
    com_port = port
    baud_rate = 4800
    ser = serial.Serial(
        com_port,
        baud_rate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=True,
    )

    if ser.is_open:
        ser.close()
        time.sleep(2)

    ser.open()

    for i in range(len(list_nmea)):
        print(f'{format((i+1) / len(list_nmea) *100, ".2f")} % completed')
        ser.write(list_nmea[i].encode("utf-8", "replace") + b"\r\n")

    ser.close()


def from_gpx_to_gps(gpx_file, port):
    listnmea = furuno_write.get_nmea_from_file(gpx_file)
    write_to_gps(listnmea, port)


if __name__ == "__main__":
    # save_raw_nmea()

    Const = const.Const()
    list_nmea = furuno_write.get_nmea_from_file(gpx_file="test2.gpx")
    print(list_nmea)
