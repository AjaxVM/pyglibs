
import safe_python

def get_default_theme():
    return {"Label":
            {"font":
             {"size":25,
              "color":(0, 0, 0),
              "name":None,
              "aa":True}}}

def load_theme(filename):
    if not safe_python.test_safe(filename):
        return False
    exec open(filename, "rU").read()
    return theme
