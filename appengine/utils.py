import hashlib
import datetime

def utf8encoded(data):
    if data is None:
        return None
    if isinstance(data, unicode):
        return unicode(data).encode('utf-8')
    else:
        return data

def sha1_hash(value):
    return hashlib.sha1(utf8encoded(value)).hexdigest()

def to_isodate(date):
    return date.strftime('%Y%m%dT%H%M%S')

def isodate(str):
    return datetime.datetime.strptime(str, '%Y%m%dT%H%M%S')
