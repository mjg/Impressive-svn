#!/usr/bin/env python3
import sys
import os
import py_compile
import zipfile
import subprocess
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--compile", action='store_true',
                        help="compile to bytecode first")
    parser.add_argument("srcfile", nargs='?', default="impressive.py",
                        help="source file name")
    parser.add_argument("exefile", nargs='?', default="impressive:",
                        help="executable file name [':' = Python version 2/3; default: $(default)s]")
    args = parser.parse_args()

    if args.compile:
        pyc = py_compile.compile(args.srcfile) or args.srcfile.replace(".py", ".pyc")

    pythonver = str(sys.version_info[0])
    exefile = args.exefile.replace(':', pythonver)
    with open(exefile, 'wb') as f:
        f.write(b'#!/usr/bin/env python' + pythonver.encode() + b'\n')
    
    with zipfile.ZipFile(exefile, 'a', zipfile.ZIP_DEFLATED) as f:
        if args.compile:
            f.write(pyc, "__main__.pyc")
        else:
            f.write(args.srcfile, "__main__.py")

    os.chmod(exefile, 0o755)
