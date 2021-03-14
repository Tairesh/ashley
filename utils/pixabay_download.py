import json
import os

import requests


WORD = 'horse'
FOLDER = 'horse'
API_URL = "https://pixabay.com/api/?key=%KEY%&min_width=200&min_height=200&per_page=200&page={}&q=" + WORD


if __name__ == "__main__":
    with open(os.path.join('config', 'api_keys.json'), 'r') as fp:
        secrets = json.load(fp)
        API_URL = API_URL.replace('%KEY%', secrets['pixabay_apikey'])

    urls = []
    page = 1
    pages = 1
    while page <= pages:
        print(f'Loading page {page}...', end='')
        data = json.loads(requests.get(API_URL.format(page)).content.decode('utf-8'))
        if data['totalHits'] > 0:
            for hit in data['hits']:
                urls.append(hit['largeImageURL'])
            pages = data['totalHits'] // 200 + 1
        print('Done!')
        page += 1

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
