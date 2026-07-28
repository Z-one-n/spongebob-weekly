"""
🦀 海绵宝宝周报系统 - SpongeBob Weekly Report System
====================================================
一个以海绵宝宝为主题的周报管理系统
A weekly report management system with SpongeBob SquarePants theme

技术栈: Python + Flask + SQLite + 原生 HTML/CSS
"""

import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# 🍍 Flask 应用初始化
# ============================================================
app = Flask(__name__)
app.secret_key = 'spongebob-lives-in-a-pineapple-under-the-sea'  # 用于 session 加密
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


# ============================================================
# 🗄️ 数据库工具函数
# ============================================================

def get_db():
    """获取数据库连接（每个请求复用同一个连接）"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # 让查询结果可以用列名访问
        g.db.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束后关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库表结构（首次运行时自动创建）"""
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_emoji TEXT DEFAULT '🧽',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            week_number INTEGER NOT NULL,
            year INTEGER NOT NULL,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(report_id, user_id),
            FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    db.commit()
    db.close()


# 应用启动时自动初始化数据库
with app.app_context():
    init_db()


# ============================================================
# 🧰 模板辅助函数
# ============================================================

@app.context_processor
def utility_processor():
    """为所有模板提供辅助函数"""
    def make_tab_url(tab_name):
        """切换标签页时保留搜索和筛选参数"""
        args = {}
        for key in ['search', 'year', 'week', 'user']:
            val = request.args.get(key, '').strip()
            if val:
                args[key] = val
        args['tab'] = tab_name
        from flask import url_for as _url_for
        return _url_for('index', **args)

    def make_page_url(page_num):
        """分页链接保留所有参数"""
        args = {}
        for key in ['tab', 'search', 'year', 'week', 'user']:
            val = request.args.get(key, '').strip()
            if val:
                args[key] = val
        args['page'] = page_num
        from flask import url_for as _url_for
        return _url_for('index', **args)

    return dict(make_tab_url=make_tab_url, make_page_url=make_page_url)


# ============================================================
# 🔐 用户认证装饰器
# ============================================================

def login_required(f):
    """要求用户登录才能访问的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('🧽 要先登录才能访问这个页面哦！', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# 🏠 首页 - 浏览所有周报（支持搜索/筛选/标签页）
# ============================================================

@app.route('/')
def index():
    """首页：展示周报，支持分页、搜索、筛选、标签页切换"""
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'latest')  # latest | mine | popular
    search = request.args.get('search', '').strip()
    filter_year = request.args.get('year', '', type=str)
    filter_week = request.args.get('week', '', type=str)
    filter_user = request.args.get('user', '').strip()

    per_page = 10
    offset = (page - 1) * per_page
    db = get_db()

    # 构建动态查询条件
    conditions = []
    params = []

    if search:
        conditions.append("(r.title LIKE ? OR r.content LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])

    if filter_year:
        conditions.append("r.year = ?")
        params.append(int(filter_year))

    if filter_week:
        conditions.append("r.week_number = ?")
        params.append(int(filter_week))

    if filter_user:
        conditions.append("u.username LIKE ?")
        params.append(f'%{filter_user}%')

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # 标签页：我的周报
    if tab == 'mine' and 'user_id' in session:
        if where_clause:
            where_clause += " AND r.user_id = ?"
        else:
            where_clause = "WHERE r.user_id = ?"
        params.append(session['user_id'])

    # 排序方式
    if tab == 'popular':
        order_by = "ORDER BY (COUNT(DISTINCT l.id) * 2 + r.view_count) DESC, r.created_at DESC"
    else:
        order_by = "ORDER BY r.created_at DESC"

    # 查询周报总数
    count_sql = f"""
        SELECT COUNT(DISTINCT r.id)
        FROM reports r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN likes l ON r.id = l.report_id
        LEFT JOIN comments c ON r.id = c.report_id
        {where_clause}
    """
    total = db.execute(count_sql, params).fetchone()[0]

    # 查询当前页的周报
    query_sql = f"""
        SELECT
            r.*,
            u.username,
            u.avatar_emoji,
            COUNT(DISTINCT l.id) AS like_count,
            COUNT(DISTINCT c.id) AS comment_count
        FROM reports r
        JOIN users u ON r.user_id = u.id
        LEFT JOIN likes l ON r.id = l.report_id
        LEFT JOIN comments c ON r.id = c.report_id
        {where_clause}
        GROUP BY r.id
        {order_by}
        LIMIT ? OFFSET ?
    """
    reports = db.execute(query_sql, params + [per_page, offset]).fetchall()

    total_pages = max(1, (total + per_page - 1) // per_page)

    # 获取所有年份和周数用于筛选下拉
    all_years = db.execute(
        "SELECT DISTINCT year FROM reports ORDER BY year DESC"
    ).fetchall()

    # 保留搜索参数用于分页链接
    filter_params = {}
    for key in ['tab', 'search', 'year', 'week', 'user']:
        val = request.args.get(key, '').strip()
        if val:
            filter_params[key] = val

    return render_template('index.html',
                           reports=reports,
                           page=page,
                           total_pages=total_pages,
                           tab=tab,
                           search=search,
                           filter_year=filter_year,
                           filter_week=filter_week,
                           filter_user=filter_user,
                           all_years=all_years,
                           filter_params=filter_params)


# ============================================================
# 👤 用户注册
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        avatar_emoji = request.form.get('avatar_emoji', '🧽').strip()

        # 表单验证
        if not username or not password:
            flash('🐌 用户名和密码不能为空！', 'danger')
            return render_template('register.html')

        if len(username) < 2 or len(username) > 20:
            flash('🐌 用户名长度需要在 2-20 个字符之间！', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('🐌 密码长度至少需要 6 个字符！', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('🐌 两次输入的密码不一致！', 'danger')
            return render_template('register.html')

        db = get_db()

        # 检查用户名是否已存在
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing:
            flash('🐌 这个用户名已经被注册了，换一个试试吧！', 'danger')
            return render_template('register.html')

        # 创建用户（密码加密存储）
        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash, avatar_emoji) VALUES (?, ?, ?)",
            (username, password_hash, avatar_emoji)
        )
        db.commit()

        flash('🎉 注册成功！欢迎来到比奇堡！现在可以登录啦~', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ============================================================
# 🔑 用户登录
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录页面"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('🐌 请输入用户名和密码！', 'danger')
            return render_template('login.html')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('🐌 用户名或密码错误！', 'danger')
            return render_template('login.html')

        # 登录成功，保存用户信息到 session
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['avatar_emoji'] = user['avatar_emoji']

        flash(f'🦀 欢迎回来，{username}！今天抓水母了吗？', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


# ============================================================
# 🚪 用户登出
# ============================================================

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('👋 再见！记得下次回比奇堡看看哦~', 'info')
    return redirect(url_for('index'))


# ============================================================
# 📝 创建周报
# ============================================================

@app.route('/report/new', methods=['GET', 'POST'])
@login_required
def create_report():
    """创建新的周报"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        week_number = request.form.get('week_number', type=int)
        year = request.form.get('year', type=int)

        # 表单验证
        if not title or not content:
            flash('🐌 标题和内容不能为空！', 'danger')
            return render_template('report_form.html',
                                   is_edit=False,
                                   today=datetime.now())

        if not week_number or not year:
            flash('🐌 请选择周数和年份！', 'danger')
            return render_template('report_form.html',
                                   is_edit=False,
                                   today=datetime.now())

        db = get_db()
        db.execute(
            """INSERT INTO reports (user_id, title, content, week_number, year)
               VALUES (?, ?, ?, ?, ?)""",
            (session['user_id'], title, content, week_number, year)
        )
        db.commit()

        flash('🎉 周报发布成功！蟹老板会为你骄傲的！', 'success')
        return redirect(url_for('index'))

    # GET 请求：显示创建表单
    return render_template('report_form.html',
                           is_edit=False,
                           today=datetime.now())


# ============================================================
# 👀 查看周报详情
# ============================================================

@app.route('/report/<int:report_id>')
def view_report(report_id):
    """查看单篇周报的详细内容"""
    db = get_db()

    # 查询周报详情（包含作者信息）
    report = db.execute("""
        SELECT r.*, u.username, u.avatar_emoji
        FROM reports r
        JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
    """, (report_id,)).fetchone()

    if report is None:
        flash('🐌 这篇周报不存在的！', 'danger')
        return redirect(url_for('index'))

    # 浏览量 +1
    db.execute(
        "UPDATE reports SET view_count = view_count + 1 WHERE id = ?",
        (report_id,)
    )
    db.commit()

    # 查询点赞数
    like_count = db.execute(
        "SELECT COUNT(*) FROM likes WHERE report_id = ?", (report_id,)
    ).fetchone()[0]

    # 当前用户是否已点赞
    user_liked = False
    if 'user_id' in session:
        liked = db.execute(
            "SELECT id FROM likes WHERE report_id = ? AND user_id = ?",
            (report_id, session['user_id'])
        ).fetchone()
        user_liked = liked is not None

    # 查询所有评论
    comments = db.execute("""
        SELECT c.*, u.username, u.avatar_emoji
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.report_id = ?
        ORDER BY c.created_at ASC
    """, (report_id,)).fetchall()

    return render_template('report_detail.html',
                           report=report,
                           like_count=like_count,
                           user_liked=user_liked,
                           comments=comments)


# ============================================================
# ✏️ 编辑周报
# ============================================================

@app.route('/report/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    """编辑自己的周报"""
    db = get_db()

    report = db.execute(
        "SELECT * FROM reports WHERE id = ?", (report_id,)
    ).fetchone()

    if report is None:
        flash('🐌 这篇周报不存在！', 'danger')
        return redirect(url_for('index'))

    # 只能编辑自己的周报
    if report['user_id'] != session['user_id']:
        flash('🚫 你只能编辑自己的周报哦！', 'danger')
        return redirect(url_for('view_report', report_id=report_id))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        week_number = request.form.get('week_number', type=int)
        year = request.form.get('year', type=int)

        if not title or not content:
            flash('🐌 标题和内容不能为空！', 'danger')
            return render_template('report_form.html',
                                   is_edit=True,
                                   report=report,
                                   today=datetime.now())

        db.execute(
            """UPDATE reports
               SET title = ?, content = ?, week_number = ?, year = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, content, week_number, year, report_id)
        )
        db.commit()

        flash('✅ 周报更新成功！', 'success')
        return redirect(url_for('view_report', report_id=report_id))

    return render_template('report_form.html',
                           is_edit=True,
                           report=report,
                           today=datetime.now())


# ============================================================
# 🗑️ 删除周报
# ============================================================

@app.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """删除自己的周报"""
    db = get_db()

    report = db.execute(
        "SELECT * FROM reports WHERE id = ?", (report_id,)
    ).fetchone()

    if report is None:
        flash('🐌 这篇周报不存在！', 'danger')
        return redirect(url_for('index'))

    if report['user_id'] != session['user_id']:
        flash('🚫 你只能删除自己的周报哦！', 'danger')
        return redirect(url_for('view_report', report_id=report_id))

    db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    db.commit()

    flash('🗑️ 周报已删除！', 'info')
    return redirect(url_for('index'))


# ============================================================
# 💬 发表评论
# ============================================================

@app.route('/report/<int:report_id>/comment', methods=['POST'])
@login_required
def add_comment(report_id):
    """为周报添加评论"""
    content = request.form.get('content', '').strip()

    if not content:
        flash('🐌 评论内容不能为空！', 'danger')
        return redirect(url_for('view_report', report_id=report_id))

    if len(content) > 1000:
        flash('🐌 评论内容太长了，控制在 1000 字以内吧！', 'danger')
        return redirect(url_for('view_report', report_id=report_id))

    db = get_db()

    # 确认周报存在
    report = db.execute(
        "SELECT id FROM reports WHERE id = ?", (report_id,)
    ).fetchone()

    if report is None:
        flash('🐌 这篇周报不存在！', 'danger')
        return redirect(url_for('index'))

    db.execute(
        "INSERT INTO comments (report_id, user_id, content) VALUES (?, ?, ?)",
        (report_id, session['user_id'], content)
    )
    db.commit()

    flash('💬 评论发表成功！', 'success')
    return redirect(url_for('view_report', report_id=report_id))


# ============================================================
# ❤️ 点赞 / 取消点赞 (AJAX 接口)
# ============================================================

@app.route('/report/<int:report_id>/like', methods=['POST'])
@login_required
def toggle_like(report_id):
    """切换点赞状态（AJAX）"""
    db = get_db()

    # 确认周报存在
    report = db.execute(
        "SELECT id FROM reports WHERE id = ?", (report_id,)
    ).fetchone()

    if report is None:
        return jsonify({'error': '周报不存在'}), 404

    # 检查是否已点赞
    existing = db.execute(
        "SELECT id FROM likes WHERE report_id = ? AND user_id = ?",
        (report_id, session['user_id'])
    ).fetchone()

    if existing:
        # 取消点赞
        db.execute(
            "DELETE FROM likes WHERE report_id = ? AND user_id = ?",
            (report_id, session['user_id'])
        )
        db.commit()
        liked = False
    else:
        # 点赞
        db.execute(
            "INSERT INTO likes (report_id, user_id) VALUES (?, ?)",
            (report_id, session['user_id'])
        )
        db.commit()
        liked = True

    # 获取最新的点赞数
    like_count = db.execute(
        "SELECT COUNT(*) FROM likes WHERE report_id = ?", (report_id,)
    ).fetchone()[0]

    return jsonify({
        'liked': liked,
        'like_count': like_count
    })


# ============================================================
# 👤 用户主页
# ============================================================

@app.route('/user/<username>')
def user_profile(username):
    """查看用户的所有周报"""
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if user is None:
        flash('🐌 这个用户不存在！', 'danger')
        return redirect(url_for('index'))

    # 查询该用户的所有周报
    reports = db.execute("""
        SELECT
            r.*,
            COUNT(DISTINCT l.id) AS like_count,
            COUNT(DISTINCT c.id) AS comment_count
        FROM reports r
        LEFT JOIN likes l ON r.id = l.report_id
        LEFT JOIN comments c ON r.id = c.report_id
        WHERE r.user_id = ?
        GROUP BY r.id
        ORDER BY r.created_at DESC
    """, (user['id'],)).fetchall()

    # 统计总浏览量和总点赞数
    stats = db.execute("""
        SELECT
            COALESCE(SUM(view_count), 0) AS total_views,
            COUNT(*) AS total_reports
        FROM reports
        WHERE user_id = ?
    """, (user['id'],)).fetchone()

    return render_template('user_profile.html',
                           user=user,
                           reports=reports,
                           stats=stats)


# ============================================================
# 🎭 错误页面
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    """404 页面 — 派大星迷路主题"""
    return render_template('404.html'), 404


# ============================================================
# 🚀 启动应用
# ============================================================

if __name__ == '__main__':
    # 设置标准输出编码为 UTF-8（Windows 兼容）
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("""
    🍍  海绵宝宝周报系统  🍍
    ============================
    🌊  比奇堡周报站启动成功！
    📍  访问地址: http://127.0.0.1:5000
    🦀  蟹老板提醒：记得写周报哦~
    ============================
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
