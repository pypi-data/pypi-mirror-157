from os.path import exists
from sys import exit, platform
import screeninfo

from . import images

if platform.startswith('win'):
    # Windows
    import ctypes

elif platform.startswith('dar'):
    # Mac OS
    from subprocess import Popen, PIPE

elif platform.startswith('lin'):
    # Linux
    from os import system

else:
    print(f"Unsupported platform: {platform}")
    exit(1)


def set_background(filename):
    """ Sets the background for any OS.
    The filename must be a full path starting with '/'
    """
    if not exists(filename):
        print(f"Error: {filename} missing or not a file.")
        return

    print(f"Setting background to {filename}")

    if platform == 'darwin':
        SCRIPT = ("/usr/bin/osascript -e "
                  "'"
                  'tell application "System Events" '
                  'to set picture of every desktop to '
                  f'("{filename}" as POSIX file)'
                  "'")
        Popen(SCRIPT, shell=True)

    elif platform.startswith('win'):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, filename, 3)

    elif platform.startswith('lin'):
        SCRIPT = "gsettings set org.gnome.desktop.background picture-uri file://{}".format(
            filename)
        system(SCRIPT)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="search query", type=str)
    parser.add_argument("--monitors", help="monitors", type=str)
    parser.add_argument("--no-set", help="don't set as wallpaper (just save image)",
                        dest='set_wallpaper', action='store_false')
    parser.set_defaults(set_wallpaper=True)
    args = parser.parse_args()

    monitors = []
    x = 0
    if args.monitors:
        for token in args.monitors.split(","):
            print("token:", token)
            s = token.split("x")
            w = int(s[0])
            h = int(s[1])
            print("w", w)
            print("h", h)
            monitor = screeninfo.Monitor(x, 0, w, h)
            x = x + w
            print(monitor)
            monitors.append(monitor)
    else:
        monitors = screeninfo.get_monitors()
        # If there are any negative coordinates, add them so they're positive.
        while True:
            lowest_x = min([monitor.x for monitor in monitors])
            if lowest_x < 0:
                for monitor in monitors:
                    monitor.x -= lowest_x
                continue
            lowest_y = min([monitor.y for monitor in monitors])
            if lowest_y < 0:
                for monitor in monitors:
                    monitor.y -= lowest_y
                continue
            # No negative coordinates.
            break

    pics = images.get_images(monitors, query=args.query)
    if pics:
        wallpaper = images.stitch_images(monitors, pics)
        if args.set_wallpaper:
            set_background(wallpaper)
        else:
            print("Saved image:")
            print(wallpaper)

    else:
        print(f"Failed to get pictures")
