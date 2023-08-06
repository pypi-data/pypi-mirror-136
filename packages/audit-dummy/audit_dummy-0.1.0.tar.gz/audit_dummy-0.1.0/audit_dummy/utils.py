import json
from functools import partial
filepath = 'file.json'

def withjson(func):
    with open(filepath, 'r+') as f:
        return func(f)
    return 'could not open file.'

def readind(file, ind):
    j = getjson(file)
    data = j['data']
    if ind < 0 or ind >= len(data):
        return 'error' 
    return data[ind]

def appenddata(file, appdata):
    j = getjson(file)
    data = j['data']
    data.append(appdata)
    file.seek(0)
    json.dump(j, file)
    file.truncate()
    return True

def getjson(file):
    contents = file.readlines()[0]
    parsed = json.loads(contents)
    return parsed

def handleRead(ind):
    # bind readind to ind
    reader = partial(readind, ind = ind)
    return withjson(reader)

def handleAppend(data):
    appender = partial(appenddata, appdata = data)
    return withjson(appender)




    



