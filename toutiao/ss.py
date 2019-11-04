import requests
from toutiao.cookie import get_cookie

url = 'https://www.toutiao.com/api/search/content/'
formdata ={
    'aid': '24',
    'app_name': 'web_search',
    'offset': '0',
    'format': 'json',
    'keyword': '狼',
    'autoload': 'true',
    'count': '20',
    'en_qc': '1',
    'cur_tab': '4',
    'from': 'media',
    'pd': 'user',
}


# headers = {
#     # 'cookie': 'csrftoken=185d39889430379d2cc4e60989e44ef5; tt_webid=6731923993248663047; tt_webid=6731923993248663047; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16cf16b354a378-09846fc3091e0a-5373e62-1fa400-16cf16b354b747; CNZZDATA1259612802=1310668984-1567415102-https%253A%252F%252Fwww.toutiao.com%252F%7C1567415102; _ga=GA1.2.670355303.1567418431; uuid="w:4937269d173d4eb29cfea3d77102a394"; login_flag=86e3d608f997d131a92d67527dc01a8f; sessionid=ce50f76a71fef0715eca023db8dae503; sid_tt=ce50f76a71fef0715eca023db8dae503; odin_tt=0ecf12d82001b4a86dc20f72345e5e7289773ac079d430e8a6c18e2e55edfbb94e480a591bff5f42bdc2dcce8dcd86d192d07bbba98dfaac47a5730b48b842d8; passport_auth_status=c9fb9ffad54dc854a93b293ba8b61b88; sso_auth_status=2d9810ab569f224c1851307833141b33; uid_tt=85bb4dd9245351a16290642aac811f8a; sid_guard="ce50f76a71fef0715eca023db8dae503|1567562356|15552000|Mon\054 02-Mar-2020 01:59:16 GMT"; s_v_web_id=0d1ba59f7a4f6e972049d8a03776de7e; __tasessionId=j7sqlp7of1568100218044',
#     #'cookie': 'tt_webid=6735268770754233859; s_v_web_id=0d1ba59f7a4f6e972049d8a03776de7e; WEATHER_CITY=%E5%8C%97%E4%BA%AC; __tasessionId=q4wq1o5y31568176970714; tt_webid=6735268770754233859; csrftoken=295092e51232b17060c27e5d191af429',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
# }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', 'referer': 'https://www.toutiao.com/search/?keyword=123', 'cookie': 's_v_web_id=b8e1d4037cbb9b28bf6289dc95964aa5;tt_webid=6738940120475010573;WEATHER_CITY=%E5%8C%97%E4%BA%AC;tt_webid=6738940120475010573;csrftoken=decfe5ae62e478bf085636580cfeb45b;__tasessionId=b8pavozo81569031772250',
           'Referer':'https://www.toutiao.com/search/?keyword=%E7%8B%BC',
           'accept-language': 'zh-CN,zh;q=0.9',
           'accept': 'application/json, text/javascript',
           'x-requested-with': 'XMLHttpRequest'}

headers['cookie'] = get_cookie('https://www.toutiao.com/search/?keyword=l')
print(headers)
response = requests.get(url=url,headers=headers,params=formdata)
print(response.text)