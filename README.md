# Gnome3 Wallpaper Changer Daemon #

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
