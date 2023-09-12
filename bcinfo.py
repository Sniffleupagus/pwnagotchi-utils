#!/usr/bin/env python3
#
# bcinfo.py
#
# bettercap info fetcher, also restarts wifi.recon if it isn't running
# bcinfo.py connects to the bettercap API, so does not need to run as root.
# connects with default pwnagotchi:pwnagotchi user, pass.  change in code if
# you changed your bettercap user,password
#
# options:
# -w = fetch wifi APs
# -b = fetch BLE devices
# -h = fetch HID
#    only use one of -w, -b, -h. If not specified, it will fetch the whole bettercap session
# -q = quiet, just output # of APs, BLE, and/or HID devices instead of printing the whole shebang
#
# to keep bettercap wifi.recon running, even if bettercap crashes and restarts, add to
# crontab for the "pi" user, like:
#
# # check bettercap every 5 minutes:
# */5 *  *   *   *     /home/pi/bin/bcinfo.py -w -q >/dev/null 2>/dev/null#
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

def print_item(name, item, prefix=""):
    #print("%s[[[%s:%s]]]" % (prefix, name, type(item)))
    if type(item) is int: 
        print("%s%s = %s" % (prefix, name, item))
    elif type(item) is str: 
        if item.startswith("{"):
            #print("********************\n%s JSON %s" % (prefix, item))
            try:
                j = json.loads(item)
                print("%sJSON " % prefix, json.dumps(j, sort_keys=True,indent=4))
            except Exception as inst:
                print("%s%s = '%s'" % (prefix, name, item))
        else:
            print("%s%s = '%s'" % (prefix, name, item))
    elif type(item) is float: 
        print("%s%s = %s" % (prefix, name, item))
    elif type(item) is bool: 
        print("%s%s is %s" % (prefix, name, item))
    elif type(item) is list: 
        #if (prefix is ""): 
        if len(item) > 1: print("\n")
        print("%s[%s]" % (prefix, name))
        i = 0
        for key in item:
            i=i+1
            #print("%s<%i> %s" % (prefix, i, key))
            print_item("{%i}" % (i), key, "  %s %s" % (" " * len(prefix), name))

        if (prefix == ""): 
            print("%s[%s END]" % (prefix, name))

    elif type(item) is dict: 
        #print("\n")
        for key in item:
            #print("%s>>> %s:%s" % (prefix, key, type(item[key])))
            print_item("%s" % (key), item[key], "%s%s." % (prefix, name))
            #prefix = " " * len(prefix)
            #name = " " * len(name)
    else:
        try:
            print("%sUnknown type %s" % (prefix,name))
            print("*%s] %s %s" % (prefix, name, type(item)))
        except Exception as inst:
            print ("*%s] Error processing %s" % (prefix,name))
            print(prefix, type(inst))
            print(prefix, inst.args)
            print(prefix, inst)
    pass

async def _on_event(self, msg):
    found_handshake = False
    jmsg = json.loads(msg)
    print("GOT AN EVENT!!!")
    print_item("Event", jmsg)
    return
    
    if jmsg['tag'] == 'wifi.client.handshake':
        filename = jmsg['data']['file']
        sta_mac = jmsg['data']['station']
        ap_mac = jmsg['data']['ap']
        key = "%s -> %s" % (sta_mac, ap_mac)
        if key not in self._handshakes:
            self._handshakes[key] = jmsg
            s = self.session()
            ap_and_station = self._find_ap_sta_in(sta_mac, ap_mac, s)
            if ap_and_station is None:
                logging.warning("!!! captured new handshake: %s !!!", key)
                self._last_pwnd = ap_mac
                plugins.on('handshake', self, filename, ap_mac, sta_mac)
            else:
                (ap, sta) = ap_and_station
                self._last_pwnd = ap['hostname'] if ap['hostname'] != '' and ap[
                    'hostname'] != '<hidden>' else ap_mac
                logging.warning(
                    "!!! captured new handshake on channel %d, %d dBm: %s (%s) -> %s [%s (%s)] !!!",
                    ap['channel'],
                    ap['rssi'],
                    sta['mac'], sta['vendor'],
                    ap['hostname'], ap['mac'], ap['vendor'])
                plugins.on('handshake', self, filename, ap, sta)
            found_handshake = True
        self._update_handshakes(1 if found_handshake else 0)
                
def _event_poller(self, loop):
    print("polling events ...")
    
    while True:
        logging.debug("polling events ...")
        print("polling events ...")
        try:
            loop.create_task(self.start_websocket(self._on_event))
            loop.run_forever()
        except Exception as ex:
            logging.debug("Error while polling via websocket (%s)", ex)

def start_event_polling(self):
    # start a thread and pass in the mainloop
    _thread.start_new_thread(self._event_poller, (asyncio.get_event_loop(),))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:wbhgq", ["session='session'", "wifi", "ble", "hid", "gps"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    session = "session"
    user = "pwnagotchi"
    passwd = "pwnagotchi"
    quiet = False

    
    for o,a in opts:
        if o in ("-s", "--session"):
            session = a
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--password"):
            passwd = a
        elif o in ("-w", "--wifi"):
            session = "session/wifi"
        elif o in ("-b", "--ble"):
            session = "session/ble"
        elif o in ("-h", "--hid"):
            session = "session/hid"
        elif o in ("-g", "--gps"):
            session = "session/gps"
        elif o in ("-q", "--quiet"):
            quiet = True


    try:        
        connection = Client('localhost', port=8081, username=user, password=passwd);
    except Exception as err:
        print(err)
        sys.exit(3)
    #print("Got Here!")

    try:
        sess = connection.session()
    except Exception as err:
        print(err)
        sys.exit(3)

    try:
        
        #for mod in sess:
        #    print_item(mod, sess[mod])
        if not quiet:
            print("[Start %s]" % session)
            print_item("Session: %s" % session, sess)
            print("[End %s]" % session)
        
        apcount = 0
        if ("aps" in sess and len(sess["aps"]) == 0) or ("wifi" in sess and len(sess["wifi"]["aps"]) == 0):
            # no aps seen, so try turning it on, just in case
            result = connection.run("wifi.recon on")
            print("Turned it back on: %s" % repr(result))
        else:
            if "wifi" in sess:
                print("Found %d aps." % (len(sess["wifi"]["aps"])))
            elif "aps" in sess:
                print("Found %d aps." % (len(sess["aps"])))

        if "ble" in sess: # fix for -b, where "devices" is the top level index
            print("Found %d BLE devices." % (len(sess["ble"]["devices"])))

        if "hid" in sess:
            print("Found %d HID devices" % (len(sess["hid"]["devices"])))
                
             
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)

        
    #start_event_polling

    #print("Waiting for a bit")
    #time.sleep(30)

if __name__ == "__main__":
    main()
