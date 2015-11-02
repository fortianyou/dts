#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import wget
import requests
import os
from bs4 import BeautifulSoup as bs


host = 'http://www.zngirls.com'

def get_albums(index_url):
    total_pages = 1
    page = 1
    while page <= total_pages:
        url = os.path.join(index_url, '{}.html'.format(page))
        text = requests.get(url).text
        soup = bs(text, "lxml")

        if page == 1:
            # total page
            navi = soup.find('div', {'class': 'pagesYY'})
            pages = navi.find_all('a')
            pages = [x.text for x in pages]
            total_pages = int(pages[-2])

        # albums
        it = soup.find('a', {'class': 'galleryli_link'})
        while it:
            cover = it.img.get('data-original')
            title = it.img.get('title')
            link = it.get('href')
            yield cover, title, link

            it = it.find_next('a', {'class': 'galleryli_link'})

        page += 1


def download_img(url):
    text = requests.get(url).text
    soup = bs(text, "lxml")

    # total
    total = soup.find('span', {'style': 'color: #DB0909'}).text
    total = total[: -3]
    total = int(total)

    # title
    title = soup.find('h1', {'id': 'htilte'}).text

    url_pattern = soup.find('ul', {'id': 'hgallery'})
    url_pattern = url_pattern.img.get('src').replace('/0.jpg', '/{:03d}.jpg')
    print title
    if os.path.exists(title):
        return

    os.mkdir(title)
    for i in xrange(total):
        file_url = url_pattern.format(i)
        file_name = "{:03d}.jpg".format(i)
        output_file = os.path.join(title, file_name)
        if i == 0:
            file_url = file_url.replace("000", "0")
        wget.download(file_url, out=output_file)


def main():
    url = 'http://www.zngirls.com/gallery/bomb/'
    albums = get_albums(url)
    for index, (cover, title, link) in enumerate(albums):
        url = host + link
        download_img(url)


if __name__ == '__main__':
    main()
