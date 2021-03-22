# coding = utf-8
import string

from bs4 import BeautifulSoup
import re  # 正则匹配
import urllib.request, urllib.error  # 指定URL，获取网页数据
from urllib.parse import quote
import xlwt
import ssl

# 全局取消证书验证（https）
ssl._create_default_https_context = ssl._create_unverified_context


def main():
    keywords = input("请输入关键字：")
    page = input("请输入页数：")
    datalist = []
    savePath = "jd" + keywords + ".xls"
    baseUrl = "https://search.jd.com/Search?keyword=" + keywords + "&page="
    datalist = getData(baseUrl, page)
    saveData(datalist, savePath)


findImgSrc = re.compile(r'<img.*data-lazy-img="(.*?)"', re.S)
findPrice = re.compile(r'<i>(.*?)</i>', re.S)
findInfo = re.compile(r'<div class="p-name p-name-type-2">(.*?)<em>(.*?)</em>', re.S)
findTag = re.compile(r'<span(.*?)>(.*?)</span>', re.S)
findStore = re.compile(r'<span class="J_im_icon"><a.*?>(.*?)</a>', re.S)
findSupply = re.compile(r'<i class="goods-icons J-picon-tips J-picon-fix" data-idx="1" data-tips="京东自营，品质保障">(.*?)</i>',
                        re.S)


# findRatNum = re.compile(r'<div class="p-commit" data-done="1"><strong><a .*>(.*?)</a>',re.S)      评价需要其他请求来实现

def getUrl(askUrl):
    head = {}
    head[
        "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    s = quote(askUrl, safe=string.printable)  # urllib.request.urlopen不支持中英文混合的字符串，方法quote的参数safe表示可以忽略的字符
    request = urllib.request.Request(s, headers=head)

    html = ""

    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except Exception as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


def getData(baseUrl, page):
    datalist = []
    for i in range(0, int(page)):
        url = baseUrl + str(i)
        html = getUrl(url)
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("li", class_="gl-item"):
            data = []
            item = str(item)
            imgSrc = re.findall(findImgSrc, item)[0]
            imgSrc = imgSrc[2:]  # 去掉前面多余的/
            price = re.findall(findPrice, item)[0]
            data.append(imgSrc)
            data.append(price)
            info = re.findall(findInfo, item)[0]
            tmpTag = info[1]
            tag = re.findall(findTag, tmpTag)
            if len(tag) != 0:
                data.append(tag[0][1])
                tmpTag = re.sub(tag[0][1], '', tmpTag)
            else:
                data.append(' ')

            tmpTag = re.sub('<(.*?)>', '', tmpTag)  # 去掉多余符号
            tmpTag = re.sub('\n', '', tmpTag)
            tmpTag = re.sub('\t', '', tmpTag)
            data.append(tmpTag)

            # ratNum = re.findall(findRatNum,item)
            store = re.findall(findStore, item)[0]
            data.append(store)
            datalist.append(data)

            supply = re.findall(findSupply, item)
            if len(supply) != 0:
                data.append(supply[0])
            else:
                data.append("第三方")

    return datalist


def saveData(datalist, savePath):
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet("jd_products")
    col = ("图片链接", "价格", "标签", "品牌参数&描述", "店铺", "货源")
    for i in range(0, 6):
        worksheet.write(0, i, col[i])
    for i in range(0, len(datalist)):
        data = datalist[i]
        for j in range(0, 6):
            worksheet.write(i + 1, j, data[j])

    workbook.save(savePath)


if __name__ == '__main__':
    main()
