# Utils

import sys

def getchar():
    sys.stdin.read(1)

# update property of name to value
def updateProperty(path, name, value):
    fp = None
    targetLine = None
    newLine = None
    try:
        fp = open(path)
        minlen = len(name) + 1
        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue
            group = line.strip().split('=')
            if 2 != len(group) or group[0].strip() != name:
                continue
            if group[1] == value:
                return None
            else:
                targetLine = line
                newLine = '{}={}\r\n'.format(name,value)
                break
    except IOError:
        pass
    finally:
        if fp != None: fp.close()

    if targetLine != None and newLine != None:
        with open(path) as fp:
            content = fp.read()

        content = content.replace(targetLine, newLine)

        with open(path, 'w') as fp:
            fp.write(content)

    return None

def getProperty(path, name):

    fp = None

    try:
        fp = open(path)

        minlen = len(name) + 1

        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue

            group = line.strip().split('=')

            if 2 != len(group) or group[0].strip() != name:
                continue

            return group[1].strip()

    except IOError:
        pass

    finally:
        if fp != None: fp.close()

    return None

