# pwnagotchi-utils
Utilities to support pwnagotchi

- bcinfo.py

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

<code># check bettercap every 10 minutes:
*/10 *  *   *   *     /home/pi/bin/bcinfo.py -w -q >/dev/null 2>/dev/null
</code>


- bccmd.py

send commands to bettercap. either on the command line, or as input with -i. -q for quiet

<code>bccmd.py wifi.recon off
echo "wifi.recon off" | bccmd.py -i
bccmd.py -iq <<EOS
wifi.recon off
wifi.clear
EOS</code>

- fix_mon0

shell script that uses bccmd.py and /usr/bin/pwnlib to pause bettercap wifi.recon, reload the
wifi driver and mon0, then continue wifi.recon
