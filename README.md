# 🍍 比奇堡周报站 — 海绵宝宝主题周报系统

> "我准备好了！我准备好了！" — 海绵宝宝

一个以**海绵宝宝**为主题的周报管理系统，用户可以注册、写周报、浏览他人周报、评论、点赞，系统自动记录浏览量。

---

## 🎯 功能列表

| 功能 | 说明 |
|------|------|
| 🧽 用户注册/登录 | 支持选择海绵宝宝角色头像（海绵宝宝、派大星、蟹老板等） |
| ✍️ 发布周报 | 选择周数和年份，编写周报标题和内容 |
| 👀 浏览周报 | 首页展示所有周报，支持分页（每页 10 篇） |
| 👤 用户主页 | 查看某个用户的所有周报和统计数据 |
| 💬 评论功能 | 登录用户可以对任意周报发表评论 |
| ❤️ 点赞功能 | AJAX 异步点赞/取消点赞，带弹出动画 |
| 📊 浏览量统计 | 每次打开周报详情页自动 +1 浏览量 |
| 📱 响应式设计 | 支持手机、平板、电脑访问 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────┐
│                   用户浏览器                       │
│              (HTML + CSS + JavaScript)           │
└────────────────────┬────────────────────────────┘
                     │ HTTP 请求
                     ▼
┌─────────────────────────────────────────────────┐
│               Flask Web 服务器                    │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  路由层    │  │  认证层   │  │  业务逻辑层   │  │
│  │ Routes    │  │ Auth     │  │  Services    │  │
│  └───────────┘  └──────────┘  └──────────────┘  │
│                     │                            │
│               ┌─────┴─────┐                      │
│               │   SQLite   │                      │
│               │  数据库    │                      │
│               └───────────┘                      │
└─────────────────────────────────────────────────┘
```

### 技术选型

| 层级 | 技术 | 为什么选择它 |
|------|------|-------------|
| **后端框架** | Flask | 轻量级，适合初学者，一个文件就能跑起来 |
| **数据库** | SQLite | 零配置，不需要单独安装数据库服务 |
| **模板引擎** | Jinja2 | Flask 内置，在 HTML 中嵌入 Python 变量 |
| **前端样式** | 原生 CSS | 不用学框架，理解 CSS 基础 |
| **密码安全** | Werkzeug | Flask 自带，SHA256 哈希加盐 |
| **字体** | Google Fonts | Lilita One + Noto Sans SC |

---

## 🗄️ 数据库设计

### ER 图（实体关系图）

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  users   │       │   reports    │       │ comments │
├──────────┤       ├──────────────┤       ├──────────┤
│ id (PK)  │──1:N──│ user_id (FK) │       │ id (PK)  │
│ username │       │ id (PK)      │──1:N──│report_id │
│ password │       │ title        │       │ user_id  │
│ avatar   │       │ content      │       │ content  │
│created_at│       │ week_number  │       │created_at│
└──────────┘       │ year         │       └──────────┘
                   │ view_count   │
                   │ created_at   │       ┌──────────┐
                   │ updated_at   │       │  likes   │
                   └──────────────┘       ├──────────┤
                                          │ id (PK)  │
                                          │report_id │──(report_id, user_id)
                                          │ user_id  │  联合唯一约束
                                          │created_at│
                                          └──────────┘
```

### 表结构说明

**users 表** — 存储用户信息
- `password_hash` 使用 Werkzeug 加密，不存储原始密码
- `avatar_emoji` 用 Emoji 代替图片上传，简单有趣

**reports 表** — 存储周报
- `week_number` + `year` 标识是哪一周的周报
- `view_count` 每次访问详情页自动 +1

**comments 表** — 存储评论
- 通过 `report_id` 关联到周报
- 删除周报时级联删除评论

**likes 表** — 存储点赞
- `UNIQUE(report_id, user_id)` 确保同一用户对同一周报只能点赞一次

---

## 📂 项目文件结构

```
spongebob-weekly/
├── app.py                  # 🌟 核心：Flask 应用主文件
├── requirements.txt        # 📦 Python 依赖列表
├── README.md               # 📖 项目说明文档（你正在读的这个）
├── database.db             # 🗄️ SQLite 数据库（运行后自动生成）
├── static/
│   └── style.css           # 🎨 海绵宝宝主题样式表
└── templates/
    ├── base.html           # 🏠 基础布局模板（导航栏、页脚、泡泡动画）
    ├── index.html          # 📰 首页 — 周报列表
    ├── login.html          # 🔑 登录页面
    ├── register.html       # 🧽 注册页面（可选头像）
    ├── report_detail.html  # 👀 周报详情 + 评论 + 点赞
    ├── report_form.html    # ✍️ 创建/编辑周报表单
    └── user_profile.html   # 👤 用户主页
```

---

## 🚀 如何运行

### 第一步：安装 Python

确保你的电脑安装了 **Python 3.9 或以上版本**。

```bash
# 检查 Python 版本
python --version
```

如果没装 Python，去 [python.org](https://www.python.org/downloads/) 下载安装。

### 第二步：下载项目

```bash
git clone https://github.com/YOUR_USERNAME/spongebob-weekly.git
cd spongebob-weekly
```

### 第三步：安装依赖

```bash
pip install -r requirements.txt
```

### 第四步：启动应用

```bash
python app.py
```

### 第五步：打开浏览器

访问 **http://127.0.0.1:5000** 🎉

---

## 🎨 设计思路

### 为什么选择海绵宝宝主题？

1. **辨识度高** — 海绵宝宝的黄色 + 海洋蓝配色让人一眼就能认出来
2. **轻松有趣** — 周报本身就是比较枯燥的事情，用有趣的主题降低抵触感
3. **角色丰富** — 海绵宝宝、派大星、章鱼哥、蟹老板等角色可以自然地映射到系统功能中

### UI 设计细节

| 设计元素 | 实现方式 | 灵感来源 |
|----------|---------|---------|
| 🫧 背景泡泡 | CSS `@keyframes` 动画，6 个不同大小/速度/位置的泡泡 | 海底世界的泡泡 |
| 🍍 跳动菠萝 | 导航栏 Logo 使用 `pineapple-bounce` 动画 | 海绵宝宝的菠萝屋 |
| 🟡 黄色导航栏 | 渐变黄色背景 + 棕色底部边框 | 海绵宝宝的身体颜色 |
| 🌊 蓝色背景 | 多层蓝色渐变，模拟海洋深度 | 比奇堡的海底世界 |
| 🟤 棕色文字 | 深棕色代替纯黑色文字 | 沙滩和海底的颜色 |
| 🎭 Emoji 头像 | 注册时选择海绵宝宝角色 Emoji | 不用上传图片，简单有趣 |
| 💬 Flash 消息 | 滑入动画 + 自动消失 | 比奇堡的对话气泡 |
| ❤️ 点赞动画 | `scale(1.2)` 弹出效果 | 海绵宝宝的夸张表情 |

### 后端设计思路

#### 1. 为什么用 Flask 而不是 Django？

Flask 更轻量，一个文件就能跑，对新手友好。Django 功能更全但学习曲线陡峭。

#### 2. 为什么用 SQLite 而不是 MySQL？

SQLite 是文件型数据库，不需要安装和配置数据库服务，`database.db` 一个文件就是整个数据库。

#### 3. 密码安全

所有用户密码使用 `Werkzeug.generate_password_hash()` 加密存储，即使数据库泄露，攻击者也无法知道原始密码。

#### 4. Session 管理

登录状态通过 Flask 的加密 Session 实现，Session 数据存储在用户浏览器的 Cookie 中，服务器端用 `secret_key` 加密验证。

#### 5. AJAX 点赞

点赞功能使用 JavaScript `fetch()` API 发送异步请求，不刷新页面就能更新点赞状态，用户体验更好。

---

## 📚 你从中学到了什么？

### 如果你是零基础小白，这个项目涵盖了：

| 知识点 | 对应代码 |
|--------|---------|
| **Python 基础** | 变量、函数、装饰器、条件判断、循环 |
| **Flask 路由** | `@app.route('/')` 定义 URL 和视图函数 |
| **HTTP 请求方法** | GET（查看）、POST（提交表单） |
| **Jinja2 模板** | `{% for %}`, `{% if %}`, `{{ variable }}` |
| **SQL 数据库操作** | SELECT, INSERT, UPDATE, DELETE |
| **数据库关系** | 一对多（用户→周报）、外键、级联删除 |
| **用户认证** | Session 登录/登出、密码哈希 |
| **HTML 表单** | input, textarea, select, form |
| **CSS 布局** | Flexbox, Grid, 响应式媒体查询 |
| **CSS 动画** | @keyframes, transition, transform |
| **JavaScript DOM** | 事件监听、AJAX fetch、DOM 操作 |
| **Git & GitHub** | clone, add, commit, push |

---

## 🔮 未来可以改进的方向

- [ ] 🖼️ 支持 Markdown 格式写周报
- [ ] 📧 邮件提醒（有人评论/点赞时通知）
- [ ] 🔍 周报搜索功能
- [ ] 📊 周报数据统计图表
- [ ] 🌐 部署到云服务器（Render / Railway）
- [ ] 🔑 OAuth 第三方登录（GitHub / Google）
- [ ] 🎨 更多主题皮肤（派大星粉色主题、章鱼哥蓝色主题）

---

## 📄 License

MIT — 自由使用，记得给蟹老板写周报！

---

> 💛 Built with SpongeBob Love | 🐍 Python + Flask | 🍍 比奇堡出品
