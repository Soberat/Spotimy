import os.path

import requests
from PyQt5.QtGui import QPixmap
import json


def get_image(uri: str):
    if not os.path.exists('./cache/.imgcache'):
        fi = open('./cache/.imgcache', 'w')
        json.dump({}, fi)
        fi.close()

    with open('./cache/.imgcache', 'r') as cacheFile:
        cache = json.load(cacheFile)
        if uri in cache.keys():
            image = QPixmap()
            with open(f"./cache/img/{cache[uri]}", 'rb') as file:
                image.loadFromData(file.read())
                return image
        else:
            data = requests.get(uri, stream=True).raw.read()
            with open(f"./cache/img/{hash(data)}", 'wb') as file:
                file.write(data)
            cache[uri] = hash(data)
            image = QPixmap()
            image.loadFromData(data)
    with open('./cache/.imgcache', 'w') as cacheFile:
        json.dump(cache, cacheFile)
        return image
