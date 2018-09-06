"""
目标：利用Selenium抓取炉石卡组数据存储到MongoDB
网址：http://ls.duowan.com/d/.html
抓取数据：卡组名、职业、所需尘、类型、卡牌详细页、卡牌具体数据
mysql数据库设计（数据库物理设计在文件夹MongoDB中）：
    表1：id、职业、所需尘、类型、卡牌详细页、卡牌具体数据（设计实现）
麻烦1：get_page分析数据时有种写法，进不到parse_page里
（已解决，应该是节点选择不正确的原因，详见注释部分代码）；
麻烦2：多玩炉石网站，从第八页以后，页面button和真实页面不符或页面button不显示区别，造成抓取出错
（已解决：删掉当前显示页button与页数相同一项，页面加载完成改为仅.card_list.cs-clear节点加载完成就OK）。
"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from pymongo import MongoClient

# 数据库配置
client = MongoClient()
db = client['lushi']
collection = db['ceshi']

# chrome配置
#无边框配置
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)  # 等待加载最长时间
base_url = "http://ls.duowan.com"

# 爬取页数配置
start_page = int(input("输入抓取起始页："))  # input输入默认为str
end_page = int(input("输入抓取结束页："))

def save_to_mongo(results):
    """
    目的：将分析得到的数据插入mongo
    :param results:得到的数据(字典时插入数据，列表时更新数据)
    """
    print('正在向数据库插入数据')
    try:
        if collection.insert_one(results):
            print('插入数据成功')
    except Exception:
        print('插入数据失败', Exception)

def update_to_mongo(list,upurl):
    """
    目的：mongo更新操作，查询值为upurl的数据项，将数据更新为list
    :param list: 需要更新的数据
    :param upurl: 需要更新项的值，用于mongo的查询
    :return:
    """
    try:
        print('正在更新卡组数据')
        condition = {'卡牌数据页': upurl}
        #向记录中插入新字段
        collection.update_one(condition, {'$set':{'具体卡牌数据':list}})
        print("更新卡牌数据成功")
    except Exception:
        print('更新卡牌数据失败',Exception)
    #多输出个换行，每条数据换个行，好看点
    print()

def parse_detail_data(url_cards):
    """
    目的：分析卡组具体数据
    思路：实例化一个driver，将传进来的url_cards进行解析，得到卡牌数据并存入列表，将列表进行存储到mongo
    :param url_cards:卡组数据url
    :return:
    """
    #这里需要重新实例化一个chrome，如果用之前的，get（url），就会将之前browser对象数据改变，造成之后再调用browser时出错
    driver = webdriver.Chrome(chrome_options=chrome_options)
    html = driver.get(url_cards)
    cards = driver.find_elements_by_css_selector('div > div.all-card > ul > li > a')
    #实例化一个列表，将具体卡牌数据都放入此列表
    list = []
    for i in range(0,len(cards)):
        list.append(cards[i].text.replace('\n',''))
    print(list)
    print('卡牌数据加载完成')
    #实例化webdriver对象用完一定要关
    driver.quit()
    upurl = url_cards
    update_to_mongo(list,upurl)

def parse_page(browser):
    """
    目的：解析数据
    思路：将browser传参，再用xpath查找数据赋值给给对应数组，后循环提取值赋值给字典或列表
    :param browser:卡牌详细页url
    :return:
    """
    print('正在分析数据')
    names = browser.find_elements_by_xpath('//div[@class="name"]/a[1]')
    zhiye = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[1]')
    cheng = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[3]')
    leixing = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[2]')
    cards = browser.find_elements_by_xpath('//li[starts-with(@class,"card_ch")]/a')
    for i in range(0, len(names)):
        """
        products = []
        products.append(names[i].text)
        products.append(zhiye[i].text)
        products.append(cheng[i].text)
        products.append(leixing[i].text)
        #这又一个陷阱：用find_elements_by_xpath获取节点以后，直接/@href获取属性值要报错，需要用get_attribute方法获取属性值
        products.append(cards[i].get_attribute('href'))
        """
        # 字典形式数据
        products = {
            '卡组名': names[i].text,
            '职业': zhiye[i].text,
            '所需尘': cheng[i].text,
            '类型': leixing[i].text,
            '卡牌数据页': cards[i].get_attribute('href')
        }
        print(products)
        save_to_mongo(products)
        url_cards = cards[i].get_attribute('href')
        parse_detail_data(url_cards)

def get_page(page):
    """
    目的：获得page页的数据
    :param page: 需要获得数据的页数
    :return:
    """
    if page == 1:
        url = base_url + '/d/' + '.html'
    else:
        url = base_url + '/d/' + 'pag' + str(page) + '.html'
    print('正在获得' + str(page) + '页的数据')
    try:
        browser.get(url)
        # 等待数据加载完成
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.card_list.cs-clear')))
        print(page+'页数据获取完成')
        parse_page(browser)
    except TimeoutException:
        get_page(page)

def main():
    """
    目的：遍历需要爬取的page
    """
    for page in range(start_page, end_page + 1):
        get_page(page)
        time.sleep(5)

if __name__ == '__main__':
    # browser记得quit
    try:
        main()
    except:
        print('一开始就出错了')
    finally:
        browser.quit()
