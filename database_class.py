class DataBase:

  def __init__(self, mysql, pymysql):
    self.mysql = mysql
    self.pymysql = pymysql
  
  def connect_to_db(self):
    conn = self.mysql.connect()
    cursor = conn.cursor(self.pymysql.cursors.DictCursor)
    return conn, cursor

  def run_sql_query(self, query, fetch_one, fetch_all=False, fetch_many=False, size =0, ):
    try:
      conn, cursor = self.connect_to_db()
      cursor.execute(query)
      if fetch_one == True:
        value= cursor.fetchone()
      elif fetch_all==True:
        value= cursor.fetchall()
      else:
        value= cursor.fetchmany(size)
    except Exception as e:
      print(e)
      value= None
    finally:
      cursor.close()
      conn.close()
    return value

  def save_to_db(self, query, args=[], args_in=False, get_id=False):
    try:
      conn, cursor = self.connect_to_db()
      if args_in:
        cursor.execute(query, args)
      else:
        cursor.execute(query)
      conn.commit()
      val = 'NO ISSUE'
      insert = cursor.lastrowid
    except Exception as e:
      print(e)
      val = "ISSUE"
    finally:
      cursor.close()
      conn.close()

    if get_id:
      return val, insert

    return val


class Email(DataBase):

  def __init__(self, mysql, pymsql):
    super().__init__(mysql, pymsql)

  def add_email(self, email):
    return self.save_to_db("insert into email (email) values ('{}')".format(email))

  def return_emails(self):
    emails =  []
    
    email = self.run_sql_query("select * from email", False, True)

    for e in email:
      emails.append(e['email'])

    return emails

class Projects(DataBase):
  mysql = None
  pymysql = None

  def __init__(self):
    super().__init__(Projects.mysql, Projects.pymysql)
    
  def get_all_projects(self):
    return self.run_sql_query("select * from projects", False, fetch_all=True)[::-1]

  def add_new_project(self, **kwargs):
    try:
      res = self.save_to_db("insert into projects (title, image, description, blog_link) values ('{}', '{}', '{}', '{}')".format(kwargs['title'], kwargs['image'], kwargs['description'], kwargs['blog_link']))
      if res != 'NO ISSUE':
        return "Problem saving project"
      return "Saved project successfully"
    except Exception as e:
      print(e)
      return "Problem saving project"

class Blogs(DataBase):
  mysql = None
  pymysql = None

  def __init__(self):
    super().__init__(Blogs.mysql, Blogs.pymysql)

  def get_all_blogs(self):
    return self.run_sql_query("select * from blogs", False, fetch_all=True)[::-1]

class Blog(DataBase):
  mysql = None
  pymysql = None

  def __init__(self):
    super().__init__(Blog.mysql, Blog.pymysql)

  def add_blog(self, html, css, js, title, image, description):
    try:
      query = "insert into blog (`html`, `css`, `js`) values (%s,%s,%s)"
      res, last_id = self.save_to_db(query, [html, css, js], True, True)

      if res != 'NO ISSUE':
        return "Problem saving Blog"
      
      query = "insert into blogs (title, image, description, blog_link) values ('{}', '{}', '{}', {})".format(title, image, description, last_id)

      res =  self.save_to_db(query)

      if res != 'NO ISSUE':
        return "Problem saving Blog"

      return "Saved Blog successfully"
    except Exception as e:
      print(e)
      return "Problem saving Blog"

  def get_blog(self, id):
    data= self.run_sql_query("select * from blog where id={}".format(id), True)
    name =  self.run_sql_query("select title, description from blogs where blog_link={}".format(id), True)
    return data,name

  def get_ids(self):
    ids = []
    ist = self.run_sql_query("select * from blog", False, True)
    for id in ist:
      ids.append(id['id'])
    return ids
    
class Domain(DataBase):
  mysql = None
  pymysql = None

  def __init__(self):
    super().__init__(Domain.mysql, Domain.pymysql)
  
  def get_domains(self):
    dom = self.run_sql_query("select * from domain", False, True)

    domains = []
    for d in dom:
      domains.append(d['domain'])
    
    return domains

  def does_exist(self, domain):
    res = self.run_sql_query("select * from domain where domain='{}'".format(domain), True)

    if res != None:
      return True
    return False

  def add_domain(self, domain):
    self.save_to_db("insert into domain (domain) values ('{}')".format(domain))
    return "Success"