import os
import re
import time
import urllib.request
from multiprocessing import Manager, Process

import requests
from PIL import Image
import cv2
from bs4 import BeautifulSoup


def makeImagesDir():
    imageDir = "./images/"
    dividedImageDir = './dividedImages/'
    resizedImageDir = './resizedImages/'

    while True:
        print("폴더를 생성하기 위해 만화 이름을 '영문'으로 입력해주세요.")
        print("예시) conan_v13")
        folderName = input('입력: ')

        imageDir += folderName
        dividedImageDir += folderName
        resizedImageDir += folderName

        if os.path.isdir(imageDir) or os.path.isdir(dividedImageDir) or os.path.isdir(resizedImageDir):
            print('주의! 동일한 이름의 폴더가 존재합니다.')
            continue
        else:
            os.makedirs(imageDir)
            os.makedirs(dividedImageDir)
            os.makedirs(resizedImageDir)
            return imageDir, dividedImageDir, resizedImageDir


def getImageURLs(soup):
    imageURLs = []
    imgTags = soup.findAll("img")
    for img in imgTags:
        imageURLs.append(img["data-orig-src"])
    return imageURLs


def downloadImage(index, imagePath, imageURLs):
    imageDir = imagePath + "/image_" + str(index) + '.jpg'
    urllib.request.urlretrieve(imageURLs[index], imageDir)


def getAllImageFiles(imagesDir):
    imageFiles, otherFiles = [], []

    for path, _, files in os.walk(imagesDir):
        for file in files:
            filename, extension = os.path.splitext(file)
            extension = str.lower(extension)
            if extension == '.zip':
                continue
            elif extension in ('.jpg', '.JPG', '.jpeg', '.gif', '.png', '.PNG', '.pgm'):
                imageFiles.append(os.path.join(path, file))
            elif extension in ('.xml', '.XML', '.gt', '.txt', 'TXT', '.json', 'JSON'):
                otherFiles.append(os.path.join(path, file))
    imageFiles.sort()
    otherFiles.sort()
    return imageFiles, otherFiles


def getFiles(imagesDir):
    imageFiles, otherFiles = getAllImageFiles(imagesDir)
    return imageFiles, otherFiles


def searchImages(dir):
    files = os.listdir(dir)
    for file in files:
        fullFile = os.path.join(dir, file)
        print(fullFile)


if __name__ == '__main__':
    manager = Manager()
    imageURLs = manager.list()

    print('크롤링할 만화 url을 입력해주세요')
    print('spacebar를 한 번 정도 누른 후에 엔터를 치세요.')
    print('예시) https://eguru.tumblr.com/post/180446193767/%EB%AA%85%ED%83%90%EC%A0%95-%EC%BD%94%EB%82%9C-28%EA%B6%8C')
    URL = input('입력: ')

    imagePath, dividedImagePath, resizedImagePath = makeImagesDir()

    response = requests.get(URL)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find("div", class_="body-text")
    imageURLs.extend(getImageURLs(soup))

    print('--------------------------------------------------------------------------')
    print('이미지 다운로드 준비!')
    processes = []
    for index, imageURL in enumerate(imageURLs):
        process = Process(target=downloadImage, args=(index, imagePath, imageURLs))
        processes.append(process)
        process.start()
    for process in processes:
        start_time = int(time.time())
        process.join()
        print(f'다운로드 완료! {(time.time() - start_time)}초')
    print('모든 이미지 다운로드 완료!')

    print('--------------------------------------------------------------------------')
    print('이미지 자르기 준비!')
    imageDirs, _ = getFiles(imagePath)
    for imageDir in imageDirs:
        index = re.findall("\d+", imageDir)[-1]
        image = cv2.imread(imageDir)
        h, w, _ = image.shape
        if h > w:
            cv2.imwrite(dividedImagePath + '/image_' + index + '.jpg', image)
        else:
            criteria = w // 2
            MARGIN = 10
            piece1 = image[:, criteria + MARGIN:, :]
            piece2 = image[:, :criteria - MARGIN, :]
            cv2.imwrite(dividedImagePath + '/img_' + index + '_1.jpg', piece1)
            cv2.imwrite(dividedImagePath + '/img_' + index + '_2.jpg', piece2)
        print(f'자르기 완료! image_{index}.jpg')
    print('모든 이미지 자르기 완료!')

    print('--------------------------------------------------------------------------')
    print('이미지 크기 재조정 준비!')
    dividedImagefiles = os.listdir(dividedImagePath)
    for file in dividedImagefiles:
        image = Image.open(dividedImagePath + '/' + file)
        imageSize = image.size
        renamedFile = file.replace('image_', '')
        if imageSize[0] > imageSize[1]:
            print(imageSize[0], imageSize[1])
            resizedImage = image.resize((640, 448))
            resizedImage.save(resizedImagePath + '/'+ renamedFile)
        else:
            resizedImage = image.resize((448, 640))
            resizedImage.save(resizedImagePath + '/'+ renamedFile)
        print(f'이미지 조정 완료! {file}')
    print('모든 이미지 크기 재조정 완료!')
    print('--------------------------------------------------------------------------')
    print('만화 이미지 크롤링을 종료하겠습니다 :)')