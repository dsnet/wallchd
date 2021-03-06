#!/usr/bin/env python

# Written in 2012 by Joe Tsai <joetsai@digital-static.net>
#
# ===================================================================
# The contents of this file are dedicated to the public domain. To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

import re
import os
import json
import shlex
import random
import signal
import getpass
import threading
import subprocess


################################################################################
############################### Global variables ###############################
################################################################################

# System configurations
ROTATE_CMD = 'gsettings set org.gnome.desktop.background picture-uri file://%s'
DEVNULL = open(os.devnull, 'wb')

# Regex patterns
REGEX_IMAGE = r'\.(png|jpg|jpeg)$'

wallpaper_path = None
rotate_delay = None
sleep_event = threading.Event()
terminate = False
images = []


################################################################################
############################### Helper functions ###############################
################################################################################

def interrupt_handler(sig_num, frame):
    """Handle system signal interrupts"""
    global terminate
    if sig_num != signal.SIGUSR1:
        terminate = True
    sleep_event.set()


def shell_escape(cmd):
    """Trivial shell escaping of a command"""
    return "'" + cmd.replace("'", "'\\''") + "'"


def load_images():
    """Reload images from source directory"""
    global images, wallpaper_path
    images = []
    for img in os.listdir(wallpaper_path):
        if re.search(REGEX_IMAGE, img, re.IGNORECASE):
            images.append(os.path.join(wallpaper_path, img))


################################################################################
################################# Script start #################################
################################################################################

if __name__ == "__main__":
    # Load the configuration file
    configs = None
    for path in [os.getcwd(), os.path.dirname(os.path.realpath(__file__))]:
        config_path = os.path.join(path, 'wallchd.json')
        if os.path.exists(config_path):
            with open(config_path) as conf_file:
                configs = json.loads(conf_file.read())
            break
    wallpaper_path = configs['wallpaper_path']
    rotate_delay = configs['rotate_delay']

    # Handle signals
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)
    signal.signal(signal.SIGUSR1, interrupt_handler)

    # Main event loop
    cycle_err = False
    while not terminate:
        if cycle_err:
            sleep_event.wait(5)
            sleep_event.clear()
        cycle_err = True

        # TODO(jtsai): Only reload images if the directory has been changed.
        try:
            load_images()
        except OSError:
            continue

        # HACK(jtsai): We need to get the DBUS_SESSION_BUS_ADDRESS in order for
        #   Gnome settings command to properly work. For this hack, we pull the
        #   D-Bus session from the environments of the actively running
        #   gnome-session under the current user that wallchd is running under.
        SESSION_REGEX = r'/(gnome|cinnamon)-session(\s+|$)'
        DBUS_REGEX = r'^DBUS_SESSION_BUS_ADDRESS=(.*)'
        dbus_addr = None
        for pid in [x for x in os.listdir('/proc') if x.isdigit()]:
            try:
                exe = os.path.realpath('/proc/%s/exe' % pid)
            except OSError:
                continue
            if re.search(SESSION_REGEX, exe):
                with open('/proc/%s/environ' % pid) as envs:
                    for env in envs.read().split('\0'):
                        res = re.search(DBUS_REGEX, env)
                        if res:
                            dbus_addr = res.groups()[0]
        if dbus_addr is None:
            continue
        os.environ['DBUS_SESSION_BUS_ADDRESS'] = dbus_addr
        os.environ['DISPLAY'] = ':0'

        # Change the background image
        image_path = shell_escape(random.choice(images))
        cmd_str = ROTATE_CMD % image_path
        cmd = shlex.split(cmd_str)
        subprocess.Popen(cmd, stdout = DEVNULL, stderr = DEVNULL).wait()

        # Sleep rotation delay
        sleep_event.wait(rotate_delay)
        sleep_event.clear()
        cycle_err = False
