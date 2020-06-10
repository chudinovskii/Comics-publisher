import requests
import os
import random
from dotenv import load_dotenv


def download_pic():
    url = 'https://xkcd.com/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()
    decoded_resp = resp.json()
    comics_quantity = int(decoded_resp['num'])

    comics_number = random.randint(1, comics_quantity)
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()
    decoded_resp = resp.json()
    title = decoded_resp['alt']
    url_for_img = decoded_resp['img']

    resp = requests.get(url_for_img)
    resp.raise_for_status()
    filename = f'comics_{comics_number}.png'
    with open(filename, 'wb') as file:
        file.write(resp.content)
    return title, filename


def upload_pic(upload_url, filename):
    with open(filename, 'rb') as file:
        url = upload_url
        files = {
            'photo': file
        }
        resp = requests.post(url, files=files)
        resp.raise_for_status()
        decoded_resp = resp.json()
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
    return resp.text


def main():
    load_dotenv()
    access_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    title, filename = download_pic()
    upload_url = get_wall_upload_server(access_token, vk_group_id)
    photo, server, hash = upload_pic(upload_url, filename)
    media_id, owner_id = save_wall_photo(access_token, vk_group_id, photo, server, hash)
    make_wall_post(access_token, vk_group_id, title, media_id, owner_id)
    os.remove(filename)


if __name__ == "__main__":
    main()
