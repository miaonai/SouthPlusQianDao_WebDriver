from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

# --- 1. 环境和配置初始化 ---
cookie_json = os.environ.get('COOKIE')
if not cookie_json:
    print("❌ 错误：COOKIE 环境变量未设置。请确保已配置。")
    exit(1)

try:
    cookie_data = json.loads(cookie_json)
    print("✅ 成功解析 COOKIE 环境变量。")
except json.JSONDecodeError:
    print("❌ 错误：无法解析 COOKIE 环境变量为 JSON。请检查其格式。")
    exit(1)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

web = webdriver.Chrome(options=chrome_options)

# --- 2. 登录流程 ---
base_url = 'https://south-plus.net/plugin.php?H_name-tasks.html'
web.get(base_url) # 必须先访问一次，才能为当前域设置 cookie

# --- 智能 Cookie 处理循环 ---
for cookie in cookie_data:
    try:
        # 创建一个干净的字典，只包含 selenium.add_cookie 支持的键
        cookie_to_add = {}
        
        # 必填项
        cookie_to_add['name'] = cookie['name']
        cookie_to_add['value'] = cookie['value']
        
        # 可选但常用的项
        if 'path' in cookie:
            cookie_to_add['path'] = cookie['path']
        if 'secure' in cookie:
            cookie_to_add['secure'] = cookie['secure']
        if 'httpOnly' in cookie:
            cookie_to_add['httpOnly'] = cookie['httpOnly']
        if 'sameSite' in cookie and cookie['sameSite'] is not None:
             cookie_to_add['sameSite'] = cookie['sameSite']
             
        # 【关键优化】智能处理 'expiry' 和 'expirationDate'
        if 'expiry' in cookie:
            cookie_to_add['expiry'] = int(cookie['expiry'])
        elif 'expirationDate' in cookie:
            cookie_to_add['expiry'] = int(cookie['expirationDate'])
        
        # 【关键修复】不添加 'domain' 键，让 Selenium 自动从当前 URL 推断
        # 这可以完美解决 'www.' 前缀导致的 domain mismatch 问题

        web.add_cookie(cookie_to_add)
        print(f"✅ 成功添加 Cookie: {cookie_to_add.get('name')}")
    except Exception as e:
        print(f"❌ 添加 Cookie 失败 ({cookie.get('name', '未知名称')}): {e}")


web.get(base_url) # 刷新页面以应用 cookie

# --- 3. 验证登录并执行任务 ---
try:
    # 使用 WebDriverWait 显式等待登录成功的标志
    user_login_element = WebDriverWait(web, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#user-login a[href='user.php']"))
    )
    username = user_login_element.text.strip()
    print(f"✅ 登入成功，使用者 ID：{username}")

    # 封装的任务处理函数
    def process_task(task_id, task_name):
        try:
            # 查找并点击申请链接
            apply_link_xpath = f'//a[contains(@href, "action=rece&id={task_id}")]'
            web.find_element(By.XPATH, apply_link_xpath).click()
            print(f"✅ 已申请 '{task_name}'。")
            time.sleep(2)

            # 点击“进行中的任务”
            ongoing_tasks_button = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//td[contains(text(), "进行中的任务")]'))
            )
            ongoing_tasks_button.click()
            print("✅ 已切换到进行中的任务页面。")
            time.sleep(2)

            # 点击完成任务
            complete_button_xpath = f'//*[@id="both_{task_id}"]/a/img'
            WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH, complete_button_xpath))).click()
            print(f"✅ '{task_name}' 任务领取成功！")
            
            # 返回任务主页以便处理下一个
            web.get(base_url)
            time.sleep(2)

        except Exception:
            print(f"ℹ️ 未发现或无需处理 '{task_name}'。")


    # 依次处理日常和周常任务
    process_task(15, "日常任务")
    process_task(14, "周常任务")

except Exception as e:
    print(f"❌ 登录失败或在任务处理中发生严重错误。请检查 Cookie 或网站结构。")
    print(f"详细错误: {e}")
    # 在 GitHub Actions 中保存截图对于调试非常有帮助
    screenshot_path = os.path.join(os.getcwd(), 'error_screenshot.png')
    web.save_screenshot(screenshot_path)
    print(f"📷 已保存错误截图至: {screenshot_path}")

finally:
    print("脚本执行完毕。")
    web.quit()
