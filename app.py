from ast import Pass
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# 配置 MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'complains'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# 初始化 MySQL
mysql = MySQL(app)

# 首页
@app.route('/')
def index():
   return render_template('home.html')

# 关于
@app.route('/about')
def about():
   return render_template('about.html')

# 文章列表
@app.route('/articles')
def articles():
   # 创建 cursor
   cur = mysql.connection.cursor()

   # 获取文章
   result = cur.execute("SELECT * FROM articles")

   articles = cur.fetchall()

   # 关闭连接
   cur.close()

   if result > 0:
      return render_template("articles.html", articles=articles)
   else:
      msg = "没有文章"
      return render_template('articles.html', msg=msg)

# 单篇文章
@app.route('/article/<string:id>/')
def article(id):
   # 创建 cursor
   cur = mysql.connection.cursor()

   # 获取文章
   result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

   article = cur.fetchone()

   return render_template('article.html', article=article)

# 注册表单类
class RegisterForm(Form):
   name = StringField('名字', [validators.Length(min=1, max=50)])
   username = StringField('笔名', [validators.Length(min=4, max=25)])
   email = StringField('邮箱', [validators.Length(min=6, max=50)])
   password = PasswordField('密码', [
      validators.DataRequired(),
      validators.EqualTo('confirm', message='密码不匹配')
   ])
   confirm = PasswordField('确认密码')

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
   form = RegisterForm(request.form)
   if request.method == 'POST' and form.validate():
      name = form.name.data
      email = form.email.data
      username = form.username.data
      password = sha256_crypt.encrypt(str(form.password.data))

      # 创建 cursor
      cur = mysql.connection.cursor()
      cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

      # 提交到数据库
      mysql.connection.commit()

      # 关闭连接
      cur.close()

      flash("注册成功，请登录", 'success')

      return redirect(url_for('login'))

   return render_template('register.html', form=form)

# 用户登录
@app.route("/login", methods=['GET','POST'])
def login():
   if request.method == 'POST':
      # 获取表单字段
      username = request.form['username']
      password_candidate = request.form['password']

      # 创建 cursor
      cur = mysql.connection.cursor()
      
      # 根据笔名获取用户
      result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

      if result > 0:
         # 获取存储的哈希值
         data = cur.fetchone()
         password = data['password']

         # Compare passwords
         # 比较密码
         if sha256_crypt.verify(password_candidate, password):
             # 通过验证
             session['logged_in'] = True
             session['username'] = username
         
             flash('您已成功登录', 'success')
             return redirect(url_for('dashboard'))
         else:
             error = '登录无效'
             return render_template('login.html', error=error)
         
         # 关闭连接
         cur.close()
         

      else:
         error = '笔名已存在'
         return render_template('login.html', error=error)

   return render_template('login.html')

#检查用户是否已经登录
def is_logged_in(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if 'logged_in' in session:
         return f(*args, **kwargs)
      else:
         flash("未经授权,请登录", "danger")
         return redirect(url_for("login"))
   return wrap

# 用户推出
@app.route('/logout')
@is_logged_in
def logout():
   session.clear()
   flash("你已退出", "success")
   return redirect(url_for("login"))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
  
   cur = mysql.connection.cursor()

   # 获取文章
   result = cur.execute("SELECT * FROM articles WHERE author = %s", [session['username']])

   articles = cur.fetchall()

   # 关闭连接
   cur.close()

   if result > 0:
       return render_template("dashboard.html", articles=articles)
   else:
       msg = "未找到文章"
       return render_template('dashboard.html', msg=msg)

# 添加文章表单类
class ArticleForm(Form):
   title = StringField('标题', [validators.Length(min=1, max=200)])
   body = TextAreaField('正文', [validators.Length(min=30)])

# 添加文章
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
   form = ArticleForm(request.form)
   if request.method == 'POST' and form.validate():
      title = form.title.data
      body = form.body.data

      cur = mysql.connection.cursor()

      # 执行
      cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

      # 提交到数据库
      mysql.connection.commit()

      #关闭连接
      cur.close()

      flash("文章已经创建", "success")

      return redirect(url_for("dashboard"))

   return render_template("add_article.html", form=form)

# 编辑
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
   # 创建游标
   cur = mysql.connection.cursor()

   # 获取文章id
   result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])

   article = cur.fetchone()

   # 获取表单
   form = ArticleForm(request.form)

   # 填充文章表单字段
   form.title.data = article['title']
   form.body.data = article['body']

   if request.method == 'POST' and form.validate():
      title = request.form['title']
      body = request.form['body']

      cur = mysql.connection.cursor()

    
      cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))

     
      mysql.connection.commit()

      
      cur.close()

      flash("Article Updated", "success")

      return redirect(url_for("dashboard"))

   return render_template("edit_article.html", form=form)

# 删除文章
@app.route("/delete_article/<string:id>", methods=['POST'])
@is_logged_in
def delete_article(id):

   cur = mysql.connection.cursor()

  
   cur.execute("DELETE FROM articles WHERE id = %s", [id])

   mysql.connection.commit()

   cur.close()

   flash("文章删除", "success")

   return redirect(url_for("dashboard"))

if __name__ == '__main__':
   app.secret_key='secret123'#密钥
   app.run(debug=True)