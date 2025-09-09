from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from bs4 import BeautifulSoup
import requests # 引入但未用，暂时保留
import time
import os

# 获取 COOKIE 环境变量
cookie_json = os.environ.get('COOKIE')

cookie_data = [] # 初始化为空列表，以防万一
if cookie_json:
    try:
        # 解析 JSON 字符串
        cookie_data = json.loads(cookie_json)
        print("✅ 成功解析 COOKIE 环境变量。")
    except json.JSONDecodeError:
        print("❌ 错误：无法解析 COOKIE 环境变量为 JSON。请检查其格式。")
        exit(1) # 解析失败则退出
else:
    print("❌ 错误：COOKIE 环境变量未设置。请确保已配置。")
    exit(1) # 未设置则退出

chrome_options = Options()
chrome_options.add_argument("--headless")  # 如果你在无头模式下运行
chrome_options.add_argument("--no-sandbox")  # 解决一些权限问题
chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存问题
# 添加用户代理，有时可以避免一些检测
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


service = Service(r'/usr/local/bin/chromedriver')  # 确保路径正确，使用 r'' 避免转义问题
web = webdriver.Chrome(service=service, options=chrome_options)

def Lingqu():
    try:
        # 切换到进行中的任务
        # 使用更稳健的等待方式，例如 WebDriverWait
        # web.find_element(By.XPATH, '//*[@id="main"]/table/tbody/tr/td[1]/div[2]/table/tbody/tr[3]/td').click()
        # 直接尝试点击，如果没有daily task这个text，就catch掉
        web.find_element(By.XPATH, '//td[contains(text(), "进行中的任务")]').click()
        print('已切换到进行中的任务')

        # 点击进行中的任务
        # 完成日常
        time.sleep(2) # 页面加载等待
        
        # 尝试点击日常任务领取按钮
        try:
            # 这里的 XPath 看起来是基于 id 的，可以尝试更具体的定位
            daily_task_img = web.find_element(By.XPATH, '//*[@id="both_15"]/a/img')
            daily_task_img.click()
            print('✅ 日常任务领取成功')
        except Exception as e:
            print(f'❌ 日常任务领取失败: {e}')
            
        # 尝试点击周常任务领取按钮
        try:
            # 尝试点击周常,没有就跳了
            weekly_task_img = web.find_element(By.XPATH, '//*[@id="both_14"]/a/img')
            weekly_task_img.click()
            print('✅ 周常任务领取成功')
        except Exception as e:
            print(f'❌ 周常任务领取失败或不存在: {e}')

    except Exception as e:
        print(f'❌ 无法切换到进行中的任务或领取失败: {e}')


url = 'https://south-plus.net/plugin.php?H_name-tasks.html'
web.get(url) # 第一次加载页面

time.sleep(1) # 给页面一点时间加载

# 将cookies添加到webdriver中
# 遍历每个 cookie 字典，并进行处理
for cookie in cookie_data:
    # 复制一份 cookie 字典，避免修改原始数据
    processed_cookie = cookie.copy()

    # 移除 'domain' 属性，让 Selenium 自动处理，避免 InvalidCookieDomainException
    if 'domain' in processed_cookie:
        # 可以选择删除，或者确保其匹配。为了通用性，我们直接删除
        del processed_cookie['domain']
        
    # 移除 'secure' 和 'httponly' 属性，因为 add_cookie 不直接使用这些布尔值
    # Selenium 会根据上下文和 cookie 其他属性自动处理它们
    if 'secure' in processed_cookie:
        del processed_cookie['secure']
    if 'httponly' in processed_cookie:
        del processed_cookie['httponly']
    
    # 如果存在 'expiry' 且是浮点数，转换为整数，否则可能导致问题
    if 'expiry' in processed_cookie and isinstance(processed_cookie['expiry'], (int, float)):
        processed_cookie['expiry'] = int(processed_cookie['expiry'])


    try:
        web.add_cookie(processed_cookie)
        print(f"✅ 成功添加 Cookie: {processed_cookie.get('name', '未知名称')}")
    except Exception as e:
        print(f"❌ 添加 Cookie 失败 ({processed_cookie.get('name', '未知名称')}): {e}")


# 重新加载页面，使添加的 cookie 生效
web.get(url)
time.sleep(3) # 再次等待页面加载，确保 cookie 生效并登录

# 检查登录状态
soup = BeautifulSoup(web.page_source, 'html.parser')
# print(soup.prettify()) # 调试用，打印完整 HTML

user_login = soup.find('div', id='user-login')

if user_login:
    username_tag = user_login.find('a', href='user.php') # 更精确地查找用户名的a标签
    if username_tag:
        username = username_tag.text.strip()
        print(f"✅ 登入成功，使用者 ID：{username}")
    else:
        print("❌ 找不到使用者名稱")
else:
    print("❌ 尚未登入（找不到 user-login 區塊）。请检查 cookie 是否有效或已正确设置。")


# 领取日常和周常任务
# 再次获取页面源，因为 Lingqu() 函数会点击，页面内容可能改变
soup = BeautifulSoup(web.page_source, 'html.parser')

# 使用更具体的 XPath 定位 '领取' 按钮，而不是 span 标签
# 检查“日常任务”和“周常任务”是否存在可领取的链接
daily_task_link = soup.find('a', href="plugin.php?H_name-tasks.html&action=rece&id=15")
weekly_task_link = soup.find('a', href="plugin.php?H_name-tasks.html&action=rece&id=14")

if daily_task_link and weekly_task_link:
    print('发现日常和周常任务待领取')
    # 直接点击这些链接，而不是通过 id 找到 span 再点击
    web.find_element(By.XPATH, '//a[@href="plugin.php?H_name-tasks.html&action=rece&id=15"]').click()
    time.sleep(1) # 等待点击后页面响应
    web.find_element(By.XPATH, '//a[@href="plugin.php?H_name-tasks.html&action=rece&id=14"]').click()
    time.sleep(1)
    print('✅ 日常和周常任务已触发领取')
    Lingqu()  # 调用 Lingqu 函数来检查并领取进行中的任务

elif daily_task_link:
    print('发现日常任务待领取')
    web.find_element(By.XPATH, '//a[@href="plugin.php?H_name-tasks.html&action=rece&id=15"]').click()
    time.sleep(1)
    print('✅ 日常任务已触发领取')
    Lingqu()

elif weekly_task_link:
    print('发现周常任务待领取')
    web.find_element(By.XPATH, '//a[@href="plugin.php?H_name-tasks.html&action=rece&id=14"]').click()
    time.sleep(1)
    print('✅ 周常任务已触发领取')
    Lingqu()
    
else:
    print('当前页面无待领取的日常或周常任务')

web.quit()
