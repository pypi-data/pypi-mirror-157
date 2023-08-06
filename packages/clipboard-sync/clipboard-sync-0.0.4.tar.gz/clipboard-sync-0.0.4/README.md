clipboard-sync
--------------

A simple tool to synchronize server and local clipboards

If you have a development server and you usually log in to the development server via ssh for development, then you must have encountered a bad situation where the development server and the local clipboard could not be synchronized, and this tool exists to solve this problem.

# Quickstart

Here's how I did it:

My local machine is a macOS and my development server is a Ubuntu.

## MacOS (Local)

### 1. Install XQuartz

```bash
brew install --cask xquartz
```

Then restart your computer

```bash
sudo reboot
```

After restarting, your DISPLAY environment variable will look like the following

```bash
$ echo $DISPLAY
/private/tmp/com.apple.launchd.ptuabljj5Y/org.xquartz:0
```

### 2. Enable X11 Forwarding and RemoteForward

```bash
vim ~/.ssh/config
```

add configuration for your development server host (on my side, it is `dev`) like this:

```
Host dev
    User yetone
    ForwardX11 yes
    ForwardX11Trusted yes
    RemoteForward 5556 localhost:5556
```

### 3. Test X Window

Log in your deployment server (on my side, the host is `dev`):

```bash
ssh dev
```

Install xeyes:

```bash
sudo apt-get install -y x11-apps
```

Launch xeyes in your deployment server:

```bash
xeyes
```

You'll see a pop-up window on your macOS that contains a pair of eyes like this:

![xeyes](statics/xeyes.png)

### 4. Install clipboard-sync on the local side (macOS)

```bash
pip install clipboard-sync
```

### 5. Create a daemon service on the local side (macOS)

Install serviceman:

```
curl -sS https://webinstall.dev/serviceman | bash
```

Create service with serviceman:

```bash
env PATH="$PATH" serviceman add -n clipboard-sync clipboard-sync --remote-host=dev --remote-port=5557 --host=0.0.0.0 --port=5556
```

## Ubuntu (Server)

### 1. Enable X11Forwarding for ssh server

Opend sshd configuration file:

```bash
sudo vim /etc/ssh/sshd_config
```

Uncomment or add the following lines:

```
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes
```

Restart the sshd service:

```bash
sudo systemctl restart sshd
```

### 2. Install xclip

```bash
sudo apt-get install -y xclip
```

### 3. Install clipboard-sync

```bash
pip install clipboard-sync
```

### 4. Create a daemon service

Install serviceman:

```
curl -sS https://webinstall.dev/serviceman | bash
```

Create service with serviceman:

```bash
env PATH="$PATH" serviceman add -n clipboard-sync clipboard-sync --remote-host=localhost --remote-port=5556 --host=0.0.0.0 --port=5557 --display=$DISPLAY
```

# Troubleshooting

## 1. Can't copy/paste in (neo)vim

Set your `clipboard` to `unname` and `unnameplus`:

```
set clipboard^=unnamed,unnamedplus
```
