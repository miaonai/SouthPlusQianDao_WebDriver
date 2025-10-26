from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
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
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

web = webdriver.Chrome(options=chrome_options)

# --- 启用 Stealth 模式，对抗反爬虫 ---
stealth(web,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# --- 2. 登录流程 ---
base_url = 'https://south-plus.net/plugin.php?H_name-tasks.html'
web.get(base_url)

for cookie in cookie_data:
    try:
        cookie_to_add = {}
        cookie_to_add['name'] = cookie['name']
        cookie_to_add['value'] = cookie['value']
        if 'path' in cookie: cookie_to_add['path'] = cookie['path']
        if 'secure' in cookie: cookie_to_add['secure'] = cookie['secure']
        if 'httpOnly' in cookie: cookie_to_add['httpOnly'] = cookie['httpOnly']
        if 'sameSite' in cookie and cookie['sameSite'] is not None: cookie_to_add['sameSite'] = cookie['sameSite']
        if 'expiry' in cookie:
            cookie_to_add['expiry'] = int(cookie['expiry'])
        elif 'expirationDate' in cookie:
            cookie_to_add['expiry'] = int(cookie['expirationDate'])
        
        web.add_cookie(cookie_to_add)
        print(f"✅ 成功添加 Cookie: {cookie_to_add.get('name')}")
    except Exception as e:
        print(f"❌ 添加 Cookie 失败 ({cookie.get('name', '未知名称')}): {e}")

web.get(base_url)

# --- 3. 验证登录并执行任务 ---
try:
    user_login_element = WebDriverWait(web, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#user-login a[href='user.php']"))
    )
    username = user_login_element.text.strip()
    print(f"✅ 登入成功，使用者 ID：{username}")

    def process_task(task_id, task_name):
        try:
            apply_link_xpath = f'//a[contains(@href, "action=rece&id={task_id}")]'
            web.find_element(By.XPATH, apply_link_xpath).click()
            print(f"✅ 已申请 '{task_name}'。")
            time.sleep(2)
            ongoing_tasks_button = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//td[contains(text(), "进行中的任务")]'))
            )
            ongoing_tasks_button.click()
            print("✅ 已切换到进行中的任务页面。")
            time.sleep(2)
            complete_button_xpath = f'//*[@id="both_{task_id}"]/a/img'
            WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH, complete_button_xpath))).click()
            print(f"✅ '{task_name}' 任务领取成功！")
            web.get(base_url)
            time.sleep(2)
        except Exception:
            print(f"ℹ️ 未发现或无需处理 '{task_name}'。")

    process_task(15, "日常任务")
    process_task(14, "周常任务")


except Exception as e:
    print(f"❌ 登录失败或在任务处理中发生严重错误。请检查 Cookie 或网站结构。")
    print(f"详细错误: {e}")
    
    # --- NEW DEBUGGING LINES ---
    print("\n--- BEGIN FAILURE PAGE SOURCE ---")
    print(web.page_source)
    print("--- END FAILURE PAGE SOURCE ---\n")
    # ---------------------------

    screenshot_path = os.path.join(os.getcwd(), 'error_screenshot.png')
    web.save_screenshot(screenshot_path)
    print(f"📷 已保存错误截图至: {screenshot_path}")

finally:
    print("脚本执行完毕。")
    web.quit()
