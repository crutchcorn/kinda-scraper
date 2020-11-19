import json
import os
from errno import EEXIST
from os import makedirs
from time import sleep
from urllib.error import HTTPError
from urllib.request import urlopen
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.remote.webelement import WebElement
import re

driver = webdriver.Chrome()
driver.implicitly_wait(3)


def findTime():
    js_meta_a_tag = driver.find_element_by_css_selector('.js_meta-time')
    time_tag = js_meta_a_tag.find_element_by_xpath('./..')
    return time_tag.get_attribute('datetime')


def findTags():
    try:
        time_and_filed_container = driver.find_element_by_css_selector('.js_meta-time').find_element_by_xpath('./../..')
        dropdown_el = time_and_filed_container.find_element_by_css_selector('.js_dropdown')
        tag_els = dropdown_el.find_elements_by_css_selector('a')
        tags: list[str] = list(map(lambda el: el.get_property('innerText'), tag_els))
        return tags
    except NoSuchElementException:
        return []


def findAuthor():
    authorEl = driver.find_element_by_css_selector('.js_meta-time').find_element_by_xpath('./../../../div[1]')
    return authorEl.text


def findImgSrc(imgEl: WebElement):
    srcset = imgEl.get_attribute('srcset')
    if not srcset:
        srcset = imgEl.get_attribute('data-srcset')
    if not srcset:
        src = imgEl.get_attribute('src')
        if not src:
            return ['', '']
        src_ids = re.findall(r'^.*\/(.*?)$', src)
        if len(src_ids) == 0 or src_ids[0].startswith('http'):
            return ['', '']
        return [f'https://i.kinja-img.com/gawker-media/image/upload/{src_ids[0]}', src_ids[0]]
    img_ids = re.findall(r'^.*\/(.*?)\s80w', srcset)
    return [f'https://i.kinja-img.com/gawker-media/image/upload/{img_ids[0]}', img_ids[0]]


def findVidSrc(vidEl: WebElement):
    postersrc = vidEl.get_attribute('data-postersrc')
    if not postersrc:
        return ['', '']
    vid_ids = re.findall(r'^.*\/(.*?)\..*?$', postersrc)
    return [f'https://i.kinja-img.com/gawker-media/image/upload/{vid_ids[0]}.mp4', f'{vid_ids[0]}.mp4']


def findTitle():
    try:
        return driver.find_element_by_css_selector('h1').get_property('innerHTML')
    except NoSuchElementException:
        return ''


def make_sure_path_exists(path):
    try:
        makedirs(path)
    except OSError as exception:
        if exception.errno != EEXIST:
            raise


dirname = os.path.join(os.path.dirname(__file__), 'dist')


def downloadPage(url: str):
    # Given a URL: https://rockmandash12.kinja.com/rockmandash-rambles-an-explanation-on-my-review-system-1619265485
    # Stub = rockmandash-rambles-an-explanation-on-my-review-system-1619265485
    stub_regex = re.findall(r'^.*\/(.*?)$', url)

    stub = stub_regex[0]

    stub_folder_path = os.path.join(dirname, stub)
    make_sure_path_exists(stub_folder_path)

    post_body = driver.find_element_by_css_selector('.js_post-content')

    print('stub', stub)

    # Image downloading
    try:
        imgs = post_body.find_elements_by_css_selector('img')
        for img in imgs:
            sleep(.1)
            print(img.get_attribute('outerHTML'))
            img_src, img_id = findImgSrc(img)
            if not img_src:
                raise Exception('No img src found')
                continue
            print(img_src, img_id)
            img_path = os.path.join(stub_folder_path, img_id)
            f = open(img_path, 'wb')
            try:
                f.write(urlopen(img_src).read())
            except HTTPError:
                ''
            f.close()
    except NoSuchElementException:
        ''

    # Video downloading
    try:
        vids = post_body.find_elements_by_css_selector('video')
        for vid in vids:
            vid_src, vid_id = findVidSrc(vid)
            if not vid_src:
                raise Exception('No video src found')
                continue
            print(vid_src, vid_id)
            vid_path = os.path.join(stub_folder_path, vid_id)
            f = open(vid_path, 'wb')
            try:
                f.write(urlopen(vid_src).read())
            except HTTPError:
                ''
            f.close()
    except NoSuchElementException:
        ''

    # Post HTML
    inner_html: str = post_body.get_property('innerHTML')
    with open(os.path.join(stub_folder_path, 'index.html'), "w", encoding="utf-8") as text_file:
        text_file.write(inner_html)

    # Metadata
    tags = findTags()
    time = findTime()
    author = findAuthor()
    title = findTitle()
    print(author, time)
    metadict = {
        "tags": tags,
        "time": time,
        "author": author,
        "title": title
    }
    with open(os.path.join(stub_folder_path, 'meta.json'), 'w') as fp:
        json.dump(metadict, fp)

# driver.get('https://rockmandash12.kinja.com/yu-no-is-more-than-just-an-old-visual-novel-1835507618')
# sleep(5)
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# downloadPage('https://rockmandash12.kinja.com/yu-no-is-more-than-just-an-old-visual-novel-1835507618')

filepath = os.path.join(os.path.dirname(__file__), 'article_list.txt')

list_file = open(filepath, "r").read().split('\n')

for line in list_file:
    try:
        driver.get(line)
        sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        downloadPage(line)
    except InvalidArgumentException:
        ''

# close the browser window
driver.quit()
