"""
目标：利用Selenium抓取炉石卡组数据存储到Mysql（完成1-8页的正常抓取，后面出错，存储到数据库未实现）
网址：http://ls.duowan.com/d/.html
抓取数据：卡组名、职业、所需尘、类型、卡牌配置
mysql数据库设计（数据库物理设计在文件夹mysqldb中）：
    表1：id、职业、所需尘、类型（设计实现，存储未实现）
    表2：卡牌配置（设计实现，存储未实现）
麻烦1：get_page分析数据时有种写法，进不到parse_page里（详见注释部分代码）；
麻烦2：存储数据到mysql，很恼火；
麻烦3：多玩炉石网站，从第八页以后，页面button和真实页面不符或页面button不显示区别，造成抓取出错。
"""
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import time
import pymysql

# 数据库配置
db = pymysql.connect(host='localhost', user='root', password='123', port=3306, db='spider')
cursor = db.cursor()

# chrome配置
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 10)  # 等待加载最长时间
base_url = "http://ls.duowan.com"

# 爬取页数配置
start_page = int(input("输入抓取起始页："))  # input输入默认为str
end_page = int(input("输入抓取结束页："))


# start_page = 1
# end_page = 1


def save_to_mysql(products):
    """
    将分析得到的数据插入mysql
    :param products:得到的数据列表
    """
    print('正在向数据库插入数据')
    data = {
        'cdgroupname': products[0],
        'profession': products[1],
        'need': products[2],
        'leixing': products[3]
    }
    table = 'baseinfo'
    # sql语句根据字典动态构造，元组也动态构造，实现通用插入（避免寻常方法造成的增加字段，则需更改很多地方）
    keys = ','.join(data.keys())
    values = ','.join(['%s'] * len(data))
    sql = 'INSERT INTO {table}({keys}) values ({values})'.format(table=table, keys=keys, values=values)
    # 插入成功则commit，失败的rollback
    try:
        if cursor.execute(sql, tuple(data.values())):
            print('插入数据成功')
            db.commit()
    except Exception:
        print('插入数据失败', Exception)
        db.rollback()
    db.close()


def parse_page(browser):
    """
    目的：解析数据
    思路：将browser传参，再用xpath查找数据赋值给给对应数组，后循环提取值赋值给字典或列表
    :param browser:
    :return:
    """
    print('正在分析数据')
    names = browser.find_elements_by_xpath('//div[@class="name"]/a[1]')
    zhiye = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[1]')
    cheng = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[3]')
    leixing = browser.find_elements_by_xpath('//div[@class="mess"]/ul[1]/li[2]')
    for i in range(0, len(names)):
        """
        #字典形式数据
        product = {
            '卡组名': names[i].text,
            '职业': zhiye[i].text,
            '所需尘': cheng[i].text,
            '类型': leixing[i].text,
            }
        """
        # 列表形式数据
        products = []
        products.append(names[i].text)
        products.append(zhiye[i].text)
        products.append(cheng[i].text)
        products.append(leixing[i].text)
        print(products)
        # save_to_mysql(products)

    """
    #麻烦：这样写 get_page根本就进不到parsr_page 鬼知道什么问题
    html = browser.page_source
    doc = pq(html)
    items = doc('li.card_ch.fl').items()
    for item in items:
        ceshi = {}
        ceshi['卡组名'] = item.find('.name').attr('title')
        ceshi['职业'] = item.find('.mess > ul:nth-child(2) > li:nth-child(1)').text()
        ceshi['所需尘'] = item.find('.mess > ul:nth-child(2) > li:nth-child(3)').text()
        ceshi['类型'] = item.find('.mess > ul:nth-child(2) > li:nth-child(2)').text()
        yield ceshi
        print(ceshi)
    """


def get_page(page):
    """
    获得page页的数据
    :param page: 需要获得数据的页数
    :return:
    """
    print('正在加载page', page)
    if page == 1:
        url = base_url + '/d/' + '.html'
    else:
        url = base_url + '/d/' + 'pag' + str(page) + '.html'
    print('正在获得' + str(page) + '页的数据')
    try:
        browser.get(url)
        # if page > 1:
        #     # 等待界面加载完成（节点li.control加载完成则数据也加载完成）
        #     next_page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.pagnav > li:nth-child(9)')))
        #     # 获取下一页的button传给next_page
        #     next_page.click()  # 点击提交button
        # 等待数据加载完成
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'li.num.on'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.card_list.cs-clear')))
        print('获取数据完成')
        parse_page(browser)
    except TimeoutException:
        get_page(page)


def main():
    """
    遍历需要爬取的page
    """
    for page in range(start_page, end_page + 1):
        get_page(page)
        time.sleep(5)


if __name__ == '__main__':
    # browser记得close
    try:
        main()
    except:
        print('一开始就出错了')
    finally:
        browser.close()
