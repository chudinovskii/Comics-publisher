import requests
import os
import random
from dotenv import load_dotenv


def get_current_comics_quantity():
    url = 'https://xkcd.com/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()
    decoded_resp = resp.json()
    comics_quantity = int(decoded_resp['num'])
    return comics_quantity


def get_comics_url_and_title(comics_quantity):
    comics_number = random.randint(1, comics_quantity)
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()
    decoded_resp = resp.json()
    title = decoded_resp['alt']
    url_for_img = decoded_resp['img']
    return title, url_for_img, comics_number


def download_pic(url, comics_number):
    resp = requests.get(url)
    resp.raise_for_status()
    filename = f'comics_{comics_number}.png'
    with open(filename, 'wb') as file:
        file.write(resp.content)
    return filename


def upload_pic(upload_url, filename):
    with open(filename, 'rb') as file:
        url = upload_url
        files = {
            'photo': file
        }
        resp = requests.post(url, files=files)
        resp.raise_for_status()
        decoded_resp = resp.json()
        if 'error' in decoded_resp:
            raise requests.exceptions.HTTPError(decoded_resp['error'])
        else:
            photo, server, hash = decoded_resp['photo'], decoded_resp['server'], decoded_resp['hash']
            return photo, server, hash


def get_wall_upload_server(access_token, vk_group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': access_token,
        'group_id': vk_group_id,
        'v': 5.107
    }
    resp = requests.get(url, params=payload)
    resp.raise_for_status()
    decoded_resp = resp.json()
    if 'error' in decoded_resp:
        raise requests.exceptions.HTTPError(decoded_resp['error'])
    else:
        upload_url = decoded_resp['response']['upload_url']
        return upload_url


def save_wall_photo(access_token, vk_group_id, photo, server, hash):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': access_token,
        'group_id': vk_group_id,
        'photo': photo,
        'server': server,
        'hash': hash,
        'v': 5.107
    }
    resp = requests.post(url, params=payload)
    resp.raise_for_status()
    decoded_resp = resp.json()
    if 'error' in decoded_resp:
        raise requests.exceptions.HTTPError(decoded_resp['error'])
    else:
        media_id, owner_id = decoded_resp['response'][0]['id'], decoded_resp['response'][0]['owner_id']
        return media_id, owner_id


def make_wall_post(access_token, vk_group_id, title, media_id, owner_id):
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': access_token,
        'v': 5.107,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'message': title,
        'attachments': f'photo{owner_id}_{media_id}'
    }
    resp = requests.get(url, params=payload)
    resp.raise_for_status()
    decoded_resp = resp.json()
    if 'error' in decoded_resp:
        raise requests.exceptions.HTTPError(decoded_resp['error'])
    else:
        return resp.text


def main():
    load_dotenv()
    access_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    try:
        comics_quantity = get_current_comics_quantity()
        title, url, comics_number = get_comics_url_and_title(comics_quantity)
        filename = download_pic(url, comics_number)
        upload_url = get_wall_upload_server(access_token, vk_group_id)
        photo, server, hash = upload_pic(upload_url, filename)
        media_id, owner_id = save_wall_photo(access_token, vk_group_id, photo, server, hash)
        make_wall_post(access_token, vk_group_id, title, media_id, owner_id)
    finally:
        os.remove(filename)


if __name__ == "__main__":
    main()
