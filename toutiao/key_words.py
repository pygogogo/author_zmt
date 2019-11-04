#@Time    :2019/10/8 11:24
#@Author  :wuxinghui 
#@FileName: key_words.py
from selenium import webdriver
import time
from lxml import etree
import jieba

url_list = ['https://www.toutiao.com/ch/news_hot/','https://www.toutiao.com/ch/news_tech/','https://www.toutiao.com/ch/news_entertainment/','https://www.toutiao.com/ch/news_game/','https://www.toutiao.com/ch/news_sports/','https://www.toutiao.com/ch/news_finance/','https://www.toutiao.com/ch/funny/','https://www.toutiao.com/ch/news_military/','https://www.toutiao.com/ch/news_fashion/','https://www.toutiao.com/ch/news_discovery/','https://www.toutiao.com/ch/news_regimen/','https://www.toutiao.com/ch/news_history/','https://www.toutiao.com/ch/news_world/','https://www.toutiao.com/ch/news_travel/','https://www.toutiao.com/ch/news_baby/','https://www.toutiao.com/ch/news_essay/','https://www.toutiao.com/ch/news_food/']

def get_words(t,url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)
    driver.execute_script('document.documentElement.scrollTop=0')
    time.sleep(3)
    for i in range(t):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
    text = driver.page_source

    html = etree.HTML(text)
    if 'funny' in url:
        lis = html.xpath("//li[@ga_event='ugc_item_click']")
        words_list = []
        for li in lis:
            author = li.xpath(".//a[@class='ugc-name']/span/text()")
            if author:
                author = author[0]
                words_list.append(author)
    else:
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
    words_list = jieba.cut_for_search(words_list)
    words_list = set(words_list)

    print(words_list)
    print(len(words_list))
    return words_list
def get_all():
    words = []
    for i in url_list:
        word_list = get_words(3,i)
        words += word_list
    words_set = set(words)
    print(words_set)
    print(len(words_set))
    return words_set



if __name__ == '__main__':
    get_all()