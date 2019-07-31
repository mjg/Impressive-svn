#!/usr/bin/env python

from __future__ import print_function

def execfile(f, c):
    with open(f) as h:
        code = compile(h.read(), f, 'exec')
        exec(code, c)

Assets = [
    ("logo.png", "LOGO"),
    ("cursor.png", "DEFAULT_CURSOR")
]

if __name__ == "__main__":
    contents = {}
    f = open("assets.tmp.py", "wb")
    for filename, varname in Assets:
        print("encoding %s into %s ..." % (filename, varname))
        contents[filename] = open(filename, "rb").read()
        data = contents[filename].encode('base64').replace('\n', '')
        brk = 247 - len(varname)
        while brk < len(data):
            data = data[:brk] + "\r\n" + data[brk:]
            brk += 256
        f.write('%s = """%s"""\r\n' % (varname, data))
    f.close()

    execfile("assets.tmp.py", globals())

    for filename, varname in Assets:
        print("verifying %s ..." % varname, end=' ')
        data = globals()[varname].decode('base64')
        if data == contents[filename]:
            print("OK")
        else:
            print("FAILED")
