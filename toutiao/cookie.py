
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from lxml import etree
import time
import platform
from selenium.webdriver.chrome.options import Options
import random


def getPlatform():
    '''测试所处平台'''
    tup = platform.architecture()
    operating_system = tup[1].lower()
    if 'windows' in operating_system:
        # print(operating_system)
        #返回1表示windows服务器
        return 1
    else:
        #返回2表示linux服务器
        return 2
def get_cookie_csrf(url):
    while True:
        try:
            plat = getPlatform()
            chrome_options = Options()
            if plat == 2:
                chrome_options.add_argument('blink-settings=images, Enabled=false')
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-extensions')
                driver = webdriver.Chrome(r'/usr/bin/chromedriver', chrome_options=chrome_options)
            else:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                driver = webdriver.Chrome(chrome_options=chrome_options)
            #chrome_options.add_argument('--proxy-server=http://192.168.10.244:8088')
            driver.get(url)
            time.sleep(10)
            cookies = driver.get_cookies()
            source = driver.page_source
            cookie_info = []
            for cookie in cookies:
                a = cookie['name'] + "=" + cookie['value']
                cookie_info.append(a)
            cookie_i = ";".join(cookie_info)
            html = etree.HTML(source)
            csrf = html.xpath("//meta[@name='csrf-token']/@content")[0]
            print(cookie_i)
            print(csrf)
            driver.close()
            return cookie_i,csrf
        except Exception as result:
            print(result)
            print('获取cookie失败，代理可能出现问题')
            print("重新获取cookie")
            continue
        else:
            print('获取成功，开始导入')
            break

# def get_cookie(url):
#     plat = getPlatform()
#     chrome_options = Options()
#     print(plat)
#     if plat == 2:
#         chrome_options.add_argument('blink-settings=images, Enabled=false')
#         chrome_options.add_argument('--headless')
#         chrome_options.add_argument('--disable-gpu')
#         chrome_options.add_argument('--no-sandbox')
#         chrome_options.add_argument('--disable-dev-shm-usage')
#         chrome_options.add_argument('--disable-extensions')
#         driver = webdriver.Chrome(r'/usr/bin/chromedriver', chrome_options=chrome_options)
#     else:
#         # ip_list = ["61.130.181.114:9999", "58.247.127.145:53281", "47.107.190.212.8118", "27.152.91.79:9999"]
#         # valid_ip = random.choice(ip_list)
#         # print(valid_ip)
#
#         chrome_options.add_argument("--proxy-server=http://106.14.40.247:16818")
#         driver = webdriver.Chrome(chrome_options=chrome_options)
#     driver.get(url)
#     time.sleep(5)
#     cookies = driver.get_cookies()
#     cookie_info = []
#     for cookie in cookies:
#         a = cookie['name'] + "=" + cookie['value']
#         cookie_info.append(a)
#     cookie_i = ";".join(cookie_info)
#     print(cookie_i)
#
#     driver.close()
#     driver.quit()
#     return cookie_i

def get_cookie(url):
    plat = getPlatform()
    chrome_options = Options()
    print(plat)
    if plat == 2:
        chrome_options.add_argument('blink-settings=images, Enabled=false')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        driver = webdriver.Chrome(r'/usr/bin/chromedriver', chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(6)
    input_text = driver.find_element_by_class_name("tt-input__inner")
    input_text.send_keys("123")
    time.sleep(3)
    button = driver.find_element_by_xpath("//button[@type='button']")
    button.click()
    time.sleep(20)
    cookies = driver.get_cookies()
    cookie_info = []
    for cookie in cookies:
        a = cookie['name'] + "=" + cookie['value']
        cookie_info.append(a)
    cookie_i = ";".join(cookie_info)
    print(cookie_i)
    driver.close()
    driver.quit()
    return cookie_i

def ceshi(url):
    plat = getPlatform()
    chrome_options = Options()
    print(plat)
    if plat == 2:
        chrome_options.add_argument('blink-settings=images, Enabled=false')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        driver = webdriver.Chrome(r'/usr/bin/chromedriver', chrome_options=chrome_options)
    else:
        # ip_list = ["61.130.181.114:9999", "58.247.127.145:53281", "47.107.190.212.8118", "27.152.91.79:9999"]
        # valid_ip = random.choice(ip_list)
        # print(valid_ip)

        chrome_options.add_argument("--proxy-server=http://192.168.10.244:8088")
        driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    time.sleep(5)
    print(driver.page_source)
    cookies = driver.get_cookies()
    cookie_info = []
    for cookie in cookies:
        a = cookie['name'] + "=" + cookie['value']
        cookie_info.append(a)
    cookie_i = ";".join(cookie_info)
    print(cookie_i)

    driver.close()
    driver.quit()
    return cookie_i




if __name__ == '__main__':
    ceshi('http://httpbin.org/ip')
