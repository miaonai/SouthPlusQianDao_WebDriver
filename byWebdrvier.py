from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from bs4 import BeautifulSoup
import requests
import time
import os

# 获取 COOKIE 环境变量
cookie_json = os.environ.get('COOKIE')

if cookie_json:
    try:
        # 解析 JSON 字符串
        cookie_data = json.loads(cookie_json)
    except json.JSONDecodeError:
        print("错误：无法解析 COOKIE 环境变量为 JSON。")
else:
    print("错误：COOKIE 环境变量未设置。")

chrome_options = Options()
chrome_options.add_argument("--headless")  # 如果你在无头模式下运行
chrome_options.add_argument("--no-sandbox")  # 解决一些权限问题
chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存问题


service = Service(rf'/usr/local/bin/chromedriver')  # 确保路径正确
web = webdriver.Chrome(service=service, options=chrome_options)

def Lingqu():
    try:
        # 切换到进行中的任务
        web.find_element(By.XPATH, '//*[@id="main"]/table/tbody/tr/td[1]/div[2]/table/tbody/tr[3]/td').click()
        # 点击进行中的任务
        # 完成日常
        time.sleep(2)
        try:
            web.find_element(By.XPATH, '//*[@id="both_15"]/a/img').click()
            print('日常领取成功')
        except:
            print('日常领取失败')
            
            
        try:
            # 尝试点击周常,没有就跳了
            web.find_element(By.XPATH, '//*[@id="both_14"]/a/img').click()
            print('周常领取成功')

        except:
            pass


    except:
        print('日常暂未刷新或领取失败')


url = 'https://south-plus.net/plugin.php?H_name-tasks.html'
web.get(url)

time.sleep(1)

# 将cookies添加到webdriver中   
for cookie in cookie_data:
    web.add_cookie(cookie)

# 重新加载页面
web.get(url)
time.sleep(3)

soup = BeautifulSoup(web.page_source, 'html.parser')
print(soup)
user_login = soup.find('div', id='user-login')

if user_login:
    username_tag = user_login.find('a')  # 第一個 <a> 就是使用者 ID
    if username_tag:
        username = username_tag.text.strip()
        print("✅ 登入成功，使用者 ID：", username)
    else:
        print("❌ 找不到使用者名稱")
else:
    print("❌ 尚未登入（找不到 user-login 區塊）")


# 领取周常
#soup = BeautifulSoup(web.page_source, 'html.parser')
weekly_task_1 = soup.find('span', id='p_15')
weekly_task_2 = soup.find('span', id='p_14')
print(weekly_task_1,weekly_task_2)


if weekly_task_1 and weekly_task_2:
    web.find_element(By.XPATH, '//*[@id="p_14"]/a/img').click()
    web.find_element(By.XPATH, '//*[@id="p_15"]/a/img').click()
    print('任务已领取')
    Lingqu()  

elif weekly_task_1:
    web.find_element(By.XPATH, '//*[@id="p_15"]/a/img').click()
    Lingqu()

elif weekly_task_2:
    web.find_element(By.XPATH, '//*[@id="p_14"]/a/img').click()
    Lingqu()
    
else:
    print('任务暂未刷新')

web.quit()
