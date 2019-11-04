from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from lxml import etree
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_cookie_csrf(url):
    while True:
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            #chrome_options.add_argument('--disable-gpu')
            #chrome_options.add_argument("--proxy-server=http://192.168.10.244:8088")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(url)
            source = driver.page_source
            wait = WebDriverWait(driver, 20)
            time.sleep(3)
            input_text = wait.until(EC.presence_of_element_located((By.ID,'q')))
            input_text.send_keys("python")
            btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'search-btn')))
            btn.click()
            time.sleep(3)

            cookies = driver.get_cookies()

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
            print(cookie_i)
            return cookie_i,csrf
        except Exception as result:
            print(result)
            driver.close()
            continue
        else:
            print('获取cookie成功')
            break


if __name__ == '__main__':
    get_cookie_csrf('https://www.jianshu.com')
