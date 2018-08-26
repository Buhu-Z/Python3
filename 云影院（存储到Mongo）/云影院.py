"""
目标1：抓取云影院指定页数据存储到Mongo
目标2：将pic一起下载下来保存
"""

import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient

# 爬取页数配置信息(抓取指定页)
start_page = int(input("输入抓取起始页：")) #input输入默认为str
end_page = int(input("输入抓取结束页："))

# mongo配置信息
client = MongoClient()
db = client['YunYingYuan']
collection = db['ceshi']

# 基础链接和headers配置信息
base_url = "http://www.yugula.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
}


# 函数：请求page页数据
def get_page(page):
    if page == '1':
        url = base_url + '/frim/' + '1' + '.html'
    else:
        url = base_url + '/frim/' + '1_' + page + '.html'
    print(url)
    try:
        html = requests.get(url, headers=headers)
        if html.status_code == 200:
            html.encoding = 'utf-8'  # 将获取的网页进行手动编码，不然爬下来的中文是乱码（有些网站需要，有些不需要，不知道啥原因）
            return html
    except requests.ConnectionError as e:
        print('请求网页：' + page + '出错', e.args)


# 函数：解析page页数据
def parse_page(html):
    doc = pq(html.text)
    items = doc('#content #yun-list li').items()
    for li in items:
        ceshi = {}
        ceshi['movie_name'] = li.find('.name').text()
        ceshi['actor'] = li.find('.actor').text()
        ceshi['pic'] = li.find('.lazy').attr('data-original')
        ceshi['content'] = li.find('.other').text()
        ceshi['playpage'] = base_url + li.find('.yun-link').attr('href')
        yield ceshi


# 函数：将结果存储到Mongo
def save_to_mongo(result,page):

    if collection.insert(result):

        print('插入数据成功')



if __name__ == '__main__':
    count = 0
    for page in range(start_page, end_page + 1):
        html = get_page(str(page))
        results = parse_page(html)
        for result in results:
            save_to_mongo(result,page)
            count = count + 1
        print('第' + str(page) + '页插入完成' + ',共' + str(count) + '条数据')
        print()
