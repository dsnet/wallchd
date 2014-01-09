# Gnome3 Wallpaper Changer Daemon #

## Introduction ##

A very simple wallpaper changing daemon designed to work with Gnome3. Most of
the wallpaper changing daemons either failed to operate as a daemon or required
a GUI to configure. As such, I decided to write my own simple wallpaper changer
daemon based around the command:
```gsettings set org.gnome.desktop.background picture-uri file://image/path```.

This script was developed until the point where "it worked for me". Much error
checking was ignored and a lot of assumptions were made throughout the code.

I have no idea if this daemon will work on a multi-user desktop enviroment. For
one, I assumed there was only one user (id 1000) and hard-coded that user to be
the owner of the daemon in the init.d script.

Feel free to modify the scripts as you see fit.

## Files ##

* wallch: Script to signal daemon to switch wallpapers
* wallchd: Init.d script to start the wallchd service
* wallchd.json: Configuration settings for wallchd
* wallchd.py: The wallpaper changing daemon

## Installation ##

```bash
# Be root to install
su

# Download the archive
SRC_VERSION=tip
curl http://code.digital-static.net/wallchd/get/$SRC_VERSION.tar.gz | tar -zxv

# Move local copy
SRC_ROOT=/usr/local/wallchd
mv *-wallchd-* $SRC_ROOT

# Update configuration file
nano $SRC_ROOT/wallchd.json

# Link scripts
ln -s $SRC_ROOT/wallch /usr/local/bin/
ln -s $SRC_ROOT/wallchd /etc/init.d/

# Setup the daemon service
update-rc.d wallchd defaults
service wallchd start
```
