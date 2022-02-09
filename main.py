import os
os.system("python -m pip install flask-mysql && clear")
from flask import Flask, render_template, request, redirect, session,jsonify 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
import sqlite3
from flaskext.mysql import MySQL
import pymysql
from datetime import date
from database_class import Projects, Blogs, Blog, Email, Domain
app = Flask(__name__)
app.secret_key = 'ChidozieNnajiMySQLAdminDbhost2005@gmail.com#codewithcn.com'

mysql = MySQL()
mysql.init_app(app)

Projects.mysql = mysql
Projects.pymysql = pymysql
Blogs.mysql = mysql
Blogs.pymysql = pymysql
Blog.mysql = mysql
Blog.pymysql = pymysql
Domain.mysql = mysql
Domain.pymysql = pymysql

"""Setting app config"""
app.config['MYSQL_DATABASE_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_DATABASE_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = os.environ['MYSQL_DB']
"""Done setting app config"""

def split_list_in_two(list, amount):
  n = 0
  new = []
  for i in range(len(list)):
    if len(list[n : n+amount]) != 0:
      new.append(list[n: n+amount])
      n+=amount
  return new

def check_type(stuff, types):
    if  type(stuff) == type(types):
        return True
    return False

app.jinja_env.filters['check_type'] = check_type

def check_len(obj):
    return len(obj)

app.jinja_env.filters['check_len'] = check_len

def send_email(subject, message, email, emailer, emailer_pass):
        port = 587  # For starttls
        smtp_server = "smtp.mail.me.com"
        sender_email = emailer
        receiver_email = email
        password = emailer_pass
        messages = MIMEMultipart()
        messages['From'] = sender_email
        messages['To'] = receiver_email
        messages['Subject'] = subject
        messages['Bcc'] = receiver_email
        messages.attach(MIMEText(message, 'plain'))
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, messages.as_string())


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    msg=''
    if request.method == "POST":
        first_name = request.form['First-Name']
        last_name = request.form['Last-Name']
        emails = request.form['Email']
        num = request.form['Contact-Phone-Number']
        message=request.form['Message']
        statement = first_name+' '+last_name +' wants to contact you' +' their email: '+ emails +' their number: '+ num +' their message: '+ message
        send_email('Contact from your website', statement, 'codingwithcn@gmail.com','nnajisgai@icloud.com', os.environ['EmailPassword'])
        msg = "Message recieved will try to get to you soon"
    return render_template('contact.html', msg=msg)


@app.route('/add_email', methods=['POST'])
def add_email():
  data = request.get_json()
  rs = Email(mysql, pymysql).add_email(data["email"])
  if rs == "ISSUE":
    return jsonify({"returns": "Problem Saving Email"})
  send_email("New Person added to blog newsletter", "The following email '{}' just became part of our blog newsletter".format(data['email']), 'codingwithcn@gmail.com','nnajisgai@icloud.com', os.environ['EmailPassword'])
  return jsonify({"returns": "Email Successfully Saved"})
  


@app.route('/add/domains', methods=['POST'])
def add_domains():
  data = request.get_json()
  return jsonify({'return': Domain().add_domain(data['domain'])})

@app.route("/projects", methods=['GET'])
def projects():
  projects = split_list_in_two(Projects().get_all_projects(), 3)
  return render_template('projects.html', projects=projects)

@app.route('/blog', methods=['GET'])
def view_blogs():
  projects = split_list_in_two(Blogs().get_all_blogs(), 3)
  return render_template('blog_view.html', projects=projects)


@app.route('/view/blog/<int:blog>', methods=['GET'])
def view_blog(blog):
  data, name = Blog().get_blog(blog)
  if data != None:
    body =  data['html'] + data['css']+ data['js']
    return render_template('blog.html', bodies = body, blog=name)
  else:
    return "Blog does not exist"

@app.route('/domain/<string:dom>/dom', methods=['GET', 'POST'])
def view_dom(dom):
  if Domain().does_exist(dom):
    msg=''
    if request.method == 'POST':
      first_name = request.form['First-Name']
      last_name = request.form['Last-Name']
      emails = request.form['Email']
      num = request.form['Contact-Phone-Number']
      message=request.form['Message']
      statement = first_name+' '+last_name +' wants to contact you about ' + dom+ ' domain. their email: '+ emails +' their number: '+ num +' their message: '+ message
      send_email('Contact from your website', statement, emails,'nnajisgai@icloud.com', os.environ['EmailPassword'])
      msg = "Message recieved will try to get to you soon"
    return render_template('view_dom.html', dom=dom, msg=msg)
  return "Domain does not exist"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        name = request.form["First-Name"]
        password = request.form["Last-Name"]
        email = request.form["Email"]
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        query = """select id from users where name='{}' and password='{}' and email='{}' """.format(
            name, password, email
        )
        print(query)
        cursor.execute(query)
        ids = cursor.fetchone()
        print(ids)
        if ids != None:
            session['id'] = ids[0]
            session['name'] = name
            session['email'] = email
            session['password'] = password
            return redirect('/admin')
        msg='Incorrect credentials'

    return render_template('admin_login.html', msg=msg)

@app.route('/admin', methods=['GET'])
def admin():
  try:
    if session['id']:
        return render_template('home.html')
    return redirect('/admin/login')
  except Exception as e:
    print(e)
    return redirect('/admin/login')

@app.route('/signout', methods=['GET'])
def signout():
  try:
    if session['id']:
        session.pop('id', None)
        session.pop('name', None)
        session.pop('email', None)
        session.pop('password', None)
  except Exception as e:
    print(e)
    return redirect('/admin/login')

@app.route('/add/project', methods=['GET'])
def add_project():
  try:
    if session['id']:
        return render_template('add_project.html', ids=session['id'])
  except Exception as e:
    print(e)
    return redirect('/admin/login')

@app.route('/add_new_project', methods=['POST'])
def add_new_project():
  data = request.get_json()
  return jsonify({"returns": Projects().add_new_project(**data)})

@app.route('/add_new_blog', methods=['POST'])
def add_new_view():
  data = request.get_json()
  res = Blog().add_blog(data['html'], data['css'], data['js'], data['title'], data['image'], data['description'])
  return jsonify({"returns": res})


@app.route('/add/blogs', methods=['GET'])
def add_blogs():
  try:
    if session['id']:
        return render_template('add_blogs.html', ids=session['id'])
  except Exception as e:
    print(e)
    return redirect('/admin/login')

@app.route('/sendmail', methods=['POST'])
def sendmail():
  data = request.get_json()
  emailse = Email(mysql, pymysql).return_emails()

  for emails in emailse:
    statement = "Come check out my new blog post Link: 'https://codingwithcn.herokuapp.com/view/blog/"+data['content']+"'" 
    send_email('CodingWithCN New Blog Post', statement, emails,'nnajisgai@icloud.com', os.environ['EmailPassword'])
  return jsonify({'return': "Success"})
  

@app.route('/domains', methods=['GET'])
def get_domains():
  return render_template('domains.html', domains=Domain().get_domains())

@app.route('/sitemap.xml')
def site_map():
  return render_template('sitemap_template.xml', articles=Blog().get_ids(), doms=Domain().get_domains(), base_url="http://www.codingwithcn.me", second_base_url='https://codingwithcn.herokuapp.com', dates=date.today())


if __name__ == '__main__':
  # Threaded option to enable multiple instances for multiple user access support
  app.run(threaded=True, host='0.0.0.0', port=5000, debug=False)