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

# 在 GitHub Actions 环境中，通常不需要指定 Service 路径，setup-chromedriver 会处理好
web = webdriver.Chrome(options=chrome_options)

# --- 2. 登录流程 ---
base_url = 'https://south-plus.net/plugin.php?H_name-tasks.html'
web.get(base_url) # 必须先访问一次，才能设置对应域的 cookie

for cookie in cookie_data:
    try:
        # 只添加 selenium 支持的关键 cookie 属性
        cookie_to_add = {k: cookie[k] for k in ('name', 'value', 'domain', 'path', 'expiry', 'secure') if k in cookie}
        if 'expiry' in cookie_to_add:
            cookie_to_add['expiry'] = int(cookie_to_add['expiry'])
        web.add_cookie(cookie_to_add)
        print(f"✅ 成功添加 Cookie: {cookie_to_add.get('name')}")
    except Exception as e:
        print(f"❌ 添加 Cookie 失败 ({cookie.get('name')}): {e}")

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
            # 查找申请链接
            apply_link_xpath = f'//a[contains(@href, "action=rece&id={task_id}")]'
            web.find_element(By.XPATH, apply_link_xpath).click()
            print(f"✅ 已申请 '{task_name}'。")
            time.sleep(2) # 等待页面响应

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
             # 如果找不到申请链接，说明任务不可领取或已完成，直接静默处理
            print(f"ℹ️ 未发现或无需处理 '{task_name}'。")


    # 依次处理日常和周常任务
    process_task(15, "日常任务")
    process_task(14, "周常任务")

except Exception as e:
    print(f"❌ 登录失败或在任务处理中发生严重错误。请检查 Cookie 或网站结构。")
    print(f"详细错误: {e}")
    web.save_screenshot('error_screenshot.png') # 保存截图用于调试

finally:
    print("脚本执行完毕。")
    web.quit()
