#!/usr/bin/env python3
#
# bccmd.py [-q] bettercap command
#
# run a command in bettercap
#
# options:
# -q = quiet, no output except errors
#
# Example:
#
# % bccmd.py wifi.recon on
# Command lin: 'wifi.recon on'
# Result: {'success': True, 'msg':''}
# %
#

import time
import os
import re
import json
import asyncio
import _thread
import logging
import getopt, sys

from pwnagotchi.bettercap import Client

###
### main()
###

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "iqu:p:", ["interactive", "quiet", "user='pwnagotchi'", ])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    command = " ".join(args)
    inputcmds=False
    user = "pwnagotchi"
    passwd = "pwnagotchi"
    quiet = False

    
    for o,a in opts:
        if o in ("-i", "--interactive"):
            inputcmds = True
            command = "#interactive"
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--password"):
            passwd = a
        elif o in ("-q", "--quiet"):
            quiet = True

    try:        
        connection = Client('localhost', port=8081, username=user, password=passwd);
    except Exception as err:
        print(err)
        sys.exit(3)

    try:
        if inputcmds:
            prompt = "" if quiet else "> "
            while command != "":
                try:
                    command = input(prompt)
                except EOFError as e:
                    sys.exit(0)
                    
                if command != "":
                    try:
                        result = connection.run(command)
                        if not quiet: print(repr(result))
                    except Exception as e:
                        if not quiet: print(repr(e))
        else:
            if not quiet:
                print("Command line: %s" % repr(command))
            result = connection.run(command)
            if not quiet:
                print("Result: %s" % repr(result))

    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)

        
if __name__ == "__main__":
    main()
