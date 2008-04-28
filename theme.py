import pygame
import safe_python

import os

pygame.init()

"""|image_name| loads an image
$font_name loads a font"""

all_functions = []
special = ["=", "{", "}", ":", "|", "$"]

def convert_value(val):
    if val == "None":
        return None
    if val == 'True':
        return True
    if val == "False":
        return False
    try:
        a = float(val)
        try:
            if int(val) == a:
                a = int(val)
        except:
            pass
        return a
    except:
        return val

def get_values(line):
    obj = []
    cur = ""
    is_string = False
    for i in line:
        if not line or line[0] == "#":
            return []
        if is_string:
            if i == '"':
                is_string = False
                obj.append(convert_value(cur))
                cur = ""
            else:
                cur = cur + i
        elif i in special:
            if cur:
                obj.append(convert_value(cur))
                cur = ""
            obj.append(i)
        elif i == '"':
            if cur:
                obj.append(convert_value(cur))
                cur = ""
            is_string = True
        elif i == " ":
            if cur:
                obj.append(convert_value(cur))
                cur = ""
        else:
            cur = cur + i
    if cur:
        obj.append(convert_value(cur))

    return obj

def matches(values, format):
    if format and format[-1] == "*->":
        format[-1] = "*"
        popped = []
        while len(values) > len(format):
            a = values.pop()
            popped.append(a)
        for i in popped:
            if i in special:
                values.extend(popped)#make sure they return alright ;)
                return False
        popped.reverse() #because we reversed them when we popped them ;)
        if format and (not len(values) == len(format)):
            values.extend(popped) #make sure they return alright ;)
            return False
        for i in xrange(len(values)):
            if not ((format[i] == "*" and not values[i] in special) or\
                    values[i] == format[i]):
                values.extend(popped) #make sure they return alright ;)
                return False
        values.extend(popped) #make sure they return alright ;)
        return True
    if format and (not len(values) == len(format)):
        return False
    for i in xrange(len(values)):
        if not ((format[i] == "*" and not values[i] in special) or\
                values[i] == format[i]):
            return False
    return True

def fix_path(foldername, pathname):
    if not pathname:
        return pathname
    return os.path.join(foldername, *pathname.split("/"))

def load_theme(foldername):
    filename = os.path.join(foldername, "theme.txt")
    if not safe_python.test_safe(filename, all_functions):
        return False

    f = open(filename, "rU").read()
    f.replace("\r", "\n")

    data = {}
    current_widget = [None, {}]

    for line in f.split("\n"):
        values = get_values(line)
        if not values:
            continue
        if matches(values, ["{", "*", ":"]):
            #this is pushing the latest widget to a new one
            if current_widget[0] or current_widget[1]:
                data[current_widget[0]] = current_widget[1]
            current_widget = [values[1], {}]
        if matches(values, ["*", "=", "|", "*", "|"]):
            if values[3] == None or values[3] == "noimage":
                current_widget[1][values[0]] = values[3]
            else:
                current_widget[1][values[0]] = pygame.image.load(fix_path(foldername, values[3]))
                try:
                    current_widget[1][values[0]] = current_widget[1][values[0]].convert_alpha()
                except:
                    pass
        if matches(values, ["*", "=", "*"]):
            current_widget[1][values[0]] = values[2]
        elif matches(values, ["*", "=", "*->"]):
            current_widget[1][values[0]] = values[2::]
        if matches(values, ["*", "=", "$", "*", "*"]):
            current_widget[1][values[0]] = pygame.font.Font(fix_path(foldername, values[3]), values[4])
        if values[-1] == "}":
            data[current_widget[0]] = current_widget[1]
            current_widget = [None, {}]
    if current_widget[0] or current_widget[1]:
        if not current_widget[0] in data:
            data[current_widget[0]] = current_widget[1]
        else:
            for i in current_widget[1]:
                data[current_widget[0]][i] = current_widget[1][i]
    return data

def get_default_theme():
    return load_theme("default_theme")

