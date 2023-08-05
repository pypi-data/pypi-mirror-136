[![GitHub release](https://img.shields.io/github/v/release/elesiuta/picosnitch?color=00a0a0)](https://github.com/elesiuta/picosnitch/releases)
[![PyPI release](https://img.shields.io/pypi/v/picosnitch?color=00a0a0)](https://pypi.org/project/picosnitch)
[![AUR release](https://img.shields.io/aur/version/picosnitch?color=00a0a0)](https://aur.archlinux.org/packages/picosnitch/)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/elesiuta/picosnitch/latest/master?color=00a0a0)](https://github.com/elesiuta/picosnitch/commits/master)
[![GitHub contributors](https://img.shields.io/github/contributors/elesiuta/picosnitch?color=00a0a0)](https://github.com/elesiuta/picosnitch/graphs/contributors)
[![File size](https://img.shields.io/github/size/elesiuta/picosnitch/picosnitch.py?color=00a0a0)](https://github.com/elesiuta/picosnitch/blob/master/picosnitch.py)
[![PyPI monthly downloads (without mirrors)](https://img.shields.io/pypi/dm/picosnitch?color=00a0a0&label=downloads%20%28pypistats%29)](https://pypistats.org/packages/picosnitch)
[![PyPI total downloads](https://img.shields.io/badge/dynamic/json?color=00a0a0&label=downloads%20%28pepy%29&query=total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Fpicosnitch)](https://pepy.tech/project/picosnitch)
[![GitHub downloads](https://img.shields.io/github/downloads/elesiuta/picosnitch/total?color=00a0a0&label=downloads%20%28github%29)](https://github.com/elesiuta/picosnitch/releases)

# [picosnitch](https://elesiuta.github.io/picosnitch/)
![screenshot.png](https://raw.githubusercontent.com/elesiuta/picosnitch/master/docs/screenshot.png)
- An extremely simple, reliable, and lightweight program for linux to help protect your privacy
- It monitors your system and notifies you whenever it sees a new program that connects to the network
- Or when the sha256 changes for one of those programs (can also check [VirusTotal](https://www.virustotal.com))
  - by hashing executables, picosnitch can provide more reliable intrusion detection since different executables can appear to be located on the same path
  - for example, it can successfully identify whether curl being run from inside a docker container is the same or different from curl being run on your system, even if they both appear to be located at /usr/bin/curl (or if another program is masquerading as curl)
  - to improve performance, hashes are cached based on the device and inode of the executable, and watched with fanotify to trigger a rehash if the executable is modified
- Featuring a curses based UI for browsing past connections
- And can monitor your bandwidth, breaking down traffic by time, executable, hash, domain, port, user
- For advanced users who know what should be running on their system, and when they should be making network connections
  - only you can decide which programs to trust, and what actions to take for offending programs
  - picosnitch is purely a monitoring and detection tool, focussing on doing one thing well, so blocking or sandboxing programs is out of scope
  - running untrustworthy programs should only be done in an isolated environment and you should always have good backups in order to recover, picosnitch can only help you detect if your system becomes compromised or if something breaks your trust
  - you may want to watch picosnitch logs with another program to automatically take actions such as blocking connections, terminating the offending program, and emailing the log if this is a server
  - picosnitch can be used with any other firewall tool and does not impact performance since it only monitors connections and does not intercept them
- Inspired by programs such as GlassWire, Little Snitch, and OpenSnitch

# [installation](#installation)

### [PPA](https://launchpad.net/~elesiuta/+archive/ubuntu/picosnitch) for Ubuntu and derivatives
- `sudo add-apt-repository ppa:elesiuta/picosnitch`
- `sudo apt update`
- `sudo apt install picosnitch`

### [AUR](https://aur.archlinux.org/packages/picosnitch/) for Arch and derivatives
- install `picosnitch` [manually](https://wiki.archlinux.org/title/Arch_User_Repository#Installing_and_upgrading_packages) or using your preferred [AUR helper](https://wiki.archlinux.org/title/AUR_helpers)

### [PyPI](https://pypi.org/project/picosnitch/) for any Linux distribution with Python >= 3.8
- install the [BPF Compiler Collection](https://github.com/iovisor/bcc/blob/master/INSTALL.md) python package for your distribution
  - it should be called `python-bcc` or `python-bpfcc`
- install picosnitch using [pip](https://pip.pypa.io/)
  - `pip3 install "picosnitch[full]" --upgrade --user`
- create a service file for systemd to run picosnitch (recommended)
  - `picosnitch systemd`
- optional dependencies (should already be installed or install automatically)
  - for notifications: `dbus-python`, `python-dbus`, or `python3-dbus` (name depends on your distro)
  - for VirusTotal: `python-requests`

# [usage](#usage)
- running picosnitch
  - enable/disable autostart on reboot with `systemctl enable|disable picosnitch`
  - start/stop/restart with `systemctl start|stop|restart picosnitch`
  - or if you don't use systemd `picosnitch start|stop|restart`
- user interface for browsing past connections
  - start with `picosnitch view`
  - `space/enter`: filter on entry `backspace`: remove filter `h/H`: cycle through history `t/T`: cycle time range `u/U`: cycle byte units `r`: refresh view `q`: quit
- show usage with `picosnitch help`

# [configuration](#configuration)
- config is stored in `~/.config/picosnitch/config.json`
  - restart picosnitch if it is currently running for any changes to take effect

```yaml
{
  "Bandwidth monitor": true, # Log traffic per connection since last db write
  "DB retention (days)": 365, # How many days to keep connection logs in snitch.db
  "DB sql log": true, # Write connection logs to snitch.db
  "DB text log": false, # Write connection logs to conn.log
  "DB write limit (seconds)": 10, # Minimum time between writing connection logs
  # increasing it decreases disk writes by grouping connections into larger time windows
  # reducing time precision, decreasing database size, and increasing hash latency
  "Desktop notifications": true, # Try connecting to dbus to show notifications
  "Every exe (not just conns)": false, # Check every running executable with picosnitch
  # these are treated as "connections" with a port of -1
  # this feature is experimental but should work fairly well, errors should be expected as
  # picosnitch is unable to open file descriptors for some extremely short-lived processes
  "Log addresses": true, # Log remote addresses for each connection
  "Log commands": true, # Log command line args for each executable
  "Log ignore": [], # List of hashes (str), domains (str), or ports (int)
  # will omit connections that match any of these from the connection log
  # domains will match any that start with the provided string, hashes or ports are exact
  # the process name, executable, and hash will still be recorded in record.json
  "Set RLIMIT_NOFILE": null, # Set the maximum number of open file descriptors (int)
  # it is used for caching process executables and hashes (typical system default is 1024)
  # this is good enough for most people since caching is based on executable device + inode
  # fanotify is used to detect if a cached executable is modified to trigger a hash update
  "VT API key": "", # API key for VirusTotal, leave blank to disable (str)
  "VT file upload": false, # Upload file if hash not found, only hashes are used by default
  "VT request limit (seconds)": 15 # Number of seconds between requests (free tier quota)
}
```

# [logging](#logging)
- a log of seen executables is stored in `~/.config/picosnitch/exe.log`
  - this is a history of your notifications
- a record of seen executables is stored in `~/.config/picosnitch/record.json`
  - this is used for determining whether to create a notification
  - it contains known process name(s) by executable, executable(s) by process name, and sha256 hash(es) with VirusTotal results by executable
- the full connection log is stored in `~/.config/picosnitch/snitch.db`
  - this is used for `picosnitch view`
  - note, connection times are based on when the group is processed, so they are accurate to within `DB write limit (seconds)` at best, and could be delayed if the previous group is slow to hash
  - notifications are handled by a separate subprocess, so they are not subject to the same delays as the connection log
- if `DB text log` is enabled, the full connection log is also written to `~/.config/picosnitch/conn.log`
  - this may be useful for watching with another program
  - it contains the following fields, separated by commas (commas, newlines, and null characters are removed from values)
  - `executable,name,cmdline,sha256,time,domain,ip,port,uid,conns,sent,received`
- the error log is stored in `~/.config/picosnitch/error.log`
  - errors will also trigger a notification and are usually caused by far too many or extremely short-lived processes/connections, or suspending your system while a new executable is being hashed
  - for most people in most cases, this should raise suspicion that some other program may be misbehaving
  - to improve reliability, picosnitch opens file descriptors to every executable once seen running, and will try deferring to the parent process if the child was too short-lived, logging the connection as coming from "/path/of/parent_exe (child)"

# [building from source](#building-from-source)
- install dependencies listed under [installation](#installation)
- install `python-setuptools`
- install picosnitch with `python setup.py install --user`
- see other options with `python setup.py [build|install] --help`
- you can also run the script `picosnitch.py` directly
