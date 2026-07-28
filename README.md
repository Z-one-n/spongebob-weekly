# 🍍 比奇堡周报站 — 海绵宝宝主题周报系统

> "我准备好了！我准备好了！" — 海绵宝宝

一个以**海绵宝宝**为主题的周报管理系统，完全由 **AI 辅助开发（Vibecoding）**，零手写代码。用户可以注册、写周报、浏览他人周报、评论、点赞，系统自动记录浏览量。

---

## 🤖 AI 辅助开发说明

### 使用模型

| 项目 | 详情 |
|------|------|
| **模型** | `deepseek-v4-pro[1M]` |
| **开发方式** | Vibecoding（自然语言描述需求，AI 生成全部代码） |
| **总耗时** | 约 2 小时（从零到完整可运行系统） |
| **代码量** | Python ~500 行 + HTML/CSS ~1800 行 |
| **用户编码量** | 0 行 |

### 开发流程

```
用户描述需求 → AI 规划架构 → AI 生成代码 → 用户测试反馈 → AI 迭代修改
     ↑                                                          |
     └──────────────── 循环迭代，直到满意 ───────────────────────┘
```

每一步用户只需用自然语言描述：「我想要一个海绵宝宝主题的周报系统，有评论和点赞功能」——AI 完成所有编码工作。

---

## 🎯 功能列表

| 功能 | 说明 |
|------|------|
| 🧽 用户注册/登录 | 支持选择海绵宝宝角色头像（海绵宝宝、派大星、蟹老板等 16 个角色） |
| ✍️ 发布/编辑/删除周报 | 选择周数和年份，编写周报标题和内容，支持修改和删除 |
| 👀 浏览周报 | 首页展示所有周报，支持分页（每页 10 篇） |
| 🔍 搜索与筛选 | 按标题/内容关键词搜索，按年份/周数/用户名筛选，可组合使用 |
| 🏷️ 标签页导航 | 最新周报 / 我的周报 / 热门周报 三个标签页自由切换 |
| 👤 用户主页 | 查看某个用户的所有周报和统计数据 |
| 💬 评论功能 | 登录用户可以对任意周报发表评论 |
| ❤️ 点赞功能 | AJAX 异步点赞/取消点赞，水母弹跳动画 |
| 📊 浏览量统计 | 每次打开周报详情页自动 +1 浏览量 |
| 🎭 角色化场景 | 不同状态显示不同角色：蟹老板催周报、派大星迷路 404、章鱼哥表示无结果 |
| 🖼️ 图片背景 | 首页海洋背景、详情/表单纸纹背景、评论区独立背景 |
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
│  │ 10 条路由  │  │ Session  │  │  搜索/排序    │  │
│  └───────────┘  └──────────┘  └──────────────┘  │
│                     │                            │
│               ┌─────┴─────┐                      │
│               │   SQLite   │                      │
│               │  4 张表    │                      │
│               └───────────┘                      │
└─────────────────────────────────────────────────┘
```

### 路由表

| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 首页（标签页 + 搜索筛选 + 分页） |
| `/register` | GET/POST | 用户注册 |
| `/login` | GET/POST | 用户登录 |
| `/logout` | GET | 退出登录 |
| `/report/new` | GET/POST | 创建周报 |
| `/report/<id>` | GET | 查看周报详情 |
| `/report/<id>/edit` | GET/POST | 编辑周报 |
| `/report/<id>/delete` | POST | 删除周报 |
| `/report/<id>/comment` | POST | 发表评论 |
| `/report/<id>/like` | POST | 点赞/取消（AJAX） |
| `/user/<username>` | GET | 用户主页 |
| `/*` | — | 404 派大星迷路页 |

### 技术选型

| 层级 | 技术 | 为什么选择它 |
|------|------|-------------|
| **后端框架** | Flask 3.1 | 轻量级，一个文件就能跑，零基础友好 |
| **数据库** | SQLite | 零配置，文件型数据库，无需安装服务 |
| **模板引擎** | Jinja2 | Flask 内置，在 HTML 中嵌入 Python 变量 |
| **前端样式** | 原生 CSS | 不需要学前端框架，理解 CSS 基础即可 |
| **密码安全** | Werkzeug | Flask 自带，SHA256 哈希加盐 |
| **异步交互** | 原生 JavaScript fetch | 点赞不刷新页面 |
| **字体** | Google Fonts | Lilita One + Noto Sans SC |

---

## 🗄️ 数据库设计

### ER 图

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

### 关键设计决策

- `password_hash` 使用 Werkzeug 加密，不存储原始密码
- `avatar_emoji` 用 Emoji 代替图片上传，简单有趣
- `view_count` 每次访问详情页自动 +1
- `UNIQUE(report_id, user_id)` 确保同一用户对同一周报只能点赞一次
- 删除周报时**级联删除**关联的评论和点赞

---

## 📂 项目文件结构

```
spongebob-weekly/
├── app.py                  # 🌟 Flask 应用主文件（路由、数据库、认证）
├── requirements.txt        # 📦 Python 依赖
├── README.md               # 📖 项目说明文档
├── .gitignore              # 🔒 Git 忽略规则
├── database.db             # 🗄️ SQLite 数据库（运行后自动生成）
├── static/
│   ├── style.css           # 🎨 海绵宝宝主题样式表（~1700 行）
│   ├── background.jpg      # 🖼️ 首页海洋背景
│   ├── paper-bg.jpg        # 🖼️ 详情/表单纸纹背景
│   └── comment-bg.jpg      # 🖼️ 评论区背景
└── templates/
    ├── base.html           # 🏠 基础布局（导航栏、页脚、泡泡动画）
    ├── index.html          # 📰 首页（标签页 + 搜索 + 周报列表）
    ├── login.html          # 🔑 登录
    ├── register.html       # 🧽 注册（可选角色头像）
    ├── report_detail.html  # 👀 周报详情（内容 + 评论 + 点赞）
    ├── report_form.html    # ✍️ 创建/编辑周报
    ├── user_profile.html   # 👤 用户主页
    └── 404.html            # ⭐ 派大星迷路页
```

---

## 🚀 如何运行

```bash
# 1. 克隆项目
git clone https://github.com/Z-one-n/spongebob-weekly.git
cd spongebob-weekly

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python app.py

# 4. 打开浏览器访问
# http://127.0.0.1:5000
```

---

## 🎨 设计思路

### 为什么选择海绵宝宝主题？

1. **辨识度高** — 黄色 + 海洋蓝配色一眼就能认出来
2. **轻松有趣** — 周报本身比较枯燥，用有趣的主题降低抵触感
3. **角色丰富** — 海绵宝宝、派大星、章鱼哥、蟹老板等角色可以自然地映射到不同场景

### 角色-场景映射

| 场景 | 角色 | 设计意图 |
|------|------|---------|
| 🏠 没有周报 | 🦀 蟹老板 | 蟹老板爱钱又暴躁，"快写周报！不然扣你蟹黄堡！"制造紧迫感 |
| 🔍 搜索无结果 | 🦑 章鱼哥 | 章鱼哥总是消极冷淡，"根本就没有这种东西~"贴合角色性格 |
| 👤 未登录 | ⭐ 派大星 | 派大星傻乎乎但友好，"嘿兄弟，先注册才能看哦~"降低门槛 |
| 🧽 没写周报 | 🧽 海绵宝宝 | 海绵宝宝永远积极，"我准备好了！"鼓励用户行动 |
| 404 错误 | ⭐ 派大星 | 派大星经常迷路，404 是最合适的角色，摇摆动画增加趣味 |
| 📋 卡片水印 | 随机角色 | 每张卡片右下角有半透明角色水印，hover 时更明显 |

### 色彩体系

三张背景图各自定位不同的视觉氛围：

| 背景 | 色调 | 用途 | 设计意图 |
|------|------|------|---------|
| 🏠 首页 | 浅黄→深蓝渐变 | 全局背景 | 模拟海底世界的纵深感 |
| 📄 详情/编辑 | 深蓝绿色纸纹 | 内容区域 | 像在海底信纸上阅读，有仪式感 |
| 💬 评论区 | 暗紫棕色纸纹 | 互动区域 | 与内容区形成视觉区分，暗示"这里是讨论区" |

所有内容卡片统一采用 **玻璃态设计**（半透明 + 毛玻璃模糊 + 细白边框），让背景图透出但文字保持可读。

---

## 💬 开发提示词记录

以下是实际开发中使用的关键提示词（翻译整理）：

### 第一阶段：系统搭建

```
现在我要利用vibecoding写一个周报系统，技术栈和ui风格不限，使用Python语言，
整体主题选用海绵宝宝主题，功能有上传周报，其他用户访问和评论，还有点赞和
记录浏览量功能，要求用GitHub托管，并且上传到GitHub以后要在README文件中写
实现思路。我现在是一个零基础小白，请你一步步指导我怎么做
```

→ AI 生成了完整的 Flask 项目：路由、数据库、模板、CSS、README

### 第二阶段：背景图片与配色

```
我想把这张图片铺满初始界面当作背景，并且把整体颜色调整到这个色调
[图片链接]
```

→ AI 下载图片 → 提取调色板 → 更新 CSS 变量 → 设置全屏背景

```
帮我把周记内容和内容编辑界面的背景换成这张图片，并适当调整其他颜色
[图片链接]
```

→ AI 将详情页和编辑页的背景换为纸纹图，调整文字为浅色保证可读性

### 第三阶段：样式打磨

```
我指的是将内容及编辑板块整个部分的背景都换成这张图片，包括标题浏览等等，
仅留出半厘米左右的白色边框就好
```

→ AI 将整张卡片改为纸纹铺满 + 细白边框 + 暗色遮罩

```
文字有些看不清，而且感觉背景有一些喧宾夺主了，透明度再高一点
```

→ AI 加深遮罩 + 添加 backdrop-filter blur 让背景更柔和

### 第四阶段：功能扩展

```
1B 2C 3D 4E
（搜索筛选 + 标签页 + 角色装饰）
```

→ AI 一次性实现三个改进：搜索栏、标签页导航、角色化场景

---

## 🐛 踩坑记录

### 坑 1：Windows GBK 编码导致 Emoji 打印失败

**现象**：启动 Flask 时终端报错 `UnicodeEncodeError: 'gbk' codec can't encode character`

**原因**：Windows 终端默认使用 GBK 编码，无法打印 Emoji 字符

**解决**：在 `app.py` 中将标准输出强制设为 UTF-8：
```python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

### 坑 2：浏览器缓存旧 CSS

**现象**：修改 CSS 后刷新浏览器看不到效果

**原因**：浏览器缓存了旧版本 CSS 文件

**解决**：
- 短期：`Ctrl + Shift + R` 强制刷新
- 长期：在 CSS 引用链接后加版本号 `style.css?v=2`

### 坑 3：GitHub 连接被墙

**现象**：`Failed to connect to github.com:443`

**原因**：中国大陆网络环境限制 GitHub HTTPS 连接

**解决**：配置 Git 代理（Sakuracat 端口 7897）：
```bash
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
```

### 坑 4：Jinja2 模板缺少闭合标签

**现象**：`TemplateSyntaxError: Unexpected end of template`

**原因**：`register.html` 中 `{% block content %}` 打开后忘记写 `{% endblock %}`

**解决**：在模板末尾补上 `{% endblock %}`，写模板时确保每个 `{% block %}` 都有对应闭合

### 坑 5：图片防盗链

**现象**：`curl` 下载知乎图片返回 HTML 而非图片

**原因**：知乎 CDN 检查 Referer 头，拒绝直接下载

**解决**：添加 Referer 和 User-Agent 头：
```bash
curl -L -H "Referer: https://www.zhihu.com/" \
        -H "User-Agent: Mozilla/5.0" \
        -o image.jpg "URL"
```

### 坑 6：数据库文件被进程锁定

**现象**：`rm: cannot remove file: Device or resource busy`

**原因**：旧 Flask 进程仍在运行，SQLite 数据库文件被锁定

**解决**：先 `taskkill //F //IM python.exe` 杀掉所有 Python 进程，再删除

### 坑 7：动态 SQL 查询的复杂性

**现象**：加入搜索和筛选后，SQL 查询变得复杂

**原因**：多个可选筛选条件需要动态构建 WHERE 子句

**解决**：采用「条件列表 + 参数列表」模式，逐步拼接 SQL：
```python
conditions = []
params = []
if search:
    conditions.append("(r.title LIKE ? OR r.content LIKE ?)")
    params.extend([f'%{search}%', f'%{search}%'])
# ... 最后拼接
where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
```

### 坑 8：CSS 覆盖优先级

**现象**：深色背景区域的文字颜色没有按预期变为白色

**原因**：全局样式（如 `.report-detail-header` 中的链接颜色）优先级高于新增的区域样式

**解决**：使用 `!important` 或提高选择器优先级，对深色背景区域内的所有文字元素逐一显式设置颜色

---

## 📚 知识点清单

| 类别 | 知识点 | 对应位置 |
|------|--------|---------|
| **Python** | 函数、装饰器、条件判断、列表操作 | `app.py` |
| **Flask** | 路由装饰器、Session、Flash 消息、错误处理 | `@app.route`, `session`, `flash`, `@app.errorhandler` |
| **HTTP** | GET/POST 方法、请求参数、重定向 | `request.args`, `redirect`, `url_for` |
| **Jinja2** | 模板继承、循环、条件、过滤器 | `{% extends %}`, `{% for %}`, `{% if %}` |
| **SQLite** | CRUD、JOIN、GROUP BY、聚合函数、外键约束 | SELECT/INSERT/UPDATE/DELETE |
| **安全** | 密码哈希、Session 加密、SQL 参数化防注入 | `generate_password_hash`, `?` 占位符 |
| **CSS** | 变量系统、Flexbox、动画、响应式、毛玻璃效果 | `:root`, `@keyframes`, `@media`, `backdrop-filter` |
| **JavaScript** | fetch API、DOM 操作、事件处理 | AJAX 点赞功能 |
| **Git** | init/add/commit/push、代理配置 | 版本控制全流程 |
| **运维** | 端口占用排查、进程管理、编码处理 | `netstat`, `taskkill`, UTF-8 |

---

## 📄 License

MIT — 自由使用，记得给蟹老板写周报！

---

> 💛 Built with SpongeBob Love | 🐍 Python + Flask | 🤖 AI-Powered by deepseek-v4-pro | 🍍 比奇堡出品
