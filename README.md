# pwnagotchi-utils
Utilities to support pwnagotchi

bcinfo.py

bettercap info fetcher, also restarts wifi.recon if it isn't running
bcinfo.py connects to the bettercap API, so does not need to run as root.
connects with default pwnagotchi:pwnagotchi user, pass.  change in code if
you changed your bettercap user,password

options:
   -w = fetch wifi APs
   -b = fetch BLE devices
   -h = fetch HID
   only use one of -w, -b, -h. If not specified, it will fetch the whole bettercap session

   -q = quiet, just output # of APs, BLE, and/or HID devices instead of printing the whole shebang

To keep bettercap wifi.recon running, even if bettercap crashes and restarts, add to
crontab for the "pi" user, like:

# check bettercap every 10 minutes:
*/10 *  *   *   *     /home/brian/bcinfo.py -w -q >/dev/null 2>/dev/null#

