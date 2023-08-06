from os import getcwd, makedirs, remove
from os.path import basename, dirname, isdir, isfile, splitext
from urllib.request import urlopen

from PIL import Image
from unsplash.api import Api
from unsplash.auth import Auth
from unsplash.photo import Photo
from unsplash.errors import UnsplashError

import shutil

# Unsplash configuration
# Split strings to fight git scraping bots
_client_id = "cd356c3b262be554770bea925ce5119f"
_client_secret = "de43ef85676f1d417574938c19d89346"
_client_id += "0503605b31a6dc4f3e9365babfd1674c"
_client_secret += "7503fbe3ba9c89ada24192c5aa881eff"
_redirect_uri = ""
_code = ""
api = Api(Auth(_client_id, _client_secret, _redirect_uri, code=_code))

IMAGE_DIR = f"{getcwd()}/images"
CURRENT_IMAGE_DIR = f"{IMAGE_DIR}/current"


def download(photo):
    """ Downloads image from a url to the filepath """
    if not isdir(dirname(photo.filepath)):
        makedirs(dirname(photo.filepath))
    if isfile(photo.filepath):
        print(f"File {photo.filepath} already exists, using cached image")
        pass
    else:
        with open(photo.filepath, "wb") as f:
            f.write(urlopen(photo.urls.raw).read())


def unsplash_get_image(width, height, query="wallpaper"):
    """ Downloads random photos and returns a list of filepaths """
    directory = IMAGE_DIR + '/unsplash'
    try:
        results = api.photo.random(w=width, h=height, query=query)
    except UnsplashError as e:
        print("Failed to get random image:", e)
        return None

    photo = results[0]

    photo.filepath = f"{directory}/{photo.id}.jpg"

    if isfile(photo.filepath):
        print(f"Photo already downloaded: {photo.filepath}")
    else:
        download(photo)

    print(photo.width, photo.height)
    # Print author info
    print(f"Image found from random({width}x{height} q={query})")
    print(f" -- Description: {photo.description}")
    print(f" -- Artist: {photo.user.name}")
    print(f" -- Artist Profile: https://unsplash.com/@{photo.user.id}")
    print(f" -- Full Image: {photo.urls.raw}")

    return photo


def get_images(dimensions, source="unsplash", query="wallpaper"):
    """ Downloads images

    Args:
        dimensions:  List of dicts containing width/height attributes
        source:      Name of the image source
    Sources:
        'unsplash'       -  unsplash.com
        'mikedrawsdota'  -  wallpapers.mikedrawsdota.com
    """
    images = []

    # Default query.
    if query is None:
        query = "wallpaper"

    for monitor in dimensions:
        if source == 'unsplash':
            photo = unsplash_get_image(
                monitor.width, monitor.height, query=query)

            images.append(photo)

    return images


def resize_photo(photo, width, height):
    """ Resizes a photo to the desired width/height

    Args:
        photo:  PIL Image
        width:  Desired width
        height: Desired height
    """
    # If the photo is too big.
    if photo.width > width or photo.height > height:
        # Find the ratio to scale the image with.
        w_ratio = width / photo.width
        h_ratio = height / photo.height
        # Find the bigger ratio so we don't scale too small.
        ratio = max(w_ratio, h_ratio)
        # Calculate new size.
        w = int(photo.width * ratio)
        h = int(photo.height * ratio)
        # Resize the image.
        print(f"Resizing image from {photo.width}x{photo.height} to {w}x{h}")
        photo = photo.resize((w, h), Image.BICUBIC)

    # If the photo is still too big
    if photo.width > width or photo.height > height:
        # Crop the image in the middle.
        left = (photo.width - width)/2
        top = (photo.height - height)/2
        right = photo.width - ((photo.width - width)/2)
        bottom = photo.height - ((photo.height - height)/2)
        photo = photo.crop((left, top, right, bottom))

    return photo


def stitch_images(monitors, images):
    """ Combines a list of images into one image and returns the filepath

    Args:
        monitors:  List of Monitors with height/width attributes
        images:    List of image file paths
    """
    filename = ""
    for image in images:
        base = basename(image.filepath)
        filename += splitext(base)[0] + '_'

    filepath = CURRENT_IMAGE_DIR + '/' + filename + '.jpg'
    print(f"Stiching images:")
    for image in images:
        print(f" - {image.filepath}")

    # Find the canvas size.
    width = max([monitor.x + monitor.width for monitor in monitors])
    height = max([monitor.y + monitor.height for monitor in monitors])

    # Create the canvas.
    img = Image.new('RGB', (width, height))
    print(f"Created image canvas ({width}x{height})")

    # Paste the photos on the monitor coordinates.
    for image, monitor in zip(images, monitors):
        print(f"image: {image} monitor: {monitor}")
        with Image.open(image.filepath) as photo:
            photo = resize_photo(photo, monitor.width, monitor.height)
            print(
                f"img.paste({photo} ({photo.width}, {photo.height}), ({monitor.x}, {monitor.y}))")
            img.paste(photo, (monitor.x, monitor.y))

    # Clean old files before saving new pic
    if isdir(CURRENT_IMAGE_DIR):
        shutil.rmtree(CURRENT_IMAGE_DIR)
    makedirs(CURRENT_IMAGE_DIR)
    img.save(filepath)

    return filepath
