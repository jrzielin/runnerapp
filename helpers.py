from constants import ISO_FORMAT
from datetime import datetime

def parse_int(x):
    try:
        x = int(x)
    except:
        x = None
    return x

def parse_date(x):
    try:
        x = datetime.strptime(x, ISO_FORMAT)
    except:
        x = None
    return x

def parse_bool(x):
    if x in {True, 'true'}:
        return True
    
    if x in {False, 'false'}:
        return False
    
    return None