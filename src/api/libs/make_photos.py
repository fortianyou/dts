#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import database

db = database.Database()
photos = []

for line in sys.stdin:
    try:
        line = line.strip()
        press, title, models, url = line.split("\t")
        p = url.split("/")[-1]
        cover = "{}/{}/{}".format(press, title.split("-")[0], p)
        params = {
            'press': press,
            'album_name': title,
            'url': cover,
        }
        photos.append(params)
    except:
        continue
print db.insert_photos(photos)
