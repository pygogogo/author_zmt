from selenium import webdriver
import time
from lxml import etree
import jieba
from selenium.webdriver.chrome.options import Options


def get_words(t):
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=http://192.168.10.244:8088')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('https://www.toutiao.com/ch/news_hot/')
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)
    driver.execute_script('document.documentElement.scrollTop=0')
    time.sleep(2)
    for i in range(t):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
    text = driver.page_source
    html = etree.HTML(text)
    lis = html.xpath("//li[@class='item    ']")
    words_list = []
    for index,li in enumerate(lis):
        title = li.xpath(".//div[@class='title-box']/a/text()")
        author = li.xpath(".//a[@ga_event='article_name_click']/text()")
        if title:
            title = title[0]
            words_list.append(title)
        if author:
            author = author[0]
            author = author.replace('\xa0','')
            author = author.replace("⋅",'')
            words_list.append(author)
    driver.close()
    words_list = "".join(words_list)
    seg_list = jieba.cut_for_search(words_list)
    words_list = set(seg_list)
    print(words_list)
    print(len(words_list))

    return words_list
if __name__ == '__main__':
    get_words(2)



     




