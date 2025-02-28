import time

import requests

from down import verify_file

search_sleep = 1
getlink_sleep = 1

# sixyin_proxies = {
#     'http': 'http://localhost:7890',
#     'https': 'http://localhost:7890',
# }

sixyin_proxies = {
    'http': '',
    'https': '',
}


def search(song_info):
    if 'sixyin_song_id' in song_info.keys():
        return

    song_search_kw = '{0} {1} {2}'.format(song_info['songname'], song_info['signernames'].replace("|", " "),
                                          song_info['albumname'])
    # song_search_kw = '{0} {1} {2}'.format(song_info['songname'], song_info['signernames'].split("|")[0], song_info['albumname'])
    # song_search_kw = '{0} {1}'.format(song_info['songname'], song_info['signernames'].replace("|", " "))
    # song_search_kw = '{0} {1}'.format(song_info['songname'], song_info['albumname'])
    # song_search_kw = '{0}'.format(song_info['songname'])

    url = "https://api.itooi.cn/tencent/search"
    headers = {}
    params = {"type": "song",
              # "keyword": "听见下雨的声音 魏如昀 听见下雨的声音 电影原声带"}
              "keyword": song_search_kw,
              "format": "1",
              "page": "0",
              "pageSize": "20"}

    time.sleep(search_sleep)
    response = requests.get(url, headers=headers, params=params, proxies=sixyin_proxies)
    result = response.json()

    if len(result['data']['list']) == 0:
        return

    song_id = result['data']['list'][0]['id']
    song_name = result['data']['list'][0]['name']
    song_singer = str.join('|', [signer for signer in result['data']['list'][0]['singers']])
    song_album = result['data']['list'][0]['albumName']

    song_info['sixyin_song_id'] = song_id
    song_info['sixyin_song_name'] = song_name
    song_info['sixyin_song_singer'] = song_singer
    song_info['sixyin_song_album'] = song_album


def verify_key(key):
    url = "https://api.itooi.cn/unlock/" + key
    headers = {}
    params = {}

    response = requests.get(url, headers=headers, params=params, proxies=sixyin_proxies)
    result = response.json()
    # print(result['code'])
    # print(result['msg'])
    return True if result['code'] == 200 else False


def get_download_link(song_info, music_dir, key):
    if 'sixyin_song_id' not in song_info.keys():
        return None

    verify = verify_file(music_dir, song_info)
    if verify:
        return song_info['download_link']

    url = "https://api.itooi.cn/tencent/url"
    headers = {'Unlockcode': key}
    params = {'id': song_info['sixyin_song_id'],
              'quality': song_info['songtype'],
              'isRedirect': '0'}  # 是否直接下载

    time.sleep(getlink_sleep)
    response = requests.get(url, headers=headers, params=params, proxies=sixyin_proxies)
    result = response.json()

    if result['code'] == 400:
        return None
    else:
        if ('data' in result.keys()):
            song_info['download_link'] = result['data'][0]
            return song_info['download_link']
        else:
            song_info['download_response'] = result
            return None


def reset_verify_failed_songs_info(songs_info):
    for song_info in songs_info:
        if ('download_verify' in song_info.keys() and not song_info['download_verify']) \
                or ('download_done' in song_info.keys() and not song_info['download_done']):
            if 'sixyin_song_id' in song_info.keys():
                del song_info['sixyin_song_id']
            if 'sixyin_song_name' in song_info.keys():
                del song_info['sixyin_song_name']
            if 'sixyin_song_singer' in song_info.keys():
                del song_info['sixyin_song_singer']
            if 'sixyin_song_album' in song_info.keys():
                del song_info['sixyin_song_album']
            if 'download_link' in song_info.keys():
                del song_info['download_link']
            if 'download_path' in song_info.keys():
                del song_info['download_path']
            song_info['download_done'] = False
            if 'download_verify' in song_info.keys():
                del song_info['download_verify']
