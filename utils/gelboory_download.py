import os
import urllib.request
from xml.etree import ElementTree

import requests


WORD = 'horse'
FOLDER = 'horse'
API_URL = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags=" + WORD


if __name__ == "__main__":
    urls = []
    print("Loading gelbooru.com...")

    root = ElementTree.parse(urllib.request.urlopen(API_URL)).getroot()
    posts = root.findall('post')
    for post in posts:
        url = post.attrib['file_url']
        urls.append(url)

    ll = len(urls)
    for i, url in enumerate(urls):
        file_name = url.split('/').pop()
        if os.path.isfile(os.path.join('res', FOLDER, file_name)):
            print(f"Skipping {i+1}/{ll} (already exists): {file_name}")
            continue
        ext = file_name.split('.').pop()
        if ext not in {'jpg', 'jpeg'}:
            print(f"Skipping {i+1}/{ll} (ext is {ext}): {file_name}")
            continue
        print(f"Downloading {i+1}/{ll}: {file_name}... ", end='')
        response = requests.get(url, stream=True)
        if not response.ok:
            print(response)
        else:
            with open(os.path.join('res', FOLDER, file_name), 'wb') as fp:
                fp.write(response.content)
                print('Done!')
