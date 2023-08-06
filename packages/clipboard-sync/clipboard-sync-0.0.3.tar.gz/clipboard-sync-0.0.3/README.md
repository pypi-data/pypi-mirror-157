clipboard-sync
--------------

A simple tool to synchronize server and client clipboards


If you have a development server and you usually log in to the development machine via ssh for development, then you must encounter the problem that the development machine and the clipboard in the client you are using cannot be synchronized, and this tool exists to solve this problem

Here's how I did it:

My client is a macOS and my development server is a Ubuntu.

## MacOS (Development Client)

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

### 2. Test X Window

Log in your deployment server (on my side, the host is `dev`)

```bash
ssh dev
```

Launch xeyes in your deployment server

```bash
xeyes
```

You'll see a pop-up window on your macOS that contains a pair of eyes

### 3. Enable X11 Forwarding and RemoteForward

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

### 4. Install clipboard-sync

```bash
pip install clipboard-sync
```

### 5. Install serviceman to create a daemon service

```
curl -sS https://webinstall.dev/serviceman | bash
```

```bash
mkdir -p clipboard_sync && cd clipboard_sync && env PATH="$PATH" serviceman add clipboard-sync --remote-host=dev --remote-port=5557 --host=0.0.0.0 --port=5556
```

## Ubuntu (Development Server)

### 1. Enable X11Forward in the sshd configuration file


```
```
