import requests
from pyquery import PyQuery as pq


url = "http://www.yugula.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
}
html = requests.get(url+'/frim/1.html',headers=headers)
html.encoding = 'utf-8'  #将获取的网页进行手动编码，不然爬下来的中文是乱码（有些网站需要，有些不需要，不知道啥原因）
doc = pq(html.text)
items = doc('#content #yun-list li').items()
for li in items:
    movie_name = li.find('.name').text()
    actor = li.find('.actor').text()
    pic = li.find('.lazy').attr('data-original')
    content = li.find('.other').text()
    playpage = li.find('.yun-link').attr('href')
    file = open('./File/云影院电影.txt','a',encoding='utf-8')
    file.write('\n'.join(['电影名'+':'+movie_name,'演员：'+actor,content,'电影海报地址：'+pic,'播放地址：'+url+playpage]))
    file.write('\n'+'='*50+'\n')
    file.close()
