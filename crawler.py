import requests
from bs4 import BeautifulSoup
import urllib.request
import os
from multiprocessing import Manager, Process, Pool


def imgDownload():
    for index, link in enumerate(soup.find_all('img')):
        if index == 0:
            continue;
        img_url = link.get('src')
        urllib.request.urlretrieve(img_url, baseDir + "/img_" + str(index) + '.jpg')


if __name__ == '__main__':
    manager = Manager()
    print("이구루에서 만화를 크롤링하는 프로그램입니다.")
    print("크롤링하고자하는 이구루 만화url을 입력해주세요.")
    # baseUrl = input("만화 url: ")
    print("크롤링할 만화 '영문이름'과 그 만화가 '몇 권'인지 입력해주세요.")
    folderName = input("예시)'conan_v18': ")
    baseDir = "./images/" + folderName
    os.makedirs(baseDir)

    # Input the target URL
    baseUrl = 'https://eguru.tumblr.com/post/180446193767/%EB%AA%85%ED%83%90%EC%A0%95-%EC%BD%94%EB%82%9C-28%EA%B6%8C'
    response = requests.get(baseUrl)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    imgDownload()

