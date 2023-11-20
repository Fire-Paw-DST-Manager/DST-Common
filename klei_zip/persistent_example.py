# -*- coding: utf-8 -*-
from base64 import b64decode

var = {
    "\x00": "KLEI     1DAQAAABAAAAAAAAAACAAAAHjaAwAAAAAB",
    "\x01": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwQAAAIAAg==",
    "\x02": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwIAAAMAAw==",
    "\x03": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwYAAAQABA==",
    "\x04": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwEAAAUABQ==",
    "\x05": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwUAAAYABg==",
    "\x06": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwMAAAcABw==",
    "\x07": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaYwcAAAgACA==",
    "\x08": "KLEI     1DAQAAABAAAAABAAAACQAAAHja4wAAAAkACQ==",
    "\x09": "KLEI     1DAQAAABAAAAABAAAACQAAAHja4wQAAAoACg==",
    "\x0a": "KLEI     1DAQAAABAAAAABAAAACQAAAHja4wIAAAsACw==",
    "1\x001": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwQAADIAMg==",

    " ": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaUwAAACEAIQ==",
    "0": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwAAADEAMQ==",
    "2": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwIAADMAMw==",
    "3": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwYAADQANA==",
    "4": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwEAADUANQ==",
    "5": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwUAADYANg==",
    "6": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwMAADcANw==",
    "7": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwcAADgAOA==",
    "8": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaswAAADkAOQ==",
    "9": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaswQAADoAOg==",
    "10": "KLEI     1DAQAAABAAAAACAAAACgAAAHjaMzQAAACUAGI=",
    "100": "KLEI     1DAQAAABAAAAADAAAACwAAAHjaMzQwAAABJgCS",
    "ABC": "KLEI     1DAQAAABAAAAADAAAACwAAAHjac3RyBgABjQDH",
    "BBC": "KLEI     1DAQAAABAAAAADAAAACwAAAHjac3JyBgABkADI",
    "ACC": "KLEI     1DAQAAABAAAAADAAAACwAAAHjac3R2BgABjwDI",
    "ABD": "KLEI     1DAQAAABAAAAADAAAACwAAAHjac3RyAQABjgDI",
    "~": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaqwMAAH8Afw==",
    "\x7f": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaqwcAAIAAgA==",
    "~~~": "KLEI     1DAQAAABAAAAADAAAACwAAAHjaq6urAwAC9wF7",
    "\x7f\x7f\x7f": "KLEI     1DAQAAABAAAAADAAAACwAAAHjaq6+vBwAC/QF+",
    "你": "KLEI     1DAQAAABAAAAADAAAACwAAAHjae7J3AQAEyQJC",

    "": "KLEI     1DAQAAABAAAAAAAAAACAAAAHjaAwAAAAAB",
    "1": "KLEI     1DAQAAABAAAAABAAAACQAAAHjaMwQAADIAMg==",
    "11": "KLEI     1DAQAAABAAAAACAAAACgAAAHjaMzQEAACVAGM=",
    "111": "KLEI     1DAQAAABAAAAADAAAACwAAAHjaMzQ0BAABKQCU",
    "1111": "KLEI     1DAQAAABAAAAAEAAAADAAAAHjaMzQ0NAQAAe4AxQ==",
    "11111": "KLEI     1DAQAAABAAAAAFAAAACwAAAHjaMzQEAgAC5AD2",
    "111111": "KLEI     1DAQAAABAAAAAGAAAACwAAAHjaMzQEAQAECwEn",
    "1111111": "KLEI     1DAQAAABAAAAAHAAAACwAAAHjaMzQEAwAFYwFY",
    # "1x33":            "KLEI     1DAQAAABAAAAAhAAAACwAAAHjaMzQkAABrggZS",
    # "1x65":            "KLEI     1DAQAAABAAAABBAAAADAAAAHjaMzSkEAAAmuEMcg==",
    # "1x64^2-1":        "KLEI     1DAQAAABAAAAD/DwAAHAAAAHja7cEBDQAAAMKgTO9fzh4OKAAAAODcAPdwD/0=",
    # "1x64^2":          "KLEI     1DAQAAABAAAAAAEAAAHAAAAHja7cEBDQAAAMKgTO9fzh4OKAAAAODdAAetEC4=",
    # "1x64^2+1":        "KLEI     1DAQAAABAAAAABEAAAHAAAAHja7cEBDQAAAMKgTO9fzh4OKAAAAODeABgMEF8=",
    # "1x64^4-1":        "KLEI     1DAQAAABAAAAD///8AvT8AAHja7MGBAAAA  AMBUYnfe7g== 全长21791，只取了前后缀。",
    # "1x64^4":          "KLEI     1DAQAAABAAAAAAAAABvT8AAHja7MGBAAAA  AMBVQaXfHw== 全长21791，只取了前后缀。这两项省略的部分完全相同",
    # "1x64^4+1":        "KLEI     1DAQAAABAAAAABAAABvT8AAHja7MGBAAAA  AMBWIQTfUA== 全长21791，只取了前后缀。这两项省略的部分完全相同",
}
tt = {}
for key, value in var.items():
    # tt[key] = '\\x' + b64decode(value[11:31]).hex('~').replace('~', '\\x')
    tt[key] = b64decode(value[11:31]).hex(' ')
# print(tt)
tt = {' ': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '0': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '1': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '2': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '3': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '4': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '5': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '6': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '7': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '8': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '9': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '10': '01 00 00 00 10 00 00 00 02 00 00 00 0a 00 00 00 78 da',
      '11': '01 00 00 00 10 00 00 00 02 00 00 00 0a 00 00 00 78 da',
      '100': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      '111': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      'ABC': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      'BBC': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      'ACC': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      'ABD': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      '~': '01 00 00 00 10 00 00 00 01 00 00 00 09 00 00 00 78 da',
      '~~~': '01 00 00 00 10 00 00 00 03 00 00 00 0b 00 00 00 78 da',
      '': '01 00 00 00 10 00 00 00 00 00 00 00 08 00 00 00 78 da',
      '1111': '01 00 00 00 10 00 00 00 04 00 00 00 0c 00 00 00 78 da',
      '11111': '01 00 00 00 10 00 00 00 05 00 00 00 0b 00 00 00 78 da',
      '111111': '01 00 00 00 10 00 00 00 06 00 00 00 0b 00 00 00 78 da',
      '1111111': '01 00 00 00 10 00 00 00 07 00 00 00 0b 00 00 00 78 da',
      '1x33': '01 00 00 00 10 00 00 00 21 00 00 00 0b 00 00 00 78 da',
      '1x65': '01 00 00 00 10 00 00 00 41 00 00 00 0c 00 00 00 78 da',
      '1x64^2-1': '01 00 00 00 10 00 00 00 ff 0f 00 00 1c 00 00 00 78 da',
      '1x64^2': '01 00 00 00 10 00 00 00 00 10 00 00 1c 00 00 00 78 da',
      '1x64^2+1': '01 00 00 00 10 00 00 00 01 10 00 00 1c 00 00 00 78 da',
      '1x64^4-1': '01 00 00 00 10 00 00 00 ff ff ff 00 bd 3f 00 00 78 da',
      '1x64^4': '01 00 00 00 10 00 00 00 00 00 00 01 bd 3f 00 00 78 da',
      '1x64^4+1': '01 00 00 00 10 00 00 00 01 00 00 01 bd 3f 00 00 78 da'}
