import requests
import re


def get_autfans(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    }

    response = requests.get(url=url,headers=headers)
    fensi = re.findall(r'fensi:\'(.*?)\',',response.text,re.DOTALL)[0]
    autfans = int(fensi)
    return autfans
