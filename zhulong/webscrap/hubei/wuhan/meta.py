import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lmfscrap import web


# __conp=["postgres","since2015","192.168.3.171","hunan","zhuzhou"]





def f1(driver, num):
    """
    进行翻页，并获取数据
    :param driver: 已经访问了url
    :param num: 返回的是从第一页一直到最后一页
    :return:
    """
    locator = (By.XPATH, '//*[@id="datagrid-row-r1-1-0"]/td[2]/div')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    # 获取当前页的url
    # url = driver.current_url
    # cnum = int(re.findall("([0-9]{1,}).html", url)[0])
    # locator = (By.XPATH, "//ul[@class='ewb-info-list']//li[1]//a")
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="datagrid-pager pagination"]/table/tbody/tr/td[7]/input').text

    # val = driver.find_element_by_xpath("//ul[@class='ewb-info-list']//li[1]//a").text
    if cnum != num:
        driver.find_element_by_xpath(
            '//div[@class="datagrid-pager pagination"]/table/tbody/tr/td[7]/input').clear()
        driver.find_element_by_xpath(
            '//div[@class="datagrid-pager pagination"]/table/tbody/tr/td[7]/input').send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//*[@id='datagrid-row-r1-1-0']/td[2]/div[string()!='%s']" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    html_data = etree.HTML(page)
    # 获取二个table的数据
    table_data_list = html_data.xpath('//table[@class="datagrid-btable"]/tbody/tr')
    data_len = len(table_data_list)
    # print(data_len)
    data = []
    for i in range(0, data_len // 2):
        list_1 = []
        table_1 = table_data_list[i]
        ass = table_1.findall('td')
        # 获取项目名称的链接
        try:
            prjName_links = table_1.xpath('./td[2]/div/a/@onclick')[0]
            # print(prjName_links)
            # print(tenderPrjName_links)
            str = re.findall(r"\('.*'\)", prjName_links)[0].split("'")[1]
            prjName_link = "http://www.whzbtb.cn/V2PRTS/" + str
        except Exception as e:
            prjName_link = ""
        list_1.append(prjName_link)
        for j in ass:
            # print(j.xpath("string(div)"))
            k = j.xpath("string(div)")
            list_1.append(k)
        table_2 = table_data_list[data_len // 2 + i]
        ass = table_2.findall('td')
        for j in ass:
            # print(j.xpath("string(div)"))
            k = j.xpath("string(div)")
            list_1.append(k)

        # print(list_1)
        data.append(list_1)
    # soup = BeautifulSoup(page, 'lxml')
    #
    # soup.find("td", attrs={"field": "prjName"}).get_text()
    # ul = soup.find("ul", class_="ewb-info-list")
    # lis = ul.find_all("li", class_="ewb-list-node clearfix")
    # data = []
    # for li in lis:
    #     a = li.find("a")
    #     span = li.find("span", recursive=False)
    #     tmp = [a["title"], "http://www.zzzyjy.cn" + a["href"], span.text.strip()]
    #     data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """

    # locator = (By.CLASS_NAME, "ewb-info-list")
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    #
    # if "下页" in driver.page_source:
    #     locator = (By.XPATH, "//ul[@class='ewb-info-list']//li[1]//a")
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    #
    #     total = int(driver.find_element_by_id("index").text.split("/")[1])
    #     driver.quit()
    #     return total
    # else:
    #     driver.quit()
    #     return 1
    locator = (By.XPATH, '//div[@class="datagrid-pager pagination"]/table/tbody/tr/td[8]/span')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('共(\d+)页', page_all)[0]
    print(page)
    return page

url="http://www.whzbtb.cn/V2PRTS/TendererNoticeInfoListInit.do"
driver=webdriver.Chrome()
#driver.minimize_window()
driver.get(url)
df=f1(driver,2)
def general_template(tb, url, col, conp):
    m = web()
    setting = {
        "url": url,
        "f1": f1,
        "f2": f2,
        "tb": tb,  # 表名
        "col": col,  # 字段名
        "conp": conp,  # 数据库连接
        "num": 10,  # 线程数量
        "total": 100,  # 测试用，只测试100页

    }
    m = web()
    m.write(**setting)


def work(conp, i=-1):
    data = [
        ["zhaobiao_zige_yushen_gg", "http://www.whzbtb.cn/V2PRTS/TendererNoticeInfoListInit.do",
         ["tenderPrjName_link", "datagrid-td-rownumber",  "tenderPrjName", "noticeState", "registrationId", "prjbuildCorpName",
          "noticeStartDate", "noticeEndDate", "totalInvestment", "platformDataSourceName", "evaluationMethodName"
          ]],

        # ["gcjs_fangwu_zhaobiao_gg", "http://www.zzzyjy.cn/016/016001/016001001/1.html",
        #  ["name", "href", "ggstart_time"]],

        # ["gcjs_fangwu_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016001/016001004/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_fangwu_zhongbiao_gg", "http://www.zzzyjy.cn/016/016001/016001006/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shizheng_zhaobiao_gg", "http://www.zzzyjy.cn/016/016002/016002001/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shizheng_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016002/016002004/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shizheng_zhongbiao_gg", "http://www.zzzyjy.cn/016/016002/016002006/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_jiaotong_zhaobiao_gg", "http://www.zzzyjy.cn/016/016003/016003001/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_jiaotong_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016003/016003004/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_jiaotong_zhongbiao_gg", "http://www.zzzyjy.cn/016/016003/016003006/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shuili_zhaobiao_gg", "http://www.zzzyjy.cn/016/016004/016004001/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shuili_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016004/016004004/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["gcjs_shuili_zhongbiao_gg", "http://www.zzzyjy.cn/016/016004/016004006/1.html",
        #  ["name", "href", "ggstart_time"]],
        #
        # ["zfcg_zhaobiao_gg", "http://www.zzzyjy.cn/017/017001/1.html", ["name", "href", "ggstart_time"]],
        #
        # ["zfcg_zhongbiao_gg", "http://www.zzzyjy.cn/017/017003/1.html", ["name", "href", "ggstart_time"]],
        #
        # ["zfcg_biangen_gg", "http://www.zzzyjy.cn/017/017002/1.html", ["name", "href", "ggstart_time"]],
        #
        # ["zfcg_liubiao_gg", "http://www.zzzyjy.cn/017/017004/1.html", ["name", "href", "ggstart_time"]],

    ]
    if i == -1:
        data = data
    else:
        data = data[i:i + 1]
        print(data)
    for w in data:
        general_template(w[0], w[1], w[2], conp)


conp = []


