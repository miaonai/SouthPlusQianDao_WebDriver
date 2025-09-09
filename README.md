## 由[wong001023/SouthPlusQianDao_WebDriver](https://github.com/wong001023/SouthPlusQianDao_WebDriver)二改
-----
修改内容：(Powered by Gemini 2.5 Pro)
1. 去除使用server酱：去除了需要在 Settings 中 Secrets and variables 的 Actions 中 Repository secrets设置serverKey，去除了使用“server酱”通知运行情况

2. cookie_data 初始化和错误处理：初始化 cookie_data = [] 并增加了 exit(1) 在解析失败或未设置环境变量时退出，使程序更健壮。

3. chrome_options 添加 user-agent：有时候设置一个常见的用户代理可以帮助避免一些网站的检测。

4. Cookie 处理循环：
processed_cookie = cookie.copy(): 对 cookie 字典进行复制操作，以避免直接修改原始的 cookie_data。
del processed_cookie['domain']： 这是解决 InvalidCookieDomainException 的关键。移除 domain 属性后，web.add_cookie() 会自动将其设置为主机名（即 south-plus.net），这通常能与你访问的 URL 匹配。
del processed_cookie['secure'] 和 del processed_cookie['httponly']： add_cookie 方法不直接接收这些布尔值作为参数，它们通常是 cookie 字符串解析后才有的。删除它们可以避免潜在的类型不匹配问题。
expiry 类型转换： 确保 expiry 是整数类型，否则也可能导致问题。
增加了成功/失败打印，方便调试。

5. Lingqu() 函数改进：
web.find_element(By.XPATH, '//td[contains(text(), "进行中的任务")]').click() 替代了硬编码的 tr/td 路径，更具文本鲁棒性。
添加了更详细的日常和周常任务领取成功/失败信息。

6. 登录状态检查： 调整了 username_tag = user_login.find('a', href='user.php') 增加 href 属性，使查找更精确。

7. 任务领取逻辑调整：
原先的 weekly_task_1 和 weekly_task_2 变量是基于 span 标签的，但你后面点击的是 img。
现在直接通过 soup.find('a', href="...") 查找具有领取链接的任务，这更可靠地判断任务是否可领取。
关键改变： web.find_element(By.XPATH, '//a[@href="plugin.php?H_name-tasks.html&action=rece&id=15"]').click() 直接点击了“领取”链接，而不是先通过 span 找到再点击内部的 img。这简化了逻辑并提高了稳定性。
在点击领取链接后，添加了 time.sleep(1)，给页面一些时间响应。
-----

- 将 API 获取改成了简单、粗暴、无脑的 WebDriver。
- 在 **Settings** 中设置好 **COOKIE**（需要 JSON 格式的 cookie）
- 运行 Action 即可。
- cookies的格式(按这个格式创建COOKIE变量的值)：
```
[

    {
        "domain": "www.south-plus.net",
        "expiry": 填写对应的时间戳,
        "httpOnly": true,
        "name": "eb9e6_winduser",
        "path": "/",
        "sameSite": "Lax",
        "secure": false,
        "value": "填写自己账号的值"
    },
    {
        "domain": "www.south-plus.net",
        "expiry": 填写对应的时间戳,
        "httpOnly": true,
        "name": "eb9e6_cknum",
        "path": "/",
        "sameSite": "Lax",
        "secure": false,
        "value": "填写自己账号的值"
    }
]
```
### 本地构建要求

请确保安装了 Chrome 和对应版本的 ChromeDriver。

经过测试得出，cookies只需要eb9e6_winduser与eb9e6_cknum两个即可，其他可以删除。有效期是一年。
