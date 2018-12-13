# coding:utf-8

import requests
import os
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool


def get_page(offset):
    """
    加载单个Ajax请求页面
    :param offset:
    :return:
    """
    # URL中的查询参数
    params = {
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'cur_tab':'1',
        'from':'search_tab',
        'pd':'synthesis'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json() # 将结果转化为json格式
    except requests.ConnectionError:
        return None

def get_images(json):
    """
    解析页面内容
    :param json:
    :return:
    """
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            try:
                for image in images: # 若为None则不可遍历
                    yield {
                        'image':image.get('url'),
                        'title':title
                    }
            except:
                return None

def save_image(item):
    """
    保存图片
    :param item:
    :return:
    """
    if not os.path.exists(item.get('title')): # 首先查看当前文件夹是否有此命名的文件，没有则创建
        os.mkdir(item.get('title'))
    try:
        response = requests.get('http:' + item.get('image')) # 注意此处URL的构造前边要加上 http:
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print('Already Download',file_path)
    except requests.ConnectionError:
        print('Failed to Save Image')

def main(offset):
    """
    主函数
    :param offset:
    :return:
    """
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)

GROUP_START = 1 # 分页的起始页
GROUP_END = 5 # 分页的终止页

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START,GROUP_END+1)]) # 列表生成式
    pool.map(main,groups) # 构建线程池
    pool.close()
    pool.join()

