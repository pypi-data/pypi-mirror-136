#coding: utf-8
import json,pymysql,random,time,sqlite3,sys,re,os,pip,psycopg2,datetime,cx_Oracle,shutil,sanitizy


# if you can't install "pyodbc" on linux, try: https://stackoverflow.com/questions/2960339/unable-to-install-pyodbc-on-linux

try:
 import pyodbc
except:
 pyodbc=None


from flask import request,Flask,redirect,send_file

__version__="1.2.0"

flask_man_version="flask_man/Python {}".format(__version__)



def create_dir_file(path,exist_ok=True):
 if not os.path.exists(path):
  os.makedirs(path)

def bind_path(*args):
 seperate='\\' if (sys.platform.lower() == "win32") or( sys.platform.lower() == "win64") else '/'
 return seperate.join(args)

def write_configs(d):
 with open('config.json', 'w') as f:
     json.dump(d, f, indent=4)
 f.close()


def write_json(fi,d):
 with open(fi, 'w') as f:
     json.dump(d, f, indent=4)
 f.close()

def read_file(fl):
 with open(fl,'r') as f:
    content = f.read()
    f.close()
 return content

def delete_file(w):
 if os.path.exists(w):
  os.remove(w)

def add_to_file(fi,s):
 f = open(fi,'a+')
 f.write(s)
 f.close()

def install():
 configs=read_configs()
 r=configs["app"].get("requirements",[])
 con=configs[configs["database"].get("database_type",'sqlite')].get("database_connector",'sqlite3')
 if con!="sqlite3":
  if sys.version_info<(3,0) and con=='cx_Oracle':
   con="cx_Oracle==7.3"
  r.append(con)
 f = open("requirements.txt", "w")
 if  sys.version_info >(3,0)==True:
  r.append("vonage")
 for x in r:
  f.write('{}\n'.format(x))
 f.close()
 os.system(configs["app"].get("pip","pip3")+" install -r requirements.txt -U  --user")



def set_firebase_apikey(s):
 d=read_file("settings.py")
 l=[ x for x in d.split('\n')]
 c=[]
 for x in l:
  if x.startswith('firebase_apikey=')==True:
   x="firebase_apikey='{}'".format(s)
  c.append(x)
 write_file("settings.py",'\n'.join(c))
 configs=read_configs()
 configs['app']['firebase_apikey']=s
 write_configs(configs)


def set_firebase_bucket(s):
 d=read_file("settings.py")
 l=[ x for x in d.split('\n')]
 c=[]
 for x in l:
  if x.startswith('firebase_storage_bucket=')==True:
   x="firebase_storage_bucket='{}'".format(s)
  c.append(x)
 write_file("settings.py",'\n'.join(c))
 configs=read_configs()
 configs['app']['firebase_bucket']=s
 write_configs(configs)


def go_pro():
 d=read_file("settings.py")
 l=[ x for x in d.split('\n')]
 c=[]
 for x in l:
  if x.startswith('dev_mode=')==True:
   x="dev_mode=False"
  c.append(x)
 write_file("settings.py",'\n'.join(c))

def go_dev():
 d=read_file("settings.py")
 l=[ x for x in d.split('\n')]
 c=[]
 for x in l:
  if x.startswith('dev_mode=')==True:
   x="dev_mode=True"
  c.append(x)
 write_file("settings.py",'\n'.join(c))

def write_firebase_configs_(d):
 configs=read_configs()
 shutil.copyfile(d,configs['app']["firebase_creds_file"])



def add_model(x):
 x=x.capitalize()
 configs=read_configs()
 r=configs["app"].get("models",[])
 if x in r:
  return 
 s="""





class {}(flask_db.Model):
 pass
""".format(x)
 r.append(x)
 configs["app"]["models"]=r
 write_configs(configs)
 add_to_file("models.py",s)



def delete_model(x):
 configs=read_configs()
 x=x.capitalize()
 r=configs["app"].get("models",[])
 if x not in r:
  return 
 r.remove(x)
 configs["app"]["models"]=r
 write_configs(configs)
 d=read_file("models.py")
 l=d.split("class")
 s=''
 for i in l:
  if i.strip().startswith(x+"(")==False:
   if "from database import *" not in i:
    s+="\n\n\n\n\n\nclass "+i.strip()
   else:
    s+=i.strip()
 write_file("models.py",s.strip()+"\n\n")



def add_template(x):
 if x[:1]!="/":
   x="/"+x
 configs=read_configs()
 r=configs["app"].get("templates",[])
 if x in r:
  return 
 s="""





@app.route('{}',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}():
 data={{"session":General_Model(**session),"title":"{}"}}
 return render_template("{}",**data)
""".format(x,x[1:].replace('.','_').replace("/","_"),x.split("/")[-1].split('.')[0].replace("_"," ").replace("/"," ").strip(),x[1:])
 r.append(x)
 configs["app"]["templates"]=r
 write_configs(configs)
 add_to_file("templates.py",s)
 create_file("templates"+x)


def delete_template(x):
 if x[:1]!="/":
   x="/"+x
 configs=read_configs()
 r=configs["app"].get("templates",[])
 if x not in r:
  return 
 r.remove(x)
 configs["app"]["templates"]=r
 write_configs(configs)
 delete_file("templates/"+x)
 d=read_file("templates.py")
 l=d.split("@app.route('")
 s=''
 for i in l:
  if x+"'" not in i:
   if "from routes import *" not in i:
    s+="\n\n\n\n\n\n@app.route('"+i.strip()
   else:
    s+=i.strip()
 write_file("templates.py",s+"\n\n")




def add_route(x):
  configs=read_configs()
  home_page_redirect="/"
  if configs["app"].get('templates',[])!=[]:
   home_page_redirect=configs["app"]['templates'][0]
  home_page='""'
  if home_page_redirect!="/":
   home_page="render_template('"+home_page_redirect+"')"
  if x[:1]!="/":
   x="/"+x
  if x[-1]=="/":
   x=x[:-1]
  r=configs["app"].get("routes",[])
  if x in r:
   return 
  a=re.findall(r'<[^>]*>',x)
  a+=re.findall(r'{[^>]*}',x)
  params=",".join([ i.replace('{','').replace('}','').replace('<','').replace('>','').split(':')[0] for i in a])
  s=''
  x="/"+"/".join([ i for i in x.split('/') if i.strip()!=""])
  if x[:1]!="/":
   x="/"+x
  if x=="/":
   s+="""





@app.route('{}',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}({}):
 return {}
""".format("/","home_root",'',home_page)
  else:
   s+="""





@app.route('{}',methods=["GET","POST"])
@app.route('{}/',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}({}):
 status_code=200
 specific_headers={{}}
 return "",status_code,specific_headers
""".format(x.replace('.','_'),x.replace('.','_'),x[1:].replace('{','').replace('}','_').replace('/','_').replace('<','').replace('>','_').replace(':','_').replace('.',''),params)

  r.append(x)
  configs["app"]["routes"]=r
  write_configs(configs)
  add_to_file("routes.py",s)


def delete_route(x):
 if x[:1]!="/":
   x="/"+x
 if x[-1]=="/":
   x=x[:-1]
 configs=read_configs()
 r=configs["app"].get("routes",[])
 if x not in r:
  return 
 r.remove(x)
 configs["app"]["routes"]=r
 write_configs(configs)
 d=read_file("routes.py")
 l=d.split("@app.route('")
 s=''
 for i in l:
  if x+"'" not in i and x+"/'" not in i:
   if "from wrappers import *" not in i:
    s+="\n\n\n\n\n\n@app.route('"+i.strip()
   else:
    s+=i.strip()
 write_file("routes.py",s+"\n\n")





def upgrade():
 p="pip" if sys.version_info < (3,0) else "pip3"
 os.system(p+" install flask_man -U   --user")


def file_exists(path):
 return os.path.exists(path)
 

def create_file(w):
    direc,file=os.path.split(w)
    try:
        create_dir_file(direc, exist_ok=True)
    except:
        pass
    with open(w ,"a+") as f:
     pass
    f.close()

def write_file(f,s):
 create_file(f)
 f = open(f, "w")
 f.write(s)
 f.close()



def get_db_code(configs):
 db_con=configs[configs["database"].get("database_type",'sqlite')].get("connection",{})
 if type(db_con)==str:
  db_con=str(json.dumps(db_con))
 else:
  db_con=str(db_con)
 return """from utils import *


# if you can't install "pyodbc" on linux, try: https://stackoverflow.com/questions/2960339/unable-to-install-pyodbc-on-linux


# if you can't install "psycopg2" on linux, try: https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python


# if you can't install "cx_Oracle" on linux, try: https://blogs.oracle.com/linux/post/installing-cx_oracle-and-oracle-instant-client-via-oracle-linux-yum-server


#in case of "cx_Oracle" connection error: https://stackoverflow.com/questions/56119490/cx-oracle-error-dpi-1047-cannot-locate-a-64-bit-oracle-client-library



import """+configs[configs["database"].get("database_type",'sqlite')].get("database_connector",'sqlite3')+""" as database_connector


db_connector='"""+configs[configs["database"].get("database_type",'sqlite')].get("database_connector",'sqlite3')+"""'

database_credentials="""+db_con+"""




database_type='"""+configs["database"].get("database_type",'sqlite')+"""'


#https://overiq.com/flask-101/database-modelling-in-flask/


if database_type=='sqlite':
 app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database_credentials['file']
elif database_type=='mysql' or database_type=='mariadb':
 app.config['SQLALCHEMY_DATABASE_URI'] = database_type+'+'+db_connector+'://{}:{}@{}:{}/{}'.format(database_credentials['user'],database_credentials['passwd'],database_credentials['host'],database_credentials['port'],database_credentials['db'])
elif database_type=='postgresql':
 c={}
 d=database_credentials.split()
 for x in d:
  c.update({x.split('=')[0]:x.split('=')[1]})
 app.config['SQLALCHEMY_DATABASE_URI'] = database_type+'+'+db_connector+'://{}:{}@{}/{}'.format(c['user'],c['password'],c['host'],c['dbname'])
elif database_type=='mssql':
 c={}
 d=database_credentials.split(';')
 for x in d:
  c.update({x.split('=')[0]:x.split('=')[1]})
 app.config['SQLALCHEMY_DATABASE_URI'] = database_type+'+'+db_connector+'://{}:{}@{}/{}'.format(c['UID'],c['PWD'],c['SERVER'],c['DATABASE']) 
elif database_type=='oracle':
 app.config['SQLALCHEMY_DATABASE_URI'] = database_type+'+'+db_connector+'://{}:{}@{}'.format(database_credentials['user'],database_credentials['passwd'],database_credentials['dsn'])



flask_db=flask_sqlalchemy.SQLAlchemy(app)




def get_database_connection():
 if type(database_credentials)==str:
   d=database_connector.connect(database_credentials)
   if database_connector==psycopg2:
    d.set_session(autocommit=True)
   else:
    d.autocommit=True
   return d
 if database_type!="sqlite":
  if connector==pymysql:
   return connector.connect(**database_credentials)
  con=connector.connect(**database_credentials)
  con.autocommit=True
  return con
 conn= database_connector.connect(database_credentials['file'],isolation_level=database_credentials.get('isolation_level',None))
 conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
 return conn




def get_connection_cursor(c):
 if database_type=="mysql":
  return c.cursor(database_connector.cursors.DictCursor)
 if database_type=="postgres":
  return c.cursor(cursor_factory=database_connector.extras.RealDictCursor)
 return c.cursor()
 



def close_object(c):
 c.close()





def database_execute(sql,*args):
 a=[]
 if args:
  if args[0]!=None:
   a=args[0]
 c=get_database_connection()
 cur=get_connection_cursor(c)
 cur.execute(sql,a)
 close_object(cur)
 close_object(c)
 




def database_executemany(sql,*args):
 a=[]
 if args:
  if args[0]!=None:
   a=args[0]
 c=get_database_connection()
 cur=get_connection_cursor(c)
 cur.executemany(sql,a)
 close_object(cur)
 close_object(c)





def database_fetch_one(sql,*args):
 a=[]
 if args:
  if args[0]!=None:
   a=args[0]
 c=get_database_connection()
 cur=get_connection_cursor(c)
 cur.execute(sql,a)
 if database_type=="mssql":
   columns = [column[0] for column in cur.description]
   rs=cur.fetchone()
   close_object(cur)
   close_object(c)
   return  dict(zip(columns, rs))
 if database_type=="oracle":
  cur.rowfactory = lambda *args: dict(zip([d[0] for d in curs.description], args))
 r=cur.fetchone()
 close_object(cur)
 close_object(c)
 return r
 




def database_fetch_all(sql,*args):
 a=[]
 if args:
  if args[0]!=None:
   a=args[0]
 c=get_database_connection()
 cur=get_connection_cursor(c)
 cur.execute(sql,a)
 if database_type=="mssql":
   columns = [column[0] for column in cur.description]
   rs=cur.fetchall()
   close_object(cur)
   close_object(c)
   return  [dict(zip(columns, x)) for x in rs]
 if database_type=="oracle":
  cur.rowfactory = lambda *args: dict(zip([d[0] for d in curs.description], args))
 r=cur.fetchall()
 close_object(cur)
 close_object(c)
 return r
"""



def random_string(s):
 return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for x in range(s)])

def create_mysql_db(d,connector):
  if type(d)==str:
   di="%s"%d
   for x in di.split():
    if "dbname=" in x.lower():
     d.replace(x,"dbname=''")
   c=connector.connect(di)
   if connector==psycopg2:
    c.set_session(autocommit=True)
   else:
    c.autocommit=True
   cu=c.cursor()
   if connector==psycopg2:
    a=d.split()
    db=""
    for x in a:
     if "dbname=" in x.lower():
      db=x.split("=")[1]
    a=d.split(';')
   elif connector==pyodbc:
    db=""
    for x in a:
     if "database=" in x.lower() :
      db=x.split("=")[1]
   try:
    cu.execute("CREATE DATABASE IF NOT EXISTS "+db)
   except:
    pass
  else:
   di=d.copy()
   for x in ['db','database','dbname','DATABASE']:
    try:
     di.pop(x)
    except:
     pass
   c=connector.connect(**di)
   cu=c.cursor()
   cu.execute("CREATE DATABASE IF NOT EXISTS "+d["db"])
   cu.close()
   c.close()


def get_connection(c,connector):
 if type(c)==str:
   d=connector.connect(c)
   if connector==psycopg2:
    d.set_session(autocommit=True)
   else:
    d.autocommit=True
   return d
 if connector==pymysql:
  return connector.connect(**c)
 con=connector.connect(**c)
 con.autocommit=True
 return con

def get_sqlite_connection(c):
 while True:
  try:
   conn = sqlite3.connect(c["file"],isolation_level=c['isolation_level'])
   if conn!=None:
    return conn
  except:
   time.sleep(0.1)


def get_cursor(c):
 return c.cursor()

def close_object(c):
 c.close()

def write_firebase_configs(d):
 with open('config.json', 'w') as f:
     json.dump(d, f, indent=4)
 f.close()

def read_configs():
 f = open('config.json')
 d = json.load(f)
 f.close()
 return d

def create_app_script(configs):
 home_page_redirect="/"
 if configs["app"].get('templates',[])!=[]:
  home_page_redirect=configs["app"]['templates'][0]
 home_page='""'
 if home_page_redirect!="/":
  home_page="render_template('"+home_page_redirect+"')"
 r=configs["app"].get("requirements",[])
 con=configs[configs["database"].get("database_type",'sqlite')].get("database_connector",'sqlite3')
 if con!="sqlite3":
  r.append(con)
 f = open("requirements.txt", "w")
 for x in r:
  f.write('{}\n'.format(x))
 f.close()
 r=list(dict.fromkeys(configs["app"].get('templates',[])))
 if r==[]:
  r=["/"]
 s1="""from routes import *

"""
 for x in r:
  if x[:1]!="/":
   x="/"+x
  s1+="""

@app.route('{}',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}():
 status_code=200
 specific_headers={{}}
 data={{"session":General_Model(**session),"title":"{}"}}
 return render_template("{}",**data),status_code,specific_headers

""".format(x,x[1:].replace('.','_').replace("/","_"),x.split("/")[-1].split('.')[0].replace("_"," ").replace("/"," ").strip(),x[1:])
 r=list(dict.fromkeys(configs["app"].get("routes",[])))
 if r==[]:
  r=["/"]
 s2="""from wrappers import *
"""
 for x in r:
  a=re.findall(r'<[^>]*>',x)
  a+=re.findall(r'{[^>]*}',x)
  params=",".join([ i.replace('{','').replace('}','').replace('<','').replace('>','').split(':')[0] for i in a])
  su=""
  x="/"+"/".join([ i for i in x.split('/') if i.strip()!=""])
  if x[:1]!="/":
   x="/"+x
  if x=="/":
   s2+="""

@app.route('{}',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}({}):
 status_code=200
 specific_headers={{}}
 return {},status_code,specific_headers

""".format("/","home_root",'',home_page)
  else:
   s2+="""

@app.route('{}',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def {}({}):
 status_code=200
 specific_headers={{}}
 return {},status_code,specific_headers

""".format(x.replace('.','_'),su,x[1:].replace('{','').replace('}','_').replace('/','_').replace('<','').replace('>','_').replace(':','_').replace('.',''),params)
 script1="""import flask,flask_admin,flask_sqlalchemy
from flask import Flask, request,send_file,Response,redirect,session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage,ImmutableMultiDict

import requests as requests_local
import flask_recaptcha 

import flask_limiter
from flask_limiter.util import get_remote_address


try:
 import vonage
except:
 vonage=None

from flask_debugtoolbar import DebugToolbarExtension

import flask_mail

import json,os,random,sys,datetime,ssl,mimetypes,time,logging

from logging.handlers import RotatingFileHandler


from firebase_admin import auth
from firebase_admin.auth import UserRecord

import firebase_admin

import sanitizy

sqlite3=None
pyodbc=None
pymysql=None
psycopg2=None


import hashlib,functools 

from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer,SecureCookieSessionInterface



from google.cloud import storage
"""

 wrappers="""from handlings import *




def user_only(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if validate_is_user(session)==True:
   return f(*args, **kwargs)
  else:
   return redirect(user_login_endpoint)
 return validate




def logged_in_user_redirect(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if validate_is_user(session)==False:
   return f(*args, **kwargs)
  else:
   return redirect(user_home_endpoint)
 return validate




def admin_only(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if validate_is_admin(session)==True:
   return f(*args, **kwargs)
  else:
   return redirect(admin_login_endpoint)
 return validate



def logged_in_admin_redirect(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if validate_is_user(session)==False:
   return f(*args, **kwargs)
  else:
   return redirect(admin_home_endpoint)
 return validate



def do_logout(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
   is_logged_out(session)
   return redirect(home_page_endpoint)
 return validate





def user_logout(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
   is_logged_out(session)
   return redirect(user_login_endpoint)
 return validate



def admin_logout(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
   is_logged_out(session)
   return redirect(admin_login_endpoint)
 return validate





def valid_authorization(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  token=request.headers.get(authorization_header,'')
  if len(token)==0:
   return "Invalid Token",401
  try:
   d=decode_flask_token(token)
   set_session_variables(session,d)
  except:
   return "Invalid Token",401
  return f(*args, **kwargs)
 return validate



def safe_uri(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  for x in kwargs:
   kwargs[x]=sanitizy.SQLI.escape(kwargs[x])
  return f(*args, **kwargs)
 return validate



def safe_args(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  request.args=sanitizy.SQLI.escape_args(request)
  return f(*args, **kwargs)
 return validate




def safe_form(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  request.form=sanitizy.SQLI.escape_form(request)
  return f(*args, **kwargs)
 return validate





def safe_request(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  request.form=sanitizy.SQLI.escape_form(request)
  request.args=sanitizy.SQLI.escape_args(request)
  return f(*args, **kwargs)
 return validate




def safe_files(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if sanitizy.FILE_UPLOAD.validate_form(request)==True:
   return f(*args, **kwargs)
  else:
   return "Unacceptable Files",401
 return validate





# for recaptcha's HTML code : https://developers.google.com/recaptcha/docs/display

# https://www.google.com/recaptcha/

# <script src="https://www.google.com/recaptcha/api.js" async defer></script>


def valid_recaptcha(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if recaptcha_app.verify():
   remove_recaptcha_response(request)
   return f(*args, **kwargs)
  else:
   remove_recaptcha_response(request)
   return "Invalid recaptcha",401
 return validate




def valid_referer(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if csrf_referer_checker(request,allowed_domains=accepted_referer_domains)==True:
   return f(*args, **kwargs)
  else:
   return "Invalid request source",401
 return validate





def valid_origin(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  validate_origin_header
  if validate_origin_header(request,allowed_domains=accepted_origin_domains)==True:
   return f(*args, **kwargs)
  else:
   return "Invalid request source",401
 return validate





def valid_csrf_token(f):
 @functools.wraps(f)
 def validate(*args, **kwargs):
  if csrf_token_checker(request,session)==True:
   return f(*args, **kwargs)
  else:
   return "Invalid CSRF Token",401
 return validate





def render_template(t,**kwargs):
 try:
  return flask.render_template(t,**kwargs)
 except Exception as e:
  print(e)
  return 'Template not found'
"""
 script2="""from imports import *


#Don't touch what's below unless you know what you are doing :)





#https://thepoints.medium.com/upload-data-to-firebase-cloud-firestore-with-10-line-of-python-code-1877690a55c6


firebase_creds_file='"""+configs['app'].get("firebase_creds_file",'firebase_creds.json')+"""'


firebase_apikey='"""+str(configs['app'].get("firebase_apikey",None))+"""'


firebase_storage_bucket='"""+configs['app'].get("firebase_bucket",None)+"""'


firebase_creds=None


if firebase_storage_bucket!=None and firebase_storage_bucket.strip()!='':
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=firebase_creds_file
  firebase_admin_app = firebase_admin.initialize_app()



authorization_header='Authorization'




CORS_SUPPORT=True

CORS_URIs=("/api/","/restapi/")

CORS_HEADERS={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers': 'Content-Type,'+authorization_header,'Access-Control-Allow-Methods': 'HEAD, GET, POST, OPTIONS'}




flask_default_salt = 'cookie-session'


app = Flask(__name__)





endpoints_limiter=flask_limiter.Limiter(app, key_func=get_remote_address, default_limits=[])


server_signature='"""+flask_man_version+"""'


accepted_referer_domains="""+str(configs["app"]["accepted_referer_domains"])+"""

accepted_origin_domains="""+str(configs["app"]["accepted_origin_domains"])+"""

#global important variables


allowed_file_extensions="""+str(configs["app"]["allowed_file_extensions"])+"""


allowed_mimetypes_="""+str(configs["app"]["allowed_mimetypes"])+"""



permanent_session=True



vonage_creds="""+str(configs["app"]["vonage_creds"])+"""



additional_headers={'X-Frame-Options':'SAMEORIGIN','X-Content-Type-Options': 'nosniff','Referrer-Policy': 'same-origin','Server':server_signature,'X-Permitted-Cross-Domain-Policies': 'none','Permissions-Policy': "geolocation 'none'; camera 'none'; speaker 'none';"}
'''

whitelist_external_sources=False


js_domains=['ajax.googleapis.com','www.google-analytics.com','cdn.jsdelivr.net','unpkg.com','cdnjs.cloudflare.com']


script_src="script-src 'self' "



if len(js_domains)>0:
 script_src+=' '.join(js_domains)


style_domains=['cdn.jsdelivr.net']



style_src="style-src 'self' "


if len(js_domains)>0:
 style_src+=' '.join(style_domains)



font_domains=[]


font_src="font-src 'self' "

if len(font_domains)>0:
 font_src+=' '.join(font_domains)



img_domains=[]


img_src="font-src 'self' "

if len(img_domains)>0:
 img_src+=' '.join(img_domains)


if whitelist_external_sources==True:
 additional_headers.update({'X-XSS-Protection': '0','Content-Security-Policy': " ; ".join([script_src,style_src,font_src,img_src])})

'''
unwanted_headers=[]


app_conf="""+str(configs["app"]["run"])+"""


server_conf="""+str(configs["app"]["config"])+"""


session_timeout="""+str(configs["app"]["session_timeout"])+"""


force_https=True if app_conf['ssl_context']!=None else False


hsts_enabled=True if app_conf['ssl_context']!=None else False

if hsts_enabled==True:
 additional_headers.update({'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload'})



#the folder where you store the files that are accesible to the users to download

downloads_folder="uploads"


#sensitive files that shouldn't be accessed by the user (downloaded for example)

sensitive_files="""+str(configs["app"]["sensitive_files"])+"""


app_basedir=os.getcwd()


#the templates' folder

templates_folder="templates"


#the static files' folder

statics_folder="static"


#the folder where you store the files that are were uploaded by the users

uploads_folder="uploads"


#the CSRF token's name where will be used it the: session,forms, and as POST parameter

csrf_token_name="csrf_token"





#the name of the session variable that tells if the user is logged in or not


session_login_indicator="logged_in"

admin_indicator="admin"

#the endpoint which the user will be redirected if he accessed a page which requires authentication

home_page_endpoint='"""+home_page_redirect+"""'



user_login_endpoint='login.html'

user_home_endpoint='home.html'



admin_login_endpoint='admin/login.html'

admin_home_endpoint='admin/dashboard.html'



dev_mode=True


if dev_mode==False:
 server_conf['ENV']= 'production'
 server_conf['DEBUG']= False
 server_conf['FLASK_ENV']= 'production'
else:
 server_conf['ENV']= 'development'
 server_conf['DEBUG']= True
 server_conf['FLASK_ENV']= 'development'




#configuring the app to be as specified in the "config.json" file


app.config.update(**server_conf)


recaptcha_app =flask_recaptcha.ReCaptcha(app)


if server_conf['RECAPTCHA_SECRET_KEY']!=None:
 server_conf.update({'RECAPTCHA_ENABLED': True})
else:
 server_conf.update({'RECAPTCHA_ENABLED': False})

recaptcha_app.init_app(app)


app.permanent_session_lifetime = datetime.timedelta(**session_timeout)




Flask_Mailler = flask_mail.Mail(app)


toolbar_app = DebugToolbarExtension(app)
"""
 script3="""from settings import *



#general Model class to have any arributes for any model


class General_Model:

 def __init__(self,**kwargs):
  self.__dict__.update(kwargs)





def fetch_basic_auth_credentials(obj):
 return obj.authorization["username"],obj.authorization["password"]




def remove_recaptcha_response(obj):
 d={}
 for x in obj.form:
  if x!='g-recaptcha-response':
   d.update({x:obj.form[x]})
 obj.form=ImmutableMultiDict(d)
 d={}
 for x in obj.args:
  if x!='g-recaptcha-response':
   d.update({x:obj.args[x]})
 obj.args=ImmutableMultiDict(d)
 for x in obj.files:
  if x!='g-recaptcha-response':
   d.update({x:obj.files[x]})
 obj.files=ImmutableMultiDict(d)



def delete_file(w):
 if os.path.exists(w):
  os.remove(w)



def create_file(w):
    direc,file=os.path.split(w)
    try:
        create_dir_file(direc, exist_ok=True)
    except:
        pass
    with open(w ,"a+") as f:
     pass
    f.close()

#https://gist.github.com/babldev/502364a3f7c9bafaa6db


def decode_flask_token(cookie_str,secret_key=server_conf["SECRET_KEY"]):
    serializer = TaggedJSONSerializer()
    signer_kwargs = {
        'key_derivation': 'hmac',
        'digest_method': hashlib.sha1
    }
    s = URLSafeTimedSerializer(secret_key, salt=flask_default_salt, serializer=serializer, signer_kwargs=signer_kwargs)
    return s.loads(cookie_str)




# https://stackoverflow.com/questions/42283778/generating-signed-session-cookie-value-used-in-flask

def generate_flask_token(cookie,app=app):
    return SecureCookieSessionInterface().get_signing_serializer(app).dumps(dict(cookie))



def read_file(fl):
 with open(fl,'rb') as f:
    content = f.read()
    f.close()
 return content





def get_real_uri(r):
 return "/"+"/".join([ x for x in r.path.split('/') if x.strip()!=""])




def validate_origin_header(obj,allowed_domains=[]):
        domains=[obj.host] if (not allowed_domains or len(allowed_domains)==0) else allowed_domains
        referer=obj.headers.get('Origin','')
        if referer.strip()=="" or referer.strip().lower()=="null":
            return False
        a=referer.split("://")[1].split("/")[0]
        if a not in domains:
            return False
        return True




#function to generate random string

def random_string(s):
 return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for x in range(s)])




def file_exists(path):
 return os.path.exists(path)




def unescape_sqli(s):
 return sanitizy.SQLI.unescape(s)




def set_headers(h,d):
 for x in d:
  h[x] = d[x]




def unset_headers(h,d):
 for x in d:
  h[x]=''




def set_cookie(r,k,v,attributes):
 r.set_cookie(k, v , **attributes)




def set_session_variables(s,d):
 for x in d:
  s[x] = d[x]
 s.modified = True
 s.permanent = permanent_session




def reset_session(s):
 s.clear()
 s.modified = True
 s.permanent = permanent_session
 




#security checks


def csrf_token_checker(r,s):
 return r.form.get(csrf_token_name,"")==s.get(csrf_token_name,"")



'''

after validating the user's login, this function must be called before redirecting to the logged in page to start the user's session correctly.
example:

@app.route('/login',methods=["POST"])
def login():
 if request.form.get('pass')=='joe':
   is_logged_in(session,admin=False,variables={"username":"joe"})
   return redirect('profile.html')
 return redirect('login.html')

'''




def is_logged_in(s,admin=False,variables={}):
 csrf=random_string(64)
 s[csrf_token_name]=csrf
 s[session_login_indicator]=True
 variables.update({admin_indicator:admin})
 set_session_variables(s,variables)
 s.modified = True
 s.permanent = permanent_session





'''

when logging out, this function must be called before redirecting to the login page to reset the session.
example:

@app.route('/logout',methods=["POST"])
def logout():
 is_logged_out(session)
 return redirect('login.html')

'''



def is_logged_out(s):
 s[csrf_token_name]=""
 s[session_login_indicator]=False
 reset_session(s)
 s.modified = True
 s.permanent = permanent_session





def validate_is_user(s):
 return s.get(session_login_indicator,False) and s.get(admin_indicator,False)==False



def validate_is_admin(s):
 return s.get(session_login_indicator,False) and s.get(admin_indicator,False)




def secure_filename(f):
 return sanitizy.FILE_UPLOAD.secure_filename(f)





def csrf_referer_checker(req,allowed_domains=[]):
 return sanitizy.CSRF.validate_flask(req,allowed_domains=allowed_domains)






def no_xss(s):
 return sanitizy.XSS.escape(s)

 


def no_sqli(s):
 return sanitizy.SQLI.escape(s)




def valid_uploaded_file(f,allowed_extensions=['png','jpg','jpeg','gif','pdf'],allowed_mimetypes=["application/pdf","application/x-pdf","image/png","image/jpg","image/jpeg"]):
 return sanitizy.FILE_UPLOAD.check_file(f,allowed_extensions=allowed_extensions,allowed_mimetypes=allowed_mimetypes)




#automatically save any file to the uploads folder


def bind_path(*args):
 seperate='\\\\' if (sys.platform.lower() == "win32") or( sys.platform.lower() == "win64") else '/'
 return seperate.join(args)



def save_file(f,path=uploads_folder):
 create_dir_file(path, exist_ok=True)
 return sanitizy.FILE_UPLOAD.save_file(f,path=path)




def delete_file_firebase(file_name):
 storage_client = storage.Client()
 bucket = storage_client.bucket(firebase_storage_bucket)
 bucket.delete_blob(file_name)





def upload_to_firebase(f):
 storage_client = storage.Client()
 bucket = storage_client.bucket(firebase_storage_bucket)
 blob = bucket.blob(f.filename) 
 blob.upload_from_string(f.read())
 return blob.public_url




def upload_all_to_firebase(f):
 return [upload_to_firebase(f[x]) for x in f]





#https://firebase.google.com/docs/auth/admin/manage-users?hl=en#python_6



def firebase_create_user(**kwargs):
 return auth.create_user(**kwargs).__dict__
 


def firebase_fetch_user_by_id(uid):
 return auth.get_user(uid).__dict__



def firebase_fetch_user_by_email(email):
 return auth.get_user_by_email(email).__dict__



def firebase_fetch_user_by_phone(phone):
 return auth.get_user_by_phone_number(phone).__dict__



def firebase_list_users():
 return auth.list_users().__dict__




def firebase_update_user(user_id, **kwargs):
    return auth.update_user(user_id, **kwargs).__dict__





def firebase_delete_user(uid):
 return auth.delete_user(uid)



def firebase_delete_users(*args):
 return auth.delete_users(args)


#https://blog.icodes.tech/posts/python-firebase-authentication.html



def firebase_signup(**kwargs):
 kwargs.update({'returnSecureToken': True})
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(firebase_apikey),data=kwargs)
  return json.loads(r.text)
 except:
  return {}


def firebase_signin(email,password):
 details={'email':email,'password':password,'returnSecureToken': True}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(firebase_apikey),data=details)
  return json.loads(r.text)
 except:
  return {}


def firebase_verify_email(idToken):
 data={"requestType":"VERIFY_EMAIL","idToken":idToken}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={}'.format(firebase_apikey), data=data)
  return json.loads(r.text)
 except:
  return {}



def firebase_reset_password(email):
 data={"requestType":"PASSWORD_RESET","email":email}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={}'.format(firebase_apikey), data=data)
  return json.loads(r.text)
 except:
  return {}




def firebase_anonymous_signin():
 data={"returnSecureToken":"true"}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(firebase_apikey), data=data)
  return json.loads(r.text)
 except:
  return {}

  
  
def firebase_user_data(idToken):
 details={'idToken':idToken}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={}'.format(firebase_apikey), data=details)
  return json.loads(r.text)
 except:
  return {}



def firebase_delete_account(idToken):
 data={"idToken":idToken}
 try:
  r=requests_local.post('https://identitytoolkit.googleapis.com/v1/accounts:delete?key={}'.format(firebase_apikey), data=data)
  return json.loads(r.text)
 except:
  return {}




def no_lfi(path):
 return sanitizy.PATH_TRAVERSAL.check(path)





def no_ssrf(p):
 return sanitizy.SSRF.validate(p)




def is_safe_path( path,root_dir=downloads_folder):
  return os.path.realpath(path).startswith(app_basedir+'\\\\'+root_dir if ((sys.platform.lower() == "win32") or( sys.platform.lower() == "win64")) else app_basedir+'/'+root_dir)





def list_contains(l,s):
 return any(x.startswith(s) for x in l)






def send_mail(subject='',sender=app.config['MAIL_USERNAME'],recipients=[],body='',html='',local_attachements=[],user_files=None):
   attachements=[]
   if local_attachements!=None:
    attachements+=local_attachements
   if recipients==None or len(recipients)==0:
    raise Exception("You need to set a least 1 recipient !!")
   if type(recipients)==str:
    recipients=[recipients]
   msg = flask_mail.Message(subject, sender = sender, recipients = recipients)
   msg.body=body
   msg.html = html
   for x in  attachements:
    msg.attach(os.path.split(x)[1],mimetypes.guess_type(x)[0],read_file(x))
   if user_files!=None:
    for x in  user_files:
     msg.attach(user_files[x].filename,user_files[x].content_type,user_files[x].read())    
   Flask_Mailler.send(msg)



#https://dashboard.nexmo.com/getting-started/sms


def get_vonage_client():
 return vonage.Client(key=vonage_creds["api_key"], secret=vonage_creds["api_secret"])




def send_sms(sender,to,text):
  client=get_vonage_client()
  sms = vonage.Sms(client)
  return sms.send_message({"from": sender,"to": to.replace('+','').replace('-','').replace(' ',''),"text": text})



def read_configs():
 f = open('config.json')
 d = json.load(f)
 f.close()
 return d




def write_configs(d):
 with open('config.json', 'w') as f:
     json.dump(d, f, indent=4)
 f.close()







def download_this(path,root_dir=downloads_folder):
 if is_safe_path(path,root_dir=root_dir)==True:
  if os.path.exists(path):
   return send_file(path, as_attachment=True)
 return "Not Found",404
"""
 db_s=get_db_code(configs)
 script4="""from models import *





#make sure everything is alright before doing anything


@app.url_value_preprocessor
def sql_escape_url(endpoint, values):
 pass




@app.before_request
def before_request():
 if force_https==True:
  if request.url.split('://')[0]=='http':
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
 else:
  if request.url.split('://')[0]=='https':
        url = request.url.replace('https://', 'http://', 1)
        code = 301
        return redirect(url, code=code)




@app.after_request
def add_header(response):
    if request.method=="OPTIONS":
     set_headers(response.headers,{'Access-Control-Allow-Headers': 'Content-Type,'+authorization_header,'Access-Control-Allow-Methods': 'HEAD, GET, POST, OPTIONS'})
    if CORS_SUPPORT==True and request.path.startswith(tuple(CORS_URIs))==True:
     set_headers(response.headers,CORS_HEADERS)
    set_headers(response.headers,additional_headers)
    unset_headers(response.headers,unwanted_headers)
    try:
     dt=time.strftime('%Y-%b-%d')
     timestamp = time.strftime('[%Y-%b-%d %H:%M:%S]')
     #create_file('logs/'+dt+'.log')
     handler = RotatingFileHandler('logs/'+dt+'.log', maxBytes=100000, backupCount=3)
     logger = logging.getLogger('tdm')
     logger.setLevel(logging.ERROR)
     logger.addHandler(handler)
     logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)    
    except:
     pass
    return response
    



@app.errorhandler(429)
def ratelimit_handler(e):
  return "No more requests for you :)",429


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404


def return_json_response(data):
 response = app.response_class(
        response=json.dumps(data,default=str),
        status=200,
        mimetype='application/json'
    )
 return response




#setup : sitemap.xml



@app.route('/sitemap.xml',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def sitemapxml():
 a='''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->


<url>
</url>

</urlset>'''
 response = flask.make_response(a, 200)
 response.mimetype = "text/xml"
 return response







#setup : robots.txt


@app.route('/robots.txt',methods=["GET","POST"])
@endpoints_limiter.limit("3600/hour")
def robotstxt():
 a= '''User-Agent: *
Allow: /'''
 response = flask.make_response(a, 200)
 response.mimetype = "text/plain"
 return response







#automatically server any static file in the static folder

@app.route('/static/<static_file>', methods = ['GET'])
def static1__(static_file):
 path="{}/{}".format(statics_folder,static_file)
 if path.lower().endswith(tuple(sensitive_files)):
   return "Not Found",404
 if is_safe_path(path,root_dir=statics_folder)==True:
  if os.path.exists(path):
   return send_file(path)
 return "Not Found",404



@app.route('/static/<file_type>/<static_file>', methods = ['GET'])
def static2__(file_type,static_file):
 path="{}/{}/{}".format(statics_folder,file_type,static_file)
 if path.lower().endswith(tuple(sensitive_files)):
   return "Not Found",404
 if is_safe_path(path,root_dir=statics_folder)==True:
  if os.path.exists(path):
   return send_file(path)
 return "Not Found",404




#automatically download any file in the downloads folder

@app.route('/'+downloads_folder+'/<file>', methods = ['GET'])
def downloads(file):
 path="{}/{}".format(downloads_folder,file)
 if path.lower().endswith(tuple(sensitive_files)):
   return "Not Found",404
 return download_this(path)
"""
 write_file("database.py",db_s)
 write_file("wrappers.py",wrappers)
 write_file("imports.py",script1)
 write_file("settings.py",script2)
 write_file("utils.py",script3)
 if file_exists(configs['app'].get("firebase_creds_file","firebase_creds.json"))==False:
  write_json(configs['app'].get("firebase_creds_file","firebase_creds.json"),{
  "type": "service_account",
  "project_id": "flask-plus",
  "private_key_id": "646d5064c79d386b7ad42cd2ccd1725c8d7397ea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCcbG4N5fJaIOm7\nwg4yp4Ct61XvwV0QtMNf4aZqVF6OAKQpcMIGTnibo2iS6BY5k6fAf8h8X75a5EpY\nQ25F3hmZs2r+alq8t9/Ode2artTKA/fOJPc6UInU7kmh5GmzmSnylE/RbEFkS+4n\ncFjVvUW/YWOjsMeOeC2jj3cDvZM0GqcWYfO8TLs0n9KgSJXTEON8hnoJ10pupgoI\n2NkxuyQ5cmyYn32RFlXNap/r3kaNqCcwxEQVfN9ba8JT6K8r25YUrTZSXcLN/1MN\nhrzmFXrBfypkvxGhwa9p4FIIeqcudf3hoJbc4h+OlnlrZV/TSeQvL6rzaQhtkHk9\nGQbdu5O7AgMBAAECggEAKnm3GMcMHDU7wuRa/p5FbvSsjUIwh0zOkMaxbcYjNuQt\nr6MSzKuaTIj+6IVlI5VYxAju4/cLtZqwJW+KDibVRMtXjmZK5Vv4xhN3xb0bww94\nxt161Lbx9oQOMovXuBErNtfXJMMErrt/m+4B8WhH/EPxzo0+Yw13NybJ5pYf1tHJ\nODG/JilwuKy3QDJGV1Gjn8uoB6LQ4/85aN0IFDMSRaFSExHI6M4qeZw1dHdSuwzg\n/MmwadV9vgJoqgcsP3FXwVL05KlM5Ml7i0wmjdZ7wgppp6uYxumt8w8jhNm/PKem\nLDgG7Kprn63lSyFX46ssKxJxh14xEGbor2nmnONUIQKBgQDO6ES1IBh0ixDBpf/w\nxvQ0v0cLJa2Ag8Ingop7sTYIQ6TQhnGHL11Rl2PBu6/LbqJ4PGQldcBjTx6y9oxU\nO5gdOKtNI6y52BfO80Bzj6dZwmmDqbMcasWMxNxHbe6HS5L3AXdhgEMBwT3pq/2B\nd944TxHnDPgDRa6ITdZ7ZTvYBwKBgQDBibwCeyrMPf53gK16RXsQp0cH9ecImMcJ\nXRJWHnt23WlgoCKgjQHCNvdnIEn/Qj4wKvGCLUKA8juWLVD8phH/lQU3YtmFgcCd\nEHB+tQNAlDMd3j5qN5Uf3ztNHwvOi9fhedJGuq6IgrGBhTGfGt+A+aB9Yugfs9Ke\nnhcDv7TxrQKBgDnGackZ2TpRyrAIJluZcn94GeJm9ve30vMtZHX9mdTc7py7rd/N\nvgUWfOiP/BqWHg/s7Rn4s2wHn87hQXYT3fnq5Qp5N7X9PUiwbALYziYmP0hgjn8U\n4WzZW5kmfUCSPctzQV6cbhmDWEJzoCoSyp52lc0qteZUAtRUx9tU/UzpAoGAcC+L\n2RBWRaAl8lWXuYmvBX9BkF69NmGA9m+J4nu267b6j3UjvVcfTtoX3SJ9Ykaez8ME\nzYW4yBAh9DJ+gIUvZ6yVIn7dQiNtaF4QJ5J7uSJu4wBhw6ZGffwjXtgBOxAa6mt4\nNWGfLCg+BqsTkXu9VQDeQ/BiR4YwL5vKEXU9yN0CgYBJuBfWpA/GSrA63hfbHwuE\n7R2fwcbA3SCixKBn0kFWj20k1kIZG+qhL4sdbIhxzUO8K+iscaDYSoxirm52XFg8\n55KCEHqsV2xgmK6Mbxh/1N/0k5KJNJzAploSpdJj23nVOAuAvZxC/yA3EK8Co4Pe\nY9PQq4anhHcyzoQFXN+TcA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-8z7xd@flask-plus.iam.gserviceaccount.com",
  "client_id": "112885768186449207156",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-8z7xd%40flask-plus.iam.gserviceaccount.com"
}
)
 write_file("handlings.py",script4)
 write_file("models.py","""from database import *

#NOTE: replace "db" variable in the tutorials with "flask_db" and you won't get errors :)

""")
 write_file("templates.py",s1)
 write_file("routes.py",s2)
 write_file(configs["app"].get('name','app')+".py","""from admin_view import *

def update_configs():
 d=read_configs()
 d["app"]["additional_headers"]=additional_headers
 d["app"]["run"]=app_conf
 d["app"]["sensitive_files"]=sensitive_files
 d["app"]["allowed_file_extensions"]=allowed_file_extensions
 d["app"]["allowed_mimetypes"]=allowed_mimetypes_
 d["app"]["accepted_referer_domains"]=accepted_referer_domains
 d["app"]["accepted_origin_domains"]=accepted_origin_domains
 d["app"]["config"]=server_conf
 d[database_type]["connection"]=database_credentials
 d["app"]["vonage_creds"]=vonage_creds
 write_configs(d)


flask_db.create_all()

flask_db.init_app(app)

update_configs()


if __name__ == '__main__':
   app.run(**app_conf)
""")
 write_file('passenger_wsgi.py',"from "+configs["app"].get('name','app')+" import app as application")
 write_file('admin_view.py',"""from templates import *

#if you want an admin interface, uncomment this part and follow "flask-admin" 's tutorials 

'''

admin_app = flask_admin.Admin(app, name="Flask's admin page", template_mode='bootstrap3')

'''
""")
 write_file('runtime.txt','python-'+sys.version.split(" ")[0])
 create_dir_file("templates", exist_ok=True)
 create_dir_file("logs", exist_ok=True)
 if configs["app"].get('uploads',None)!=None:
  create_dir_file("uploads", exist_ok=True)
 create_dir_file("static", exist_ok=True)
 create_dir_file("tmp", exist_ok=True)
 create_dir_file("backup", exist_ok=True)
 create_dir_file("static/img", exist_ok=True)
 create_dir_file("static/css", exist_ok=True)
 create_dir_file("static/js", exist_ok=True)
 if configs["app"].get('templates',[])!=[]:
  for x in configs["app"].get('templates',[]):
   if file_exists("templates/"+x)==False:
    create_file("templates/"+x)
 if configs["app"].get('static',None)!=None:
  for x in configs["app"]["static"]:
   if file_exists("static/"+x)==False:
    create_file("static/"+x)
 write_file('Procfile','web: gunicorn '+configs["app"].get('name','app')+':app')




def init_configs():
 configs={
    "app":
        {
         "name":
                "app",
         "run":{
                "host":
                        "0.0.0.0",
                "port":
                        5000,
                "threaded":
                        True,
                "ssl_context":
                        None,
                "processes":
                        1
                },
         "config":{
                'ENV': 'development', 
                'DEBUG': True, 
                'TESTING': False, 
                'PROPAGATE_EXCEPTIONS': None, 
                'PRESERVE_CONTEXT_ON_EXCEPTION': None, 
                'SECRET_KEY': random_string(64), 
                'USE_X_SENDFILE': False, 
                'SERVER_NAME': None, 
                'APPLICATION_ROOT': '/', 
                'SESSION_COOKIE_NAME': 'FPSessionId', 
                'SESSION_COOKIE_DOMAIN': None, 
                'SESSION_COOKIE_PATH': None, 
                'SESSION_COOKIE_HTTPONLY': False, 
                'SESSION_COOKIE_SECURE': None, 
                'SESSION_COOKIE_SAMESITE': 'Lax', 
                'SESSION_REFRESH_EACH_REQUEST': True, 
                'MAX_CONTENT_LENGTH': None, 
                'SEND_FILE_MAX_AGE_DEFAULT': None, 
                'TRAP_BAD_REQUEST_ERRORS': None, 
                'TRAP_HTTP_EXCEPTIONS': False, 
                'EXPLAIN_TEMPLATE_LOADING': False, 
                'PREFERRED_URL_SCHEME': 'http', 
                'JSON_AS_ASCII': True, 
                'JSON_SORT_KEYS': True, 
                'JSONIFY_PRETTYPRINT_REGULAR': False, 
                'JSONIFY_MIMETYPE': 'application/json', 
                'TEMPLATES_AUTO_RELOAD': None, 
                'MAX_COOKIE_SIZE': 4093, 
                'FLASK_ENV': 'development',
                'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,
                'RECAPTCHA_SITE_KEY':None,
                'RECAPTCHA_SECRET_KEY':None,
                'MAIL_SERVER':'smtp.gmail.com',
                'MAIL_PORT':465,
                'MAIL_USERNAME':'flask.plus@gmail.com',
                'MAIL_PASSWORD':'Flaskplus99',
                'MAIL_USE_TLS':False,
                'MAIL_USE_SSL':True
                },
        "session_timeout":
                {
                    "days": 30
                },
        "sensitive_files":
                ['.pyc','.py', '.sql','.db'],
        "allowed_file_extensions":
                ['png','jpg','jpeg','gif','pdf'],
        "allowed_mimetypes":
                ["application/pdf","application/x-pdf","image/png","image/jpg","image/jpeg","image/jpeg"],
        "accepted_referer_domains":
                [],
        "accepted_origin_domains":
                [],
        "firebase_creds_file":
                "firebase_creds.json",
        "firebase_bucket":
                'flask-plus.appspot.com',
        "firebase_apikey":
                "AIzaSyD13N7xRICcaMCQdqIpfWNXItlYnN-DiqI",
        "vonage_creds":
                {
                 "api_key": '',
                 "api_secret":''
                },
        "additional_headers":
                {
                'X-Frame-Options':'SAMEORIGIN',
                'X-Content-Type-Options': 'nosniff',
                'Referrer-Policy': 'same-origin',
                'Server':flask_man_version,
                'X-Permitted-Cross-Domain-Policies': 'none',
                'Permissions-Policy': "geolocation 'none'; camera 'none'; speaker 'none';"
                },
        "routes":
            ["/"],
        "templates":
            ["index.html"],
        "static":
            [],
        "uploads":
            [],
        "models":
            [],
        "requirements":
            ["flask","sanitizy","flask-limiter","flask-admin","flask-debugtoolbar","git+https://github.com/ozgur/python-firebase","firebase-admin","google-cloud-storage","Flask-SQLAlchemy","Flask-reCaptcha","Flask-Mail","werkzeug","gunicorn","itsdangerous","Jinja2"],
        "pip":
            "pip" if sys.version_info < (3,0) else "pip3"
        },
    "sqlite":
            {
                "connection":
                        {
                        "file":
                            "flask_man_db.db",
                        "isolation_level":
                            None
                        },
                "database_connector":
                        "sqlite3"
                            
            },
	"mysql":{
                "connection":
                    {
                        "host":
                                "localhost",
                        "user":
                                "root",
                        "passwd":
                                "",
                        "port":
                                3306,
                        "db":
                                "flask_man_db",
                        "autocommit":
                                True
                    },
                "database_connector":
                        "pymysql"
			},
    "mariadb":{
                "connection":
                    {
                        "host":
                                "localhost",
                        "user":
                                "root",
                        "passwd":
                                "",
                        "port":
                                3306,
                        "db":
                                "flask_man_db",
                        "autocommit":
                                True
                    },
                "database_connector":
                        "pymysql"
			},
    "oracle":{
                "connection":
                    {
                        "dsn":
                                "localhost/flask_man_db",
                        "user":
                                "root",
                        "password":
                                ""
                    },
                "database_connector":
                        "cx_Oracle"
			},
    "postgresql":{
                "connection":
                    "host=localhost dbname=flask_man_db user=postgres password=root",
                "database_connector":
                        "psycopg2"
			},
    "mssql":{
                "connection":
                    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=flask_man_db;UID=user;PWD=user",
                "database_connector":
                        "pyodbc"
			},
    "database":
			{
				"tables_names":
						None,
                "database_type":
                        "sqlite",
                "tables":
                        {},
                "values":
                        {},
                "tables_example_sqlite":
                        {
                            "users_example":
                                {
                                    "id": 
                                        "INTEGER PRIMARY KEY AUTOINCREMENT  not null",
                                    "name":
                                        "varchar(20)",
                                    "pwd":
                                        "varchar(20)"
                                },
                            "articles_example":
                                {
                                    "id": 
                                        "INTEGER PRIMARY KEY AUTOINCREMENT  not null",
                                    "title":
                                        "varchar(20)",
                                    "content":
                                        "text"
                                }
                        },
                "values_example":
                        {
                            "users_example":
                                    {
                                        "name,pwd":
                                                [("admin","password"),("user","user")],
                                    },
                            "articles_example":
                                    {
                                        "title,content":
                                                [("test","this is a test.")]
                                    }
                            
                        }
            },
	"secret_token":
			random_string(64)
}

 write_configs(configs)

def init_app():
 create_app_script(read_configs())


def set_database(data,db):
 a=[]
 try:
  if data[db]["database_connector"].isalnum() ==True:
   create_mysql_db(data[db]["connection"],eval(data[db]["database_connector"]))
  co=get_connection(data[db]["connection"],eval(data[db]["database_connector"]))
  cu=get_cursor(co)
  t=data["database"]["tables"]
  for x in t:
   a.append({x: [ i for i in t[x]]})
   cu.execute("CREATE TABLE IF NOT EXISTS "+x+" ( "+' , '.join([ i+" "+t[x][i] for i in t[x]])+" )")
  data["database"]["tables_names"]=a
  t=data["database"]["values"]
  for x in t:
   p_h=' , '.join([ "%s" for y in [''.join([ i for i in t[x]]).split(',')][0]])
   val_p=[ i for i in t[x]][0]
   val=t[x][val_p]
   cu.executemany("INSERT INTO "+x+" ( "+''.join([ i for i in t[x]])+" ) VALUES ( " +p_h+" )",val)
  cu.close()
  co.close()
 except Exception as ex:
  print(ex)
 data["database"]["tables_names"]=a
 data["database"]["database_type"]=db
 write_configs(data)



def save_file(f,path='tmp'):
 create_dir_file(path, exist_ok=True)
 return sanitizy.FILE_UPLOAD.save_file(f,path=path)


def set_sqlite_database(data):
 co=get_sqlite_connection(data["sqlite"]["connection"])
 cu=get_cursor(co)
 t=data["database"]["tables"]
 a=[]
 for x in t:
  a.append({x: [ i for i in t[x]]})
  cu.execute("CREATE TABLE IF NOT EXISTS "+x+" ( "+' , '.join([ i+" "+t[x][i] for i in t[x]])+" )")
 data["database"]["tables_names"]=a
 t=data["database"]["values"]
 for x in t:
  p_h=' , '.join([ "?" for y in [''.join([ i for i in t[x]]).split(',')][0]])
  val_p=[ i for i in t[x]][0]
  val=t[x][val_p]
  cu.executemany("INSERT INTO "+x+" ( "+''.join([ i for i in t[x]])+" ) VALUES ( " +p_h+" )",val)
 cu.close()
 co.close()
 data["database"]["tables_names"]=a
 data["database"]["database_type"]="sqlite"
 write_configs(data)

supported_dbs=["sqlite","mysql","mariadb","postgresql","mssql","oracle"]
supported_inits=["app","config","install"]
supported_args=["init","db","upgrade","examples","add_model","delete_model","add_template","delete_template","add_route","delete_route","firebase_apikey","firebase_bucket","firebase_configs","manager","pro","dev"]

def help_msg(e):
  dbs=" or ".join(supported_dbs)
  print(e+"""

Usage:
        
        flask_man [args...]

args:
        

        manager: to launch the web interface and manage the project from there
        

        examples: to show commands examples
        

        upgrade: to upgrade to the latest version of flask_man package
        

        init: to create "config.json" and python files that contains 
              code and setup configurations, and to install required packages 
        

        db: to choose database type to use ( """+dbs+""" )
        

        add_template: create a template file with that path in the 
                      templates folder,add the name to the "config.json" 
                      file and add necessary code to "templates.py"
        

        delete_template: delete the template file with that path from the
                         templates folder, remove the name from the 
                         "config.json" file and delete the code from "templates.py"
        

        add_route: add the name to the "config.json" file and 
                   add necessary code to "routes.py"
        

        delete_route: remove the name from the "config.json"
                      file and delete the code from "routes.py"
        
        
        add_model: add the name to the "config.json" file and 
                   add necessary code to "models.py"
        

        delete_model: remove the name from the "config.json"
                      file and delete the code from "models.py"
        
        
        firebase_apikey: set the firebase APIKey
        
        
        firebase_bucket: set the firebase storage bucket
        
        
        firebase_configs: copy the firebase storage bucket's configs' 
                          file to the local configs file
        
        
        pro: set project to production mode
        
        
        dev: set project to development mode""")


def examples_msg():
 print("""** Launching the web interface:


Example:
        
        
        flask_man manager




** Upgrading the package:


Example:
        
        
        flask_man upgrade




** Creating a Project:


Example 1 (database: SQLite) :


        flask_man init config
        flask_man db sqlite
        flask_man init app
        flask_man init install


Example 2 (database: MySQL/MariaDB) :


        flask_man init config
        flask_man db mysql
        flask_man init app
        flask_man init install
        

Example 3 (database: PostgreSQL) :


        flask_man init config
        flask_man db postgresql
        flask_man init app
        flask_man init install


Example 4 (database: MS SQL) :


        flask_man init config
        flask_man db mssql
        flask_man init app
        flask_man init install


Example 5 (database: Oracle SQL) :


        flask_man init config
        flask_man db oracle
        flask_man init app
        flask_man init install




** Installing the requirements:


Example:
        
        
        flask_man init install




** Add a template to the project:


Example:


        flask_man add_template "admin/login.html"




** Remove a template from the project:


Example:


        flask_man delete_template "admin/login.html"




** Add a model to the project:


Example:


        flask_man add_model "user"




** Remove a model from the project:


Example:


        flask_man delete_model "user"




** Add a route to the project:


Example 1:


        flask_man add_route "admin/upload"


Example 2:


        flask_man add_route "/profile/<user_id>"




** Remove a route from the project:


Example 1:


        flask_man delete_route "admin/upload"


Example 2:


        flask_man delete_route "/profile/<user_id>" 




** Set firebase APIKey:


Example :


        flask_man firebase_apikey "kjkhgyftrdfghjklkjhgfrdefg"




** Set firebase storage bucket:


Example :


        flask_man firebase_bucket "myfbbucket.appspot.com"




** Copy firebase storage bucket's config file to local config file:


Example 1 (Non-Windows):


        flask_man firebase_configs "/home/root/configs.json"


Example 2 (Windows):


        flask_man firebase_configs "C:\\Users\\user\\Desktop\\configs.json"




** Change Database type:


Example 1:


        flask_man db mysql


Example 2:


        flask_man db postgresql




** Go production:


Example :


        flask_man pro
        



** Go development:


Example :


        flask_man dev""")



def csrf_referer_checker(req,allowed_domains=[]):
 return sanitizy.CSRF.validate_flask(req,allowed_domains=allowed_domains)



def get_templates_routes():
 try:
  d=read_configs()
 except:
  return ''
 return ''.join([ "<option value='{}'>{}</option>".format(x,x) for x in d["app"]["templates"]+d["app"]["routes"]])


def get_models():
 try:
  d=read_configs()
 except:
  return ''
 return ''.join([ "<option value='{}'>{}</option>".format(x,x) for x in d["app"]["models"]])


def manager():
 app = Flask(__name__)
 
 
 @app.before_request
 def validate():
  if request.method=='POST' and csrf_referer_checker(request)==False:
   return "Unauthorized",401
 
 @app.route('/add',methods=["POST"])
 def add():
  t=request.form.get("type",'')
  a=request.form.get("template",'').split(',')
  if t=='template':
   for x in a:
    if x.strip()!='':
     add_template(x)
  else:
   for x in a:
    if x.strip()!='':
     add_route(x)
  return redirect('/')
  
  
 @app.route('/delete',methods=["POST"])
 def delete():
  t=request.form.get("type",'')
  a=request.form.get("template",'').split(',')
  if t=='template':
   if a.strip()!='':
     delete_template(a)
  else:
   if a.strip()!='':
     delete_route(a)
  return redirect('/')

 @app.route('/add_m',methods=["POST"])
 def add_m():
  a=request.form.get("model",'').split(',')
  for x in a:
   if x.strip()!='':
    add_model(x)
  return redirect('/')
  
  
 @app.route('/delete_m',methods=["POST"])
 def delete_m():
  a=request.form.get('model','')
  if a.strip()!='':
   delete_model(request.form["model"])
  return redirect('/')

 @app.route('/db',methods=["POST"])
 def db():
  t=request.form.get("db",'')
  if t in supported_dbs:
   os.system('flask_man db '+t)
  return redirect('/') 
  
  
 @app.route('/go',methods=["POST"])
 def go():
  t=request.form.get("go",'')
  if t in ["dev","pro"]:
   os.system('flask_man '+t)
  return redirect('/') 
  
  
 @app.route('/create',methods=["POST"])
 def create():
  t=request.form.get("db",'')
  if t in supported_dbs:
   if file_exists('config.json')==False:
    os.system('flask_man init config')
   os.system('flask_man db '+t)
   os.system('flask_man init app')
   os.system('flask_man init install')
  return redirect('/') 
 
 
 
 @app.route('/fsb',methods=["POST"])
 def fsb():
  t=request.form["name"]
  set_firebase_bucket(t)
  return redirect('/') 
 
 
 @app.route('/fsb_conf',methods=["POST"])
 def fsb_conf():
  d=read_configs()
  t=save_file(request.files["path"],path=bind_path('tmp','config'))
  write_firebase_configs_(t)
  os.remove(t)
  return redirect('/') 
  
 
 @app.route('/fb_key',methods=["POST"])
 def fb_key():
  set_firebase_apikey(request.form["key"])
  return redirect('/') 
 
 @app.route('/upgrade',methods=["POST"])
 def upgrade_():
  upgrade()
  return redirect('/')  
 
 
 @app.route('/backup',methods=["POST"])
 def backup():
  shutil.rmtree("backup", ignore_errors=True)
  create_dir_file("backup", exist_ok=True)
  path=bind_path('backup','flask-app-backup-'+datetime.datetime.now().strftime("%Y-%b-%d-%H-%M-%S"))
  return send_file(shutil.make_archive(path , 'zip', root_dir='.'), as_attachment=True)
 
 @app.route('/',methods=["GET"])
 def home():
  tr=get_templates_routes()
  mo=get_models()
  return """
  <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
            "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">


    <!-- Bootstrap CSS CDN -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
    <!-- Font Awesome JS -->
    <script defer src="https://use.fontawesome.com/releases/v5.0.13/js/solid.js" integrity="sha384-tzzSw1/Vo+0N5UhStP3bvwWPq+uvzCMfrN1fEFe+xBmv1C/AtVX5K0uZtmcHitFZ" crossorigin="anonymous"></script>
    <script defer src="https://use.fontawesome.com/releases/v5.0.13/js/fontawesome.js" integrity="sha384-6OIrr52G08NpOFSZdxxz1xdNSndlD4vdcf/q2myIUVO0VsqaGHJsB0RaBE01VTOY" crossorigin="anonymous"></script>

    <!-- jQuery CDN - Slim version (=without AJAX) -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <!-- Popper.JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js" integrity="sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ" crossorigin="anonymous"></script>
    <!-- Bootstrap JS -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>

<style>
:root{--blue:#007bff;--indigo:#6610f2;--purple:#6f42c1;--pink:#e83e8c;--red:#dc3545;--orange:#fd7e14;--yellow:#ffc107;--green:#28a745;--teal:#20c997;--cyan:#17a2b8;--white:#fff;--gray:#1d1e2f;--gray-dark:#11111d;--primary:#714cdf;--secondary:#16a4de;--success:#17b06b;--info:#2983fe;--warning:#f97515;--danger:#ff3c5c;--light:#dbebfb;--dark:#32334a;--breakpoint-xs:0;--breakpoint-sm:576px;--breakpoint-md:768px;--breakpoint-lg:992px;--breakpoint-xl:1200px;--font-family-sans-serif:"Roboto",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";--font-family-monospace:SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}*,::after,::before{-webkit-box-sizing:border-box;box-sizing:border-box}html{font-family:sans-serif;line-height:1.15;-webkit-text-size-adjust:100%;-webkit-tap-highlight-color:transparent}article,aside,figcaption,figure,footer,header,hgroup,main,nav,section{display:block}body{margin:0;font-family:Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-size:1rem;font-weight:400;line-height:1.5;color:#e4e2ff;text-align:left;background-color:#0c0d16}[tabindex="-1"]:focus{outline:0!important}hr{-webkit-box-sizing:content-box;box-sizing:content-box;height:0;overflow:visible}h1,h2,h3,h4,h5,h6{margin-top:0;margin-bottom:.5rem}p{margin-top:0;margin-bottom:1rem}abbr[data-original-title],abbr[title]{text-decoration:underline;-webkit-text-decoration:underline dotted;text-decoration:underline dotted;cursor:help;border-bottom:0;-webkit-text-decoration-skip-ink:none;text-decoration-skip-ink:none}address{margin-bottom:1rem;font-style:normal;line-height:inherit}dl,ol,ul{margin-top:0;margin-bottom:1rem}ol ol,ol ul,ul ol,ul ul{margin-bottom:0}dt{font-weight:700}dd{margin-bottom:.5rem;margin-left:0}blockquote{margin:0 0 1rem}b,strong{font-weight:bolder}small{font-size:80%}sub,sup{position:relative;font-size:75%;line-height:0;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}a{color:#714cdf;text-decoration:none;background-color:transparent}a:hover{color:#4922bd;text-decoration:underline}a:not([href]):not([tabindex]){color:inherit;text-decoration:none}a:not([href]):not([tabindex]):focus,a:not([href]):not([tabindex]):hover{color:inherit;text-decoration:none}a:not([href]):not([tabindex]):focus{outline:0}code,kbd,pre,samp{font-family:SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;font-size:1em}pre{margin-top:0;margin-bottom:1rem;overflow:auto}figure{margin:0 0 1rem}img{vertical-align:middle;border-style:none}svg{overflow:hidden;vertical-align:middle}table{border-collapse:collapse}caption{padding-top:.75rem;padding-bottom:.75rem;color:#81839a;text-align:left;caption-side:bottom}th{text-align:inherit}label{display:inline-block;margin-bottom:.5rem}button{border-radius:0}button:focus{outline:1px dotted;outline:5px auto -webkit-focus-ring-color}button,input,optgroup,select,textarea{margin:0;font-family:inherit;font-size:inherit;line-height:inherit}button,input{overflow:visible}button,select{text-transform:none}select{word-wrap:normal}[type=button],[type=reset],[type=submit],button{-webkit-appearance:button}[type=button]:not(:disabled),[type=reset]:not(:disabled),[type=submit]:not(:disabled),button:not(:disabled){cursor:pointer}[type=button]::-moz-focus-inner,[type=reset]::-moz-focus-inner,[type=submit]::-moz-focus-inner,button::-moz-focus-inner{padding:0;border-style:none}input[type=checkbox],input[type=radio]{-webkit-box-sizing:border-box;box-sizing:border-box;padding:0}input[type=date],input[type=datetime-local],input[type=month],input[type=time]{-webkit-appearance:listbox}textarea{overflow:auto;resize:vertical}fieldset{min-width:0;padding:0;margin:0;border:0}legend{display:block;width:100%;max-width:100%;padding:0;margin-bottom:.5rem;font-size:1.5rem;line-height:inherit;color:inherit;white-space:normal}progress{vertical-align:baseline}[type=number]::-webkit-inner-spin-button,[type=number]::-webkit-outer-spin-button{height:auto}[type=search]{outline-offset:-2px;-webkit-appearance:none}[type=search]::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{font:inherit;-webkit-appearance:button}output{display:inline-block}summary{display:list-item;cursor:pointer}template{display:none}[hidden]{display:none!important}.h1,.h2,.h3,.h4,.h5,.h6,h1,h2,h3,h4,h5,h6{margin-bottom:.5rem;font-weight:500;line-height:1.2}.h1,h1{font-size:2.5rem}.h2,h2{font-size:2rem}.h3,h3{font-size:1.75rem}.h4,h4{font-size:1.5rem}.h5,h5{font-size:1.25rem}.h6,h6{font-size:1rem}.lead{font-size:1.25rem;font-weight:300}.display-1{font-size:4.5rem;font-weight:300;line-height:1.2}.display-2{font-size:3.5rem;font-weight:300;line-height:1.2}.display-3{font-size:2.5rem;font-weight:300;line-height:1.2}.display-4{font-size:2rem;font-weight:300;line-height:1.2}hr{margin-top:1rem;margin-bottom:1rem;border:0;border-top:1px solid rgba(0,0,0,.1)}.small,small{font-size:80%;font-weight:400}.mark,mark{padding:.2em;background-color:#fcf8e3}.list-unstyled{padding-left:0;list-style:none}.list-inline{padding-left:0;list-style:none}.list-inline-item{display:inline-block}.list-inline-item:not(:last-child){margin-right:.5rem}.initialism{font-size:90%;text-transform:uppercase}.blockquote{margin-bottom:1rem;font-size:1.25rem}.blockquote-footer{display:block;font-size:80%;color:#81839a}.blockquote-footer::before{content:"\2014\00A0"}.img-fluid{max-width:100%;height:auto}.img-thumbnail{padding:.25rem;background-color:#0c0d16;border:1px solid #151623;border-radius:6px;max-width:100%;height:auto}.figure{display:inline-block}.figure-img{margin-bottom:.5rem;line-height:1}.figure-caption{font-size:90%;color:#1d1e2f}code{font-size:87.5%;color:#2983fe;word-break:break-word}a>code{color:inherit}kbd{padding:.2rem .4rem;font-size:87.5%;color:#32334a;background-color:#0a0b14;border-radius:.2rem}kbd kbd{padding:0;font-size:100%;font-weight:700}pre{display:block;font-size:87.5%;color:#0a0b14}pre code{font-size:inherit;color:inherit;word-break:normal}.pre-scrollable{max-height:340px;overflow-y:scroll}.container{width:100%;padding-right:15px;padding-left:15px;margin-right:auto;margin-left:auto}@media (min-width:576px){.container{max-width:540px}}@media (min-width:768px){.container{max-width:720px}}@media (min-width:992px){.container{max-width:960px}}@media (min-width:1200px){.container{max-width:1140px}}.container-fluid{width:100%;padding-right:15px;padding-left:15px;margin-right:auto;margin-left:auto}.row{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;margin-right:-15px;margin-left:-15px}.no-gutters{margin-right:0;margin-left:0}.no-gutters>.col,.no-gutters>[class*=col-]{padding-right:0;padding-left:0}.col,.col-1,.col-10,.col-11,.col-12,.col-2,.col-3,.col-4,.col-5,.col-6,.col-7,.col-8,.col-9,.col-auto,.col-lg,.col-lg-1,.col-lg-10,.col-lg-11,.col-lg-12,.col-lg-2,.col-lg-3,.col-lg-4,.col-lg-5,.col-lg-6,.col-lg-7,.col-lg-8,.col-lg-9,.col-lg-auto,.col-md,.col-md-1,.col-md-10,.col-md-11,.col-md-12,.col-md-2,.col-md-3,.col-md-4,.col-md-5,.col-md-6,.col-md-7,.col-md-8,.col-md-9,.col-md-auto,.col-sm,.col-sm-1,.col-sm-10,.col-sm-11,.col-sm-12,.col-sm-2,.col-sm-3,.col-sm-4,.col-sm-5,.col-sm-6,.col-sm-7,.col-sm-8,.col-sm-9,.col-sm-auto,.col-xl,.col-xl-1,.col-xl-10,.col-xl-11,.col-xl-12,.col-xl-2,.col-xl-3,.col-xl-4,.col-xl-5,.col-xl-6,.col-xl-7,.col-xl-8,.col-xl-9,.col-xl-auto{position:relative;width:100%;padding-right:15px;padding-left:15px}.col{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;max-width:100%}.col-auto{-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;width:auto;max-width:100%}.col-1{-webkit-box-flex:0;-webkit-flex:0 0 8.33333%;-ms-flex:0 0 8.33333%;flex:0 0 8.33333%;max-width:8.33333%}.col-2{-webkit-box-flex:0;-webkit-flex:0 0 16.66667%;-ms-flex:0 0 16.66667%;flex:0 0 16.66667%;max-width:16.66667%}.col-3{-webkit-box-flex:0;-webkit-flex:0 0 25%;-ms-flex:0 0 25%;flex:0 0 25%;max-width:25%}.col-4{-webkit-box-flex:0;-webkit-flex:0 0 33.33333%;-ms-flex:0 0 33.33333%;flex:0 0 33.33333%;max-width:33.33333%}.col-5{-webkit-box-flex:0;-webkit-flex:0 0 41.66667%;-ms-flex:0 0 41.66667%;flex:0 0 41.66667%;max-width:41.66667%}.col-6{-webkit-box-flex:0;-webkit-flex:0 0 50%;-ms-flex:0 0 50%;flex:0 0 50%;max-width:50%}.col-7{-webkit-box-flex:0;-webkit-flex:0 0 58.33333%;-ms-flex:0 0 58.33333%;flex:0 0 58.33333%;max-width:58.33333%}.col-8{-webkit-box-flex:0;-webkit-flex:0 0 66.66667%;-ms-flex:0 0 66.66667%;flex:0 0 66.66667%;max-width:66.66667%}.col-9{-webkit-box-flex:0;-webkit-flex:0 0 75%;-ms-flex:0 0 75%;flex:0 0 75%;max-width:75%}.col-10{-webkit-box-flex:0;-webkit-flex:0 0 83.33333%;-ms-flex:0 0 83.33333%;flex:0 0 83.33333%;max-width:83.33333%}.col-11{-webkit-box-flex:0;-webkit-flex:0 0 91.66667%;-ms-flex:0 0 91.66667%;flex:0 0 91.66667%;max-width:91.66667%}.col-12{-webkit-box-flex:0;-webkit-flex:0 0 100%;-ms-flex:0 0 100%;flex:0 0 100%;max-width:100%}.order-first{-webkit-box-ordinal-group:0;-webkit-order:-1;-ms-flex-order:-1;order:-1}.order-last{-webkit-box-ordinal-group:14;-webkit-order:13;-ms-flex-order:13;order:13}.order-0{-webkit-box-ordinal-group:1;-webkit-order:0;-ms-flex-order:0;order:0}.order-1{-webkit-box-ordinal-group:2;-webkit-order:1;-ms-flex-order:1;order:1}.order-2{-webkit-box-ordinal-group:3;-webkit-order:2;-ms-flex-order:2;order:2}.order-3{-webkit-box-ordinal-group:4;-webkit-order:3;-ms-flex-order:3;order:3}.order-4{-webkit-box-ordinal-group:5;-webkit-order:4;-ms-flex-order:4;order:4}.order-5{-webkit-box-ordinal-group:6;-webkit-order:5;-ms-flex-order:5;order:5}.order-6{-webkit-box-ordinal-group:7;-webkit-order:6;-ms-flex-order:6;order:6}.order-7{-webkit-box-ordinal-group:8;-webkit-order:7;-ms-flex-order:7;order:7}.order-8{-webkit-box-ordinal-group:9;-webkit-order:8;-ms-flex-order:8;order:8}.order-9{-webkit-box-ordinal-group:10;-webkit-order:9;-ms-flex-order:9;order:9}.order-10{-webkit-box-ordinal-group:11;-webkit-order:10;-ms-flex-order:10;order:10}.order-11{-webkit-box-ordinal-group:12;-webkit-order:11;-ms-flex-order:11;order:11}.order-12{-webkit-box-ordinal-group:13;-webkit-order:12;-ms-flex-order:12;order:12}.offset-1{margin-left:8.33333%}.offset-2{margin-left:16.66667%}.offset-3{margin-left:25%}.offset-4{margin-left:33.33333%}.offset-5{margin-left:41.66667%}.offset-6{margin-left:50%}.offset-7{margin-left:58.33333%}.offset-8{margin-left:66.66667%}.offset-9{margin-left:75%}.offset-10{margin-left:83.33333%}.offset-11{margin-left:91.66667%}@media (min-width:576px){.col-sm{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;max-width:100%}.col-sm-auto{-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;width:auto;max-width:100%}.col-sm-1{-webkit-box-flex:0;-webkit-flex:0 0 8.33333%;-ms-flex:0 0 8.33333%;flex:0 0 8.33333%;max-width:8.33333%}.col-sm-2{-webkit-box-flex:0;-webkit-flex:0 0 16.66667%;-ms-flex:0 0 16.66667%;flex:0 0 16.66667%;max-width:16.66667%}.col-sm-3{-webkit-box-flex:0;-webkit-flex:0 0 25%;-ms-flex:0 0 25%;flex:0 0 25%;max-width:25%}.col-sm-4{-webkit-box-flex:0;-webkit-flex:0 0 33.33333%;-ms-flex:0 0 33.33333%;flex:0 0 33.33333%;max-width:33.33333%}.col-sm-5{-webkit-box-flex:0;-webkit-flex:0 0 41.66667%;-ms-flex:0 0 41.66667%;flex:0 0 41.66667%;max-width:41.66667%}.col-sm-6{-webkit-box-flex:0;-webkit-flex:0 0 50%;-ms-flex:0 0 50%;flex:0 0 50%;max-width:50%}.col-sm-7{-webkit-box-flex:0;-webkit-flex:0 0 58.33333%;-ms-flex:0 0 58.33333%;flex:0 0 58.33333%;max-width:58.33333%}.col-sm-8{-webkit-box-flex:0;-webkit-flex:0 0 66.66667%;-ms-flex:0 0 66.66667%;flex:0 0 66.66667%;max-width:66.66667%}.col-sm-9{-webkit-box-flex:0;-webkit-flex:0 0 75%;-ms-flex:0 0 75%;flex:0 0 75%;max-width:75%}.col-sm-10{-webkit-box-flex:0;-webkit-flex:0 0 83.33333%;-ms-flex:0 0 83.33333%;flex:0 0 83.33333%;max-width:83.33333%}.col-sm-11{-webkit-box-flex:0;-webkit-flex:0 0 91.66667%;-ms-flex:0 0 91.66667%;flex:0 0 91.66667%;max-width:91.66667%}.col-sm-12{-webkit-box-flex:0;-webkit-flex:0 0 100%;-ms-flex:0 0 100%;flex:0 0 100%;max-width:100%}.order-sm-first{-webkit-box-ordinal-group:0;-webkit-order:-1;-ms-flex-order:-1;order:-1}.order-sm-last{-webkit-box-ordinal-group:14;-webkit-order:13;-ms-flex-order:13;order:13}.order-sm-0{-webkit-box-ordinal-group:1;-webkit-order:0;-ms-flex-order:0;order:0}.order-sm-1{-webkit-box-ordinal-group:2;-webkit-order:1;-ms-flex-order:1;order:1}.order-sm-2{-webkit-box-ordinal-group:3;-webkit-order:2;-ms-flex-order:2;order:2}.order-sm-3{-webkit-box-ordinal-group:4;-webkit-order:3;-ms-flex-order:3;order:3}.order-sm-4{-webkit-box-ordinal-group:5;-webkit-order:4;-ms-flex-order:4;order:4}.order-sm-5{-webkit-box-ordinal-group:6;-webkit-order:5;-ms-flex-order:5;order:5}.order-sm-6{-webkit-box-ordinal-group:7;-webkit-order:6;-ms-flex-order:6;order:6}.order-sm-7{-webkit-box-ordinal-group:8;-webkit-order:7;-ms-flex-order:7;order:7}.order-sm-8{-webkit-box-ordinal-group:9;-webkit-order:8;-ms-flex-order:8;order:8}.order-sm-9{-webkit-box-ordinal-group:10;-webkit-order:9;-ms-flex-order:9;order:9}.order-sm-10{-webkit-box-ordinal-group:11;-webkit-order:10;-ms-flex-order:10;order:10}.order-sm-11{-webkit-box-ordinal-group:12;-webkit-order:11;-ms-flex-order:11;order:11}.order-sm-12{-webkit-box-ordinal-group:13;-webkit-order:12;-ms-flex-order:12;order:12}.offset-sm-0{margin-left:0}.offset-sm-1{margin-left:8.33333%}.offset-sm-2{margin-left:16.66667%}.offset-sm-3{margin-left:25%}.offset-sm-4{margin-left:33.33333%}.offset-sm-5{margin-left:41.66667%}.offset-sm-6{margin-left:50%}.offset-sm-7{margin-left:58.33333%}.offset-sm-8{margin-left:66.66667%}.offset-sm-9{margin-left:75%}.offset-sm-10{margin-left:83.33333%}.offset-sm-11{margin-left:91.66667%}}@media (min-width:768px){.col-md{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;max-width:100%}.col-md-auto{-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;width:auto;max-width:100%}.col-md-1{-webkit-box-flex:0;-webkit-flex:0 0 8.33333%;-ms-flex:0 0 8.33333%;flex:0 0 8.33333%;max-width:8.33333%}.col-md-2{-webkit-box-flex:0;-webkit-flex:0 0 16.66667%;-ms-flex:0 0 16.66667%;flex:0 0 16.66667%;max-width:16.66667%}.col-md-3{-webkit-box-flex:0;-webkit-flex:0 0 25%;-ms-flex:0 0 25%;flex:0 0 25%;max-width:25%}.col-md-4{-webkit-box-flex:0;-webkit-flex:0 0 33.33333%;-ms-flex:0 0 33.33333%;flex:0 0 33.33333%;max-width:33.33333%}.col-md-5{-webkit-box-flex:0;-webkit-flex:0 0 41.66667%;-ms-flex:0 0 41.66667%;flex:0 0 41.66667%;max-width:41.66667%}.col-md-6{-webkit-box-flex:0;-webkit-flex:0 0 50%;-ms-flex:0 0 50%;flex:0 0 50%;max-width:50%}.col-md-7{-webkit-box-flex:0;-webkit-flex:0 0 58.33333%;-ms-flex:0 0 58.33333%;flex:0 0 58.33333%;max-width:58.33333%}.col-md-8{-webkit-box-flex:0;-webkit-flex:0 0 66.66667%;-ms-flex:0 0 66.66667%;flex:0 0 66.66667%;max-width:66.66667%}.col-md-9{-webkit-box-flex:0;-webkit-flex:0 0 75%;-ms-flex:0 0 75%;flex:0 0 75%;max-width:75%}.col-md-10{-webkit-box-flex:0;-webkit-flex:0 0 83.33333%;-ms-flex:0 0 83.33333%;flex:0 0 83.33333%;max-width:83.33333%}.col-md-11{-webkit-box-flex:0;-webkit-flex:0 0 91.66667%;-ms-flex:0 0 91.66667%;flex:0 0 91.66667%;max-width:91.66667%}.col-md-12{-webkit-box-flex:0;-webkit-flex:0 0 100%;-ms-flex:0 0 100%;flex:0 0 100%;max-width:100%}.order-md-first{-webkit-box-ordinal-group:0;-webkit-order:-1;-ms-flex-order:-1;order:-1}.order-md-last{-webkit-box-ordinal-group:14;-webkit-order:13;-ms-flex-order:13;order:13}.order-md-0{-webkit-box-ordinal-group:1;-webkit-order:0;-ms-flex-order:0;order:0}.order-md-1{-webkit-box-ordinal-group:2;-webkit-order:1;-ms-flex-order:1;order:1}.order-md-2{-webkit-box-ordinal-group:3;-webkit-order:2;-ms-flex-order:2;order:2}.order-md-3{-webkit-box-ordinal-group:4;-webkit-order:3;-ms-flex-order:3;order:3}.order-md-4{-webkit-box-ordinal-group:5;-webkit-order:4;-ms-flex-order:4;order:4}.order-md-5{-webkit-box-ordinal-group:6;-webkit-order:5;-ms-flex-order:5;order:5}.order-md-6{-webkit-box-ordinal-group:7;-webkit-order:6;-ms-flex-order:6;order:6}.order-md-7{-webkit-box-ordinal-group:8;-webkit-order:7;-ms-flex-order:7;order:7}.order-md-8{-webkit-box-ordinal-group:9;-webkit-order:8;-ms-flex-order:8;order:8}.order-md-9{-webkit-box-ordinal-group:10;-webkit-order:9;-ms-flex-order:9;order:9}.order-md-10{-webkit-box-ordinal-group:11;-webkit-order:10;-ms-flex-order:10;order:10}.order-md-11{-webkit-box-ordinal-group:12;-webkit-order:11;-ms-flex-order:11;order:11}.order-md-12{-webkit-box-ordinal-group:13;-webkit-order:12;-ms-flex-order:12;order:12}.offset-md-0{margin-left:0}.offset-md-1{margin-left:8.33333%}.offset-md-2{margin-left:16.66667%}.offset-md-3{margin-left:25%}.offset-md-4{margin-left:33.33333%}.offset-md-5{margin-left:41.66667%}.offset-md-6{margin-left:50%}.offset-md-7{margin-left:58.33333%}.offset-md-8{margin-left:66.66667%}.offset-md-9{margin-left:75%}.offset-md-10{margin-left:83.33333%}.offset-md-11{margin-left:91.66667%}}@media (min-width:992px){.col-lg{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;max-width:100%}.col-lg-auto{-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;width:auto;max-width:100%}.col-lg-1{-webkit-box-flex:0;-webkit-flex:0 0 8.33333%;-ms-flex:0 0 8.33333%;flex:0 0 8.33333%;max-width:8.33333%}.col-lg-2{-webkit-box-flex:0;-webkit-flex:0 0 16.66667%;-ms-flex:0 0 16.66667%;flex:0 0 16.66667%;max-width:16.66667%}.col-lg-3{-webkit-box-flex:0;-webkit-flex:0 0 25%;-ms-flex:0 0 25%;flex:0 0 25%;max-width:25%}.col-lg-4{-webkit-box-flex:0;-webkit-flex:0 0 33.33333%;-ms-flex:0 0 33.33333%;flex:0 0 33.33333%;max-width:33.33333%}.col-lg-5{-webkit-box-flex:0;-webkit-flex:0 0 41.66667%;-ms-flex:0 0 41.66667%;flex:0 0 41.66667%;max-width:41.66667%}.col-lg-6{-webkit-box-flex:0;-webkit-flex:0 0 50%;-ms-flex:0 0 50%;flex:0 0 50%;max-width:50%}.col-lg-7{-webkit-box-flex:0;-webkit-flex:0 0 58.33333%;-ms-flex:0 0 58.33333%;flex:0 0 58.33333%;max-width:58.33333%}.col-lg-8{-webkit-box-flex:0;-webkit-flex:0 0 66.66667%;-ms-flex:0 0 66.66667%;flex:0 0 66.66667%;max-width:66.66667%}.col-lg-9{-webkit-box-flex:0;-webkit-flex:0 0 75%;-ms-flex:0 0 75%;flex:0 0 75%;max-width:75%}.col-lg-10{-webkit-box-flex:0;-webkit-flex:0 0 83.33333%;-ms-flex:0 0 83.33333%;flex:0 0 83.33333%;max-width:83.33333%}.col-lg-11{-webkit-box-flex:0;-webkit-flex:0 0 91.66667%;-ms-flex:0 0 91.66667%;flex:0 0 91.66667%;max-width:91.66667%}.col-lg-12{-webkit-box-flex:0;-webkit-flex:0 0 100%;-ms-flex:0 0 100%;flex:0 0 100%;max-width:100%}.order-lg-first{-webkit-box-ordinal-group:0;-webkit-order:-1;-ms-flex-order:-1;order:-1}.order-lg-last{-webkit-box-ordinal-group:14;-webkit-order:13;-ms-flex-order:13;order:13}.order-lg-0{-webkit-box-ordinal-group:1;-webkit-order:0;-ms-flex-order:0;order:0}.order-lg-1{-webkit-box-ordinal-group:2;-webkit-order:1;-ms-flex-order:1;order:1}.order-lg-2{-webkit-box-ordinal-group:3;-webkit-order:2;-ms-flex-order:2;order:2}.order-lg-3{-webkit-box-ordinal-group:4;-webkit-order:3;-ms-flex-order:3;order:3}.order-lg-4{-webkit-box-ordinal-group:5;-webkit-order:4;-ms-flex-order:4;order:4}.order-lg-5{-webkit-box-ordinal-group:6;-webkit-order:5;-ms-flex-order:5;order:5}.order-lg-6{-webkit-box-ordinal-group:7;-webkit-order:6;-ms-flex-order:6;order:6}.order-lg-7{-webkit-box-ordinal-group:8;-webkit-order:7;-ms-flex-order:7;order:7}.order-lg-8{-webkit-box-ordinal-group:9;-webkit-order:8;-ms-flex-order:8;order:8}.order-lg-9{-webkit-box-ordinal-group:10;-webkit-order:9;-ms-flex-order:9;order:9}.order-lg-10{-webkit-box-ordinal-group:11;-webkit-order:10;-ms-flex-order:10;order:10}.order-lg-11{-webkit-box-ordinal-group:12;-webkit-order:11;-ms-flex-order:11;order:11}.order-lg-12{-webkit-box-ordinal-group:13;-webkit-order:12;-ms-flex-order:12;order:12}.offset-lg-0{margin-left:0}.offset-lg-1{margin-left:8.33333%}.offset-lg-2{margin-left:16.66667%}.offset-lg-3{margin-left:25%}.offset-lg-4{margin-left:33.33333%}.offset-lg-5{margin-left:41.66667%}.offset-lg-6{margin-left:50%}.offset-lg-7{margin-left:58.33333%}.offset-lg-8{margin-left:66.66667%}.offset-lg-9{margin-left:75%}.offset-lg-10{margin-left:83.33333%}.offset-lg-11{margin-left:91.66667%}}@media (min-width:1200px){.col-xl{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;max-width:100%}.col-xl-auto{-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;width:auto;max-width:100%}.col-xl-1{-webkit-box-flex:0;-webkit-flex:0 0 8.33333%;-ms-flex:0 0 8.33333%;flex:0 0 8.33333%;max-width:8.33333%}.col-xl-2{-webkit-box-flex:0;-webkit-flex:0 0 16.66667%;-ms-flex:0 0 16.66667%;flex:0 0 16.66667%;max-width:16.66667%}.col-xl-3{-webkit-box-flex:0;-webkit-flex:0 0 25%;-ms-flex:0 0 25%;flex:0 0 25%;max-width:25%}.col-xl-4{-webkit-box-flex:0;-webkit-flex:0 0 33.33333%;-ms-flex:0 0 33.33333%;flex:0 0 33.33333%;max-width:33.33333%}.col-xl-5{-webkit-box-flex:0;-webkit-flex:0 0 41.66667%;-ms-flex:0 0 41.66667%;flex:0 0 41.66667%;max-width:41.66667%}.col-xl-6{-webkit-box-flex:0;-webkit-flex:0 0 50%;-ms-flex:0 0 50%;flex:0 0 50%;max-width:50%}.col-xl-7{-webkit-box-flex:0;-webkit-flex:0 0 58.33333%;-ms-flex:0 0 58.33333%;flex:0 0 58.33333%;max-width:58.33333%}.col-xl-8{-webkit-box-flex:0;-webkit-flex:0 0 66.66667%;-ms-flex:0 0 66.66667%;flex:0 0 66.66667%;max-width:66.66667%}.col-xl-9{-webkit-box-flex:0;-webkit-flex:0 0 75%;-ms-flex:0 0 75%;flex:0 0 75%;max-width:75%}.col-xl-10{-webkit-box-flex:0;-webkit-flex:0 0 83.33333%;-ms-flex:0 0 83.33333%;flex:0 0 83.33333%;max-width:83.33333%}.col-xl-11{-webkit-box-flex:0;-webkit-flex:0 0 91.66667%;-ms-flex:0 0 91.66667%;flex:0 0 91.66667%;max-width:91.66667%}.col-xl-12{-webkit-box-flex:0;-webkit-flex:0 0 100%;-ms-flex:0 0 100%;flex:0 0 100%;max-width:100%}.order-xl-first{-webkit-box-ordinal-group:0;-webkit-order:-1;-ms-flex-order:-1;order:-1}.order-xl-last{-webkit-box-ordinal-group:14;-webkit-order:13;-ms-flex-order:13;order:13}.order-xl-0{-webkit-box-ordinal-group:1;-webkit-order:0;-ms-flex-order:0;order:0}.order-xl-1{-webkit-box-ordinal-group:2;-webkit-order:1;-ms-flex-order:1;order:1}.order-xl-2{-webkit-box-ordinal-group:3;-webkit-order:2;-ms-flex-order:2;order:2}.order-xl-3{-webkit-box-ordinal-group:4;-webkit-order:3;-ms-flex-order:3;order:3}.order-xl-4{-webkit-box-ordinal-group:5;-webkit-order:4;-ms-flex-order:4;order:4}.order-xl-5{-webkit-box-ordinal-group:6;-webkit-order:5;-ms-flex-order:5;order:5}.order-xl-6{-webkit-box-ordinal-group:7;-webkit-order:6;-ms-flex-order:6;order:6}.order-xl-7{-webkit-box-ordinal-group:8;-webkit-order:7;-ms-flex-order:7;order:7}.order-xl-8{-webkit-box-ordinal-group:9;-webkit-order:8;-ms-flex-order:8;order:8}.order-xl-9{-webkit-box-ordinal-group:10;-webkit-order:9;-ms-flex-order:9;order:9}.order-xl-10{-webkit-box-ordinal-group:11;-webkit-order:10;-ms-flex-order:10;order:10}.order-xl-11{-webkit-box-ordinal-group:12;-webkit-order:11;-ms-flex-order:11;order:11}.order-xl-12{-webkit-box-ordinal-group:13;-webkit-order:12;-ms-flex-order:12;order:12}.offset-xl-0{margin-left:0}.offset-xl-1{margin-left:8.33333%}.offset-xl-2{margin-left:16.66667%}.offset-xl-3{margin-left:25%}.offset-xl-4{margin-left:33.33333%}.offset-xl-5{margin-left:41.66667%}.offset-xl-6{margin-left:50%}.offset-xl-7{margin-left:58.33333%}.offset-xl-8{margin-left:66.66667%}.offset-xl-9{margin-left:75%}.offset-xl-10{margin-left:83.33333%}.offset-xl-11{margin-left:91.66667%}}.table{width:100%;margin-bottom:1rem;color:#e4e2ff}.table td,.table th{padding:.75rem;vertical-align:top;border-top:1px solid #28293e}.table thead th{vertical-align:bottom;border-bottom:2px solid #28293e}.table tbody+tbody{border-top:2px solid #28293e}.table-sm td,.table-sm th{padding:.3rem}.table-bordered{border:1px solid #28293e}.table-bordered td,.table-bordered th{border:1px solid #28293e}.table-bordered thead td,.table-bordered thead th{border-bottom-width:2px}.table-borderless tbody+tbody,.table-borderless td,.table-borderless th,.table-borderless thead th{border:0}.table-striped tbody tr:nth-of-type(odd){background-color:rgba(0,0,0,.05)}.table-hover tbody tr:hover{color:#e4e2ff;background-color:rgba(0,0,0,.075)}.table-primary,.table-primary>td,.table-primary>th{background-color:#d7cdf6}.table-primary tbody+tbody,.table-primary td,.table-primary th,.table-primary thead th{border-color:#b5a2ee}.table-hover .table-primary:hover{background-color:#c6b7f2}.table-hover .table-primary:hover>td,.table-hover .table-primary:hover>th{background-color:#c6b7f2}.table-secondary,.table-secondary>td,.table-secondary>th{background-color:#bee6f6}.table-secondary tbody+tbody,.table-secondary td,.table-secondary th,.table-secondary thead th{border-color:#86d0ee}.table-hover .table-secondary:hover{background-color:#a8ddf3}.table-hover .table-secondary:hover>td,.table-hover .table-secondary:hover>th{background-color:#a8ddf3}.table-success,.table-success>td,.table-success>th{background-color:#bee9d6}.table-success tbody+tbody,.table-success td,.table-success th,.table-success thead th{border-color:#86d6b2}.table-hover .table-success:hover{background-color:#abe3ca}.table-hover .table-success:hover>td,.table-hover .table-success:hover>th{background-color:#abe3ca}.table-info,.table-info>td,.table-info>th{background-color:#c3dcff}.table-info tbody+tbody,.table-info td,.table-info th,.table-info thead th{border-color:#90bffe}.table-hover .table-info:hover{background-color:#aacdff}.table-hover .table-info:hover>td,.table-hover .table-info:hover>th{background-color:#aacdff}.table-warning,.table-warning>td,.table-warning>th{background-color:#fdd8bd}.table-warning tbody+tbody,.table-warning td,.table-warning th,.table-warning thead th{border-color:#fcb785}.table-hover .table-warning:hover{background-color:#fcc9a4}.table-hover .table-warning:hover>td,.table-hover .table-warning:hover>th{background-color:#fcc9a4}.table-danger,.table-danger>td,.table-danger>th{background-color:#ffc8d1}.table-danger tbody+tbody,.table-danger td,.table-danger th,.table-danger thead th{border-color:#ff9aaa}.table-hover .table-danger:hover{background-color:#ffafbc}.table-hover .table-danger:hover>td,.table-hover .table-danger:hover>th{background-color:#ffafbc}.table-light,.table-light>td,.table-light>th{background-color:#f5f9fe}.table-light tbody+tbody,.table-light td,.table-light th,.table-light thead th{border-color:#ecf5fd}.table-hover .table-light:hover{background-color:#deebfc}.table-hover .table-light:hover>td,.table-hover .table-light:hover>th{background-color:#deebfc}.table-dark,.table-dark>td,.table-dark>th{background-color:#c6c6cc}.table-dark tbody+tbody,.table-dark td,.table-dark th,.table-dark thead th{border-color:#9495a1}.table-hover .table-dark:hover{background-color:#b9b9c0}.table-hover .table-dark:hover>td,.table-hover .table-dark:hover>th{background-color:#b9b9c0}.table-active,.table-active>td,.table-active>th{background-color:rgba(0,0,0,.075)}.table-hover .table-active:hover{background-color:rgba(0,0,0,.075)}.table-hover .table-active:hover>td,.table-hover .table-active:hover>th{background-color:rgba(0,0,0,.075)}.table .thead-dark th{color:#e4e2ff;background-color:#11111d;border-color:#1f1f35}.table .thead-light th{color:#151623;background-color:#282a38;border-color:#28293e}.table-dark{color:#e4e2ff;background-color:#11111d}.table-dark td,.table-dark th,.table-dark thead th{border-color:#1f1f35}.table-dark.table-bordered{border:0}.table-dark.table-striped tbody tr:nth-of-type(odd){background-color:rgba(50,51,74,.05)}.table-dark.table-hover tbody tr:hover{color:#e4e2ff;background-color:rgba(50,51,74,.075)}@media (max-width:575.98px){.table-responsive-sm{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}.table-responsive-sm>.table-bordered{border:0}}@media (max-width:767.98px){.table-responsive-md{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}.table-responsive-md>.table-bordered{border:0}}@media (max-width:991.98px){.table-responsive-lg{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}.table-responsive-lg>.table-bordered{border:0}}@media (max-width:1199.98px){.table-responsive-xl{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}.table-responsive-xl>.table-bordered{border:0}}.table-responsive{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}.table-responsive>.table-bordered{border:0}.form-control{display:block;width:100%;height:calc(1.5em + .75rem + 2px);padding:.375rem .75rem;font-size:1rem;font-weight:400;line-height:1.5;color:#adabc6;background-color:#28293e;background-clip:padding-box;border:1px solid #11111d;border-radius:6px;-webkit-transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}@media (prefers-reduced-motion:reduce){.form-control{-webkit-transition:none;-o-transition:none;transition:none}}.form-control::-ms-expand{background-color:transparent;border:0}.form-control:focus{color:#adabc6;background-color:#28293e;border-color:#c7b8f2;outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 .2rem rgba(113,76,223,.25)}.form-control::-webkit-input-placeholder{color:#a19fb9;opacity:1}.form-control::-moz-placeholder{color:#a19fb9;opacity:1}.form-control:-ms-input-placeholder{color:#a19fb9;opacity:1}.form-control::-ms-input-placeholder{color:#a19fb9;opacity:1}.form-control::placeholder{color:#a19fb9;opacity:1}.form-control:disabled,.form-control[readonly]{background-color:#282a38;opacity:1}select.form-control:focus::-ms-value{color:#adabc6;background-color:#28293e}.form-control-file,.form-control-range{display:block;width:100%}.col-form-label{padding-top:calc(.375rem + 1px);padding-bottom:calc(.375rem + 1px);margin-bottom:0;font-size:inherit;line-height:1.5}.col-form-label-lg{padding-top:calc(.5rem + 1px);padding-bottom:calc(.5rem + 1px);font-size:1.25rem;line-height:1.5}.col-form-label-sm{padding-top:calc(.25rem + 1px);padding-bottom:calc(.25rem + 1px);font-size:.875rem;line-height:1.5}.form-control-plaintext{display:block;width:100%;padding-top:.375rem;padding-bottom:.375rem;margin-bottom:0;line-height:1.5;color:#e4e2ff;background-color:transparent;border:solid transparent;border-width:1px 0}.form-control-plaintext.form-control-lg,.form-control-plaintext.form-control-sm{padding-right:0;padding-left:0}.form-control-sm{height:calc(1.5em + .5rem + 2px);padding:.25rem .5rem;font-size:.875rem;line-height:1.5;border-radius:.2rem}.form-control-lg{height:calc(1.5em + 1rem + 2px);padding:.5rem 1rem;font-size:1.25rem;line-height:1.5;border-radius:6px}select.form-control[multiple],select.form-control[size]{height:auto}textarea.form-control{height:auto}.form-group{margin-bottom:1rem}.form-text{display:block;margin-top:.25rem}.form-row{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;margin-right:-5px;margin-left:-5px}.form-row>.col,.form-row>[class*=col-]{padding-right:5px;padding-left:5px}.form-check{position:relative;display:block;padding-left:1.25rem}.form-check-input{position:absolute;margin-top:.3rem;margin-left:-1.25rem}.form-check-input:disabled~.form-check-label{color:#81839a}.form-check-label{margin-bottom:0}.form-check-inline{display:-webkit-inline-box;display:-webkit-inline-flex;display:-ms-inline-flexbox;display:inline-flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;padding-left:0;margin-right:.75rem}.form-check-inline .form-check-input{position:static;margin-top:0;margin-right:.3125rem;margin-left:0}.valid-feedback{display:none;width:100%;margin-top:.25rem;font-size:80%;color:#17b06b}.valid-tooltip{position:absolute;top:100%;z-index:5;display:none;max-width:100%;padding:.25rem .5rem;margin-top:.1rem;font-size:.875rem;line-height:1.5;color:#fff;background-color:rgba(23,176,107,.9);border-radius:6px}.form-control.is-valid,.was-validated .form-control:valid{border-color:#17b06b;padding-right:calc(1.5em + .75rem);background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2317b06b' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e");background-repeat:no-repeat;background-position:center right calc(.375em + .1875rem);-webkit-background-size:calc(.75em + .375rem) calc(.75em + .375rem);background-size:calc(.75em + .375rem) calc(.75em + .375rem)}.form-control.is-valid:focus,.was-validated .form-control:valid:focus{border-color:#17b06b;-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.25);box-shadow:0 0 0 .2rem rgba(23,176,107,.25)}.form-control.is-valid~.valid-feedback,.form-control.is-valid~.valid-tooltip,.was-validated .form-control:valid~.valid-feedback,.was-validated .form-control:valid~.valid-tooltip{display:block}.was-validated textarea.form-control:valid,textarea.form-control.is-valid{padding-right:calc(1.5em + .75rem);background-position:top calc(.375em + .1875rem) right calc(.375em + .1875rem)}.custom-select.is-valid,.was-validated .custom-select:valid{border-color:#17b06b;padding-right:calc((1em + .75rem) * 3 / 4 + 1.75rem);background:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'%3e%3cpath fill='%2311111d' d='M2 0L0 2h4zm0 5L0 3h4z'/%3e%3c/svg%3e") no-repeat right .75rem center/8px 10px,url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2317b06b' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e") #32334a no-repeat center right 1.75rem/calc(.75em + .375rem) calc(.75em + .375rem)}.custom-select.is-valid:focus,.was-validated .custom-select:valid:focus{border-color:#17b06b;-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.25);box-shadow:0 0 0 .2rem rgba(23,176,107,.25)}.custom-select.is-valid~.valid-feedback,.custom-select.is-valid~.valid-tooltip,.was-validated .custom-select:valid~.valid-feedback,.was-validated .custom-select:valid~.valid-tooltip{display:block}.form-control-file.is-valid~.valid-feedback,.form-control-file.is-valid~.valid-tooltip,.was-validated .form-control-file:valid~.valid-feedback,.was-validated .form-control-file:valid~.valid-tooltip{display:block}.form-check-input.is-valid~.form-check-label,.was-validated .form-check-input:valid~.form-check-label{color:#17b06b}.form-check-input.is-valid~.valid-feedback,.form-check-input.is-valid~.valid-tooltip,.was-validated .form-check-input:valid~.valid-feedback,.was-validated .form-check-input:valid~.valid-tooltip{display:block}.custom-control-input.is-valid~.custom-control-label,.was-validated .custom-control-input:valid~.custom-control-label{color:#17b06b}.custom-control-input.is-valid~.custom-control-label::before,.was-validated .custom-control-input:valid~.custom-control-label::before{border-color:#17b06b}.custom-control-input.is-valid~.valid-feedback,.custom-control-input.is-valid~.valid-tooltip,.was-validated .custom-control-input:valid~.valid-feedback,.was-validated .custom-control-input:valid~.valid-tooltip{display:block}.custom-control-input.is-valid:checked~.custom-control-label::before,.was-validated .custom-control-input:valid:checked~.custom-control-label::before{border-color:#1ddd86;background-color:#1ddd86}.custom-control-input.is-valid:focus~.custom-control-label::before,.was-validated .custom-control-input:valid:focus~.custom-control-label::before{-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.25);box-shadow:0 0 0 .2rem rgba(23,176,107,.25)}.custom-control-input.is-valid:focus:not(:checked)~.custom-control-label::before,.was-validated .custom-control-input:valid:focus:not(:checked)~.custom-control-label::before{border-color:#17b06b}.custom-file-input.is-valid~.custom-file-label,.was-validated .custom-file-input:valid~.custom-file-label{border-color:#17b06b}.custom-file-input.is-valid~.valid-feedback,.custom-file-input.is-valid~.valid-tooltip,.was-validated .custom-file-input:valid~.valid-feedback,.was-validated .custom-file-input:valid~.valid-tooltip{display:block}.custom-file-input.is-valid:focus~.custom-file-label,.was-validated .custom-file-input:valid:focus~.custom-file-label{border-color:#17b06b;-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.25);box-shadow:0 0 0 .2rem rgba(23,176,107,.25)}.invalid-feedback{display:none;width:100%;margin-top:.25rem;font-size:80%;color:#ff3c5c}.invalid-tooltip{position:absolute;top:100%;z-index:5;display:none;max-width:100%;padding:.25rem .5rem;margin-top:.1rem;font-size:.875rem;line-height:1.5;color:#fff;background-color:rgba(255,60,92,.9);border-radius:6px}.form-control.is-invalid,.was-validated .form-control:invalid{border-color:#ff3c5c;padding-right:calc(1.5em + .75rem);background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%23ff3c5c' viewBox='-2 -2 7 7'%3e%3cpath stroke='%23ff3c5c' d='M0 0l3 3m0-3L0 3'/%3e%3ccircle r='.5'/%3e%3ccircle cx='3' r='.5'/%3e%3ccircle cy='3' r='.5'/%3e%3ccircle cx='3' cy='3' r='.5'/%3e%3c/svg%3E");background-repeat:no-repeat;background-position:center right calc(.375em + .1875rem);-webkit-background-size:calc(.75em + .375rem) calc(.75em + .375rem);background-size:calc(.75em + .375rem) calc(.75em + .375rem)}.form-control.is-invalid:focus,.was-validated .form-control:invalid:focus{border-color:#ff3c5c;-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.25);box-shadow:0 0 0 .2rem rgba(255,60,92,.25)}.form-control.is-invalid~.invalid-feedback,.form-control.is-invalid~.invalid-tooltip,.was-validated .form-control:invalid~.invalid-feedback,.was-validated .form-control:invalid~.invalid-tooltip{display:block}.was-validated textarea.form-control:invalid,textarea.form-control.is-invalid{padding-right:calc(1.5em + .75rem);background-position:top calc(.375em + .1875rem) right calc(.375em + .1875rem)}.custom-select.is-invalid,.was-validated .custom-select:invalid{border-color:#ff3c5c;padding-right:calc((1em + .75rem) * 3 / 4 + 1.75rem);background:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'%3e%3cpath fill='%2311111d' d='M2 0L0 2h4zm0 5L0 3h4z'/%3e%3c/svg%3e") no-repeat right .75rem center/8px 10px,url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%23ff3c5c' viewBox='-2 -2 7 7'%3e%3cpath stroke='%23ff3c5c' d='M0 0l3 3m0-3L0 3'/%3e%3ccircle r='.5'/%3e%3ccircle cx='3' r='.5'/%3e%3ccircle cy='3' r='.5'/%3e%3ccircle cx='3' cy='3' r='.5'/%3e%3c/svg%3E") #32334a no-repeat center right 1.75rem/calc(.75em + .375rem) calc(.75em + .375rem)}.custom-select.is-invalid:focus,.was-validated .custom-select:invalid:focus{border-color:#ff3c5c;-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.25);box-shadow:0 0 0 .2rem rgba(255,60,92,.25)}.custom-select.is-invalid~.invalid-feedback,.custom-select.is-invalid~.invalid-tooltip,.was-validated .custom-select:invalid~.invalid-feedback,.was-validated .custom-select:invalid~.invalid-tooltip{display:block}.form-control-file.is-invalid~.invalid-feedback,.form-control-file.is-invalid~.invalid-tooltip,.was-validated .form-control-file:invalid~.invalid-feedback,.was-validated .form-control-file:invalid~.invalid-tooltip{display:block}.form-check-input.is-invalid~.form-check-label,.was-validated .form-check-input:invalid~.form-check-label{color:#ff3c5c}.form-check-input.is-invalid~.invalid-feedback,.form-check-input.is-invalid~.invalid-tooltip,.was-validated .form-check-input:invalid~.invalid-feedback,.was-validated .form-check-input:invalid~.invalid-tooltip{display:block}.custom-control-input.is-invalid~.custom-control-label,.was-validated .custom-control-input:invalid~.custom-control-label{color:#ff3c5c}.custom-control-input.is-invalid~.custom-control-label::before,.was-validated .custom-control-input:invalid~.custom-control-label::before{border-color:#ff3c5c}.custom-control-input.is-invalid~.invalid-feedback,.custom-control-input.is-invalid~.invalid-tooltip,.was-validated .custom-control-input:invalid~.invalid-feedback,.was-validated .custom-control-input:invalid~.invalid-tooltip{display:block}.custom-control-input.is-invalid:checked~.custom-control-label::before,.was-validated .custom-control-input:invalid:checked~.custom-control-label::before{border-color:#ff6f87;background-color:#ff6f87}.custom-control-input.is-invalid:focus~.custom-control-label::before,.was-validated .custom-control-input:invalid:focus~.custom-control-label::before{-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.25);box-shadow:0 0 0 .2rem rgba(255,60,92,.25)}.custom-control-input.is-invalid:focus:not(:checked)~.custom-control-label::before,.was-validated .custom-control-input:invalid:focus:not(:checked)~.custom-control-label::before{border-color:#ff3c5c}.custom-file-input.is-invalid~.custom-file-label,.was-validated .custom-file-input:invalid~.custom-file-label{border-color:#ff3c5c}.custom-file-input.is-invalid~.invalid-feedback,.custom-file-input.is-invalid~.invalid-tooltip,.was-validated .custom-file-input:invalid~.invalid-feedback,.was-validated .custom-file-input:invalid~.invalid-tooltip{display:block}.custom-file-input.is-invalid:focus~.custom-file-label,.was-validated .custom-file-input:invalid:focus~.custom-file-label{border-color:#ff3c5c;-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.25);box-shadow:0 0 0 .2rem rgba(255,60,92,.25)}.form-inline{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row wrap;-ms-flex-flow:row wrap;flex-flow:row wrap;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center}.form-inline .form-check{width:100%}@media (min-width:576px){.form-inline label{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;margin-bottom:0}.form-inline .form-group{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-flex:0;-webkit-flex:0 0 auto;-ms-flex:0 0 auto;flex:0 0 auto;-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row wrap;-ms-flex-flow:row wrap;flex-flow:row wrap;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;margin-bottom:0}.form-inline .form-control{display:inline-block;width:auto;vertical-align:middle}.form-inline .form-control-plaintext{display:inline-block}.form-inline .custom-select,.form-inline .input-group{width:auto}.form-inline .form-check{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;width:auto;padding-left:0}.form-inline .form-check-input{position:relative;-webkit-flex-shrink:0;-ms-flex-negative:0;flex-shrink:0;margin-top:0;margin-right:.25rem;margin-left:0}.form-inline .custom-control{-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center}.form-inline .custom-control-label{margin-bottom:0}}.btn{display:inline-block;font-weight:400;color:#e4e2ff;text-align:center;vertical-align:middle;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;background-color:transparent;border:1px solid transparent;padding:.375rem .75rem;font-size:1rem;line-height:1.5;border-radius:6px;-webkit-transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}@media (prefers-reduced-motion:reduce){.btn{-webkit-transition:none;-o-transition:none;transition:none}}.btn:hover{color:#e4e2ff;text-decoration:none}.btn.focus,.btn:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 .2rem rgba(113,76,223,.25)}.btn.disabled,.btn:disabled{opacity:.65}a.btn.disabled,fieldset:disabled a.btn{pointer-events:none}.btn-primary{color:#fff;background-color:#714cdf;border-color:#714cdf}.btn-primary:hover{color:#fff;background-color:#572cd9;border-color:#5126d2}.btn-primary.focus,.btn-primary:focus{-webkit-box-shadow:0 0 0 .2rem rgba(134,103,228,.5);box-shadow:0 0 0 .2rem rgba(134,103,228,.5)}.btn-primary.disabled,.btn-primary:disabled{color:#fff;background-color:#714cdf;border-color:#714cdf}.btn-primary:not(:disabled):not(.disabled).active,.btn-primary:not(:disabled):not(.disabled):active,.show>.btn-primary.dropdown-toggle{color:#fff;background-color:#5126d2;border-color:#4d24c8}.btn-primary:not(:disabled):not(.disabled).active:focus,.btn-primary:not(:disabled):not(.disabled):active:focus,.show>.btn-primary.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(134,103,228,.5);box-shadow:0 0 0 .2rem rgba(134,103,228,.5)}.btn-secondary{color:#fff;background-color:#16a4de;border-color:#16a4de}.btn-secondary:hover{color:#fff;background-color:#138abb;border-color:#1182b0}.btn-secondary.focus,.btn-secondary:focus{-webkit-box-shadow:0 0 0 .2rem rgba(57,178,227,.5);box-shadow:0 0 0 .2rem rgba(57,178,227,.5)}.btn-secondary.disabled,.btn-secondary:disabled{color:#fff;background-color:#16a4de;border-color:#16a4de}.btn-secondary:not(:disabled):not(.disabled).active,.btn-secondary:not(:disabled):not(.disabled):active,.show>.btn-secondary.dropdown-toggle{color:#fff;background-color:#1182b0;border-color:#1079a4}.btn-secondary:not(:disabled):not(.disabled).active:focus,.btn-secondary:not(:disabled):not(.disabled):active:focus,.show>.btn-secondary.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(57,178,227,.5);box-shadow:0 0 0 .2rem rgba(57,178,227,.5)}.btn-success{color:#fff;background-color:#17b06b;border-color:#17b06b}.btn-success:hover{color:#fff;background-color:#138e56;border-color:#118350}.btn-success.focus,.btn-success:focus{-webkit-box-shadow:0 0 0 .2rem rgba(58,188,129,.5);box-shadow:0 0 0 .2rem rgba(58,188,129,.5)}.btn-success.disabled,.btn-success:disabled{color:#fff;background-color:#17b06b;border-color:#17b06b}.btn-success:not(:disabled):not(.disabled).active,.btn-success:not(:disabled):not(.disabled):active,.show>.btn-success.dropdown-toggle{color:#fff;background-color:#118350;border-color:#107849}.btn-success:not(:disabled):not(.disabled).active:focus,.btn-success:not(:disabled):not(.disabled):active:focus,.show>.btn-success.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(58,188,129,.5);box-shadow:0 0 0 .2rem rgba(58,188,129,.5)}.btn-info{color:#fff;background-color:#2983fe;border-color:#2983fe}.btn-info:hover{color:#fff;background-color:#036dfe;border-color:#0167f3}.btn-info.focus,.btn-info:focus{-webkit-box-shadow:0 0 0 .2rem rgba(73,150,254,.5);box-shadow:0 0 0 .2rem rgba(73,150,254,.5)}.btn-info.disabled,.btn-info:disabled{color:#fff;background-color:#2983fe;border-color:#2983fe}.btn-info:not(:disabled):not(.disabled).active,.btn-info:not(:disabled):not(.disabled):active,.show>.btn-info.dropdown-toggle{color:#fff;background-color:#0167f3;border-color:#0162e6}.btn-info:not(:disabled):not(.disabled).active:focus,.btn-info:not(:disabled):not(.disabled):active:focus,.show>.btn-info.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(73,150,254,.5);box-shadow:0 0 0 .2rem rgba(73,150,254,.5)}.btn-warning{color:#fff;background-color:#f97515;border-color:#f97515}.btn-warning:hover{color:#fff;background-color:#e26206;border-color:#d65d05}.btn-warning.focus,.btn-warning:focus{-webkit-box-shadow:0 0 0 .2rem rgba(250,138,56,.5);box-shadow:0 0 0 .2rem rgba(250,138,56,.5)}.btn-warning.disabled,.btn-warning:disabled{color:#fff;background-color:#f97515;border-color:#f97515}.btn-warning:not(:disabled):not(.disabled).active,.btn-warning:not(:disabled):not(.disabled):active,.show>.btn-warning.dropdown-toggle{color:#fff;background-color:#d65d05;border-color:#c95805}.btn-warning:not(:disabled):not(.disabled).active:focus,.btn-warning:not(:disabled):not(.disabled):active:focus,.show>.btn-warning.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(250,138,56,.5);box-shadow:0 0 0 .2rem rgba(250,138,56,.5)}.btn-danger{color:#fff;background-color:#ff3c5c;border-color:#ff3c5c}.btn-danger:hover{color:#fff;background-color:#ff163c;border-color:#ff0931}.btn-danger.focus,.btn-danger:focus{-webkit-box-shadow:0 0 0 .2rem rgba(255,89,116,.5);box-shadow:0 0 0 .2rem rgba(255,89,116,.5)}.btn-danger.disabled,.btn-danger:disabled{color:#fff;background-color:#ff3c5c;border-color:#ff3c5c}.btn-danger:not(:disabled):not(.disabled).active,.btn-danger:not(:disabled):not(.disabled):active,.show>.btn-danger.dropdown-toggle{color:#fff;background-color:#ff0931;border-color:#fb0029}.btn-danger:not(:disabled):not(.disabled).active:focus,.btn-danger:not(:disabled):not(.disabled):active:focus,.show>.btn-danger.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(255,89,116,.5);box-shadow:0 0 0 .2rem rgba(255,89,116,.5)}.btn-light{color:#0a0b14;background-color:#dbebfb;border-color:#dbebfb}.btn-light:hover{color:#0a0b14;background-color:#b9d8f7;border-color:#add2f6}.btn-light.focus,.btn-light:focus{-webkit-box-shadow:0 0 0 .2rem rgba(188,201,216,.5);box-shadow:0 0 0 .2rem rgba(188,201,216,.5)}.btn-light.disabled,.btn-light:disabled{color:#0a0b14;background-color:#dbebfb;border-color:#dbebfb}.btn-light:not(:disabled):not(.disabled).active,.btn-light:not(:disabled):not(.disabled):active,.show>.btn-light.dropdown-toggle{color:#0a0b14;background-color:#add2f6;border-color:#a2cbf5}.btn-light:not(:disabled):not(.disabled).active:focus,.btn-light:not(:disabled):not(.disabled):active:focus,.show>.btn-light.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(188,201,216,.5);box-shadow:0 0 0 .2rem rgba(188,201,216,.5)}.btn-dark{color:#fff;background-color:#32334a;border-color:#32334a}.btn-dark:hover{color:#fff;background-color:#232333;border-color:#1d1e2c}.btn-dark.focus,.btn-dark:focus{-webkit-box-shadow:0 0 0 .2rem rgba(81,82,101,.5);box-shadow:0 0 0 .2rem rgba(81,82,101,.5)}.btn-dark.disabled,.btn-dark:disabled{color:#fff;background-color:#32334a;border-color:#32334a}.btn-dark:not(:disabled):not(.disabled).active,.btn-dark:not(:disabled):not(.disabled):active,.show>.btn-dark.dropdown-toggle{color:#fff;background-color:#1d1e2c;border-color:#181924}.btn-dark:not(:disabled):not(.disabled).active:focus,.btn-dark:not(:disabled):not(.disabled):active:focus,.show>.btn-dark.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(81,82,101,.5);box-shadow:0 0 0 .2rem rgba(81,82,101,.5)}.btn-outline-primary{color:#714cdf;border-color:#714cdf}.btn-outline-primary:hover{color:#fff;background-color:#714cdf;border-color:#714cdf}.btn-outline-primary.focus,.btn-outline-primary:focus{-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.5);box-shadow:0 0 0 .2rem rgba(113,76,223,.5)}.btn-outline-primary.disabled,.btn-outline-primary:disabled{color:#714cdf;background-color:transparent}.btn-outline-primary:not(:disabled):not(.disabled).active,.btn-outline-primary:not(:disabled):not(.disabled):active,.show>.btn-outline-primary.dropdown-toggle{color:#fff;background-color:#714cdf;border-color:#714cdf}.btn-outline-primary:not(:disabled):not(.disabled).active:focus,.btn-outline-primary:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-primary.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.5);box-shadow:0 0 0 .2rem rgba(113,76,223,.5)}.btn-outline-secondary{color:#16a4de;border-color:#16a4de}.btn-outline-secondary:hover{color:#fff;background-color:#16a4de;border-color:#16a4de}.btn-outline-secondary.focus,.btn-outline-secondary:focus{-webkit-box-shadow:0 0 0 .2rem rgba(22,164,222,.5);box-shadow:0 0 0 .2rem rgba(22,164,222,.5)}.btn-outline-secondary.disabled,.btn-outline-secondary:disabled{color:#16a4de;background-color:transparent}.btn-outline-secondary:not(:disabled):not(.disabled).active,.btn-outline-secondary:not(:disabled):not(.disabled):active,.show>.btn-outline-secondary.dropdown-toggle{color:#fff;background-color:#16a4de;border-color:#16a4de}.btn-outline-secondary:not(:disabled):not(.disabled).active:focus,.btn-outline-secondary:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-secondary.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(22,164,222,.5);box-shadow:0 0 0 .2rem rgba(22,164,222,.5)}.btn-outline-success{color:#17b06b;border-color:#17b06b}.btn-outline-success:hover{color:#fff;background-color:#17b06b;border-color:#17b06b}.btn-outline-success.focus,.btn-outline-success:focus{-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.5);box-shadow:0 0 0 .2rem rgba(23,176,107,.5)}.btn-outline-success.disabled,.btn-outline-success:disabled{color:#17b06b;background-color:transparent}.btn-outline-success:not(:disabled):not(.disabled).active,.btn-outline-success:not(:disabled):not(.disabled):active,.show>.btn-outline-success.dropdown-toggle{color:#fff;background-color:#17b06b;border-color:#17b06b}.btn-outline-success:not(:disabled):not(.disabled).active:focus,.btn-outline-success:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-success.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.5);box-shadow:0 0 0 .2rem rgba(23,176,107,.5)}.btn-outline-info{color:#2983fe;border-color:#2983fe}.btn-outline-info:hover{color:#fff;background-color:#2983fe;border-color:#2983fe}.btn-outline-info.focus,.btn-outline-info:focus{-webkit-box-shadow:0 0 0 .2rem rgba(41,131,254,.5);box-shadow:0 0 0 .2rem rgba(41,131,254,.5)}.btn-outline-info.disabled,.btn-outline-info:disabled{color:#2983fe;background-color:transparent}.btn-outline-info:not(:disabled):not(.disabled).active,.btn-outline-info:not(:disabled):not(.disabled):active,.show>.btn-outline-info.dropdown-toggle{color:#fff;background-color:#2983fe;border-color:#2983fe}.btn-outline-info:not(:disabled):not(.disabled).active:focus,.btn-outline-info:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-info.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(41,131,254,.5);box-shadow:0 0 0 .2rem rgba(41,131,254,.5)}.btn-outline-warning{color:#f97515;border-color:#f97515}.btn-outline-warning:hover{color:#fff;background-color:#f97515;border-color:#f97515}.btn-outline-warning.focus,.btn-outline-warning:focus{-webkit-box-shadow:0 0 0 .2rem rgba(249,117,21,.5);box-shadow:0 0 0 .2rem rgba(249,117,21,.5)}.btn-outline-warning.disabled,.btn-outline-warning:disabled{color:#f97515;background-color:transparent}.btn-outline-warning:not(:disabled):not(.disabled).active,.btn-outline-warning:not(:disabled):not(.disabled):active,.show>.btn-outline-warning.dropdown-toggle{color:#fff;background-color:#f97515;border-color:#f97515}.btn-outline-warning:not(:disabled):not(.disabled).active:focus,.btn-outline-warning:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-warning.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(249,117,21,.5);box-shadow:0 0 0 .2rem rgba(249,117,21,.5)}.btn-outline-danger{color:#ff3c5c;border-color:#ff3c5c}.btn-outline-danger:hover{color:#fff;background-color:#ff3c5c;border-color:#ff3c5c}.btn-outline-danger.focus,.btn-outline-danger:focus{-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.5);box-shadow:0 0 0 .2rem rgba(255,60,92,.5)}.btn-outline-danger.disabled,.btn-outline-danger:disabled{color:#ff3c5c;background-color:transparent}.btn-outline-danger:not(:disabled):not(.disabled).active,.btn-outline-danger:not(:disabled):not(.disabled):active,.show>.btn-outline-danger.dropdown-toggle{color:#fff;background-color:#ff3c5c;border-color:#ff3c5c}.btn-outline-danger:not(:disabled):not(.disabled).active:focus,.btn-outline-danger:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-danger.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.5);box-shadow:0 0 0 .2rem rgba(255,60,92,.5)}.btn-outline-light{color:#dbebfb;border-color:#dbebfb}.btn-outline-light:hover{color:#0a0b14;background-color:#dbebfb;border-color:#dbebfb}.btn-outline-light.focus,.btn-outline-light:focus{-webkit-box-shadow:0 0 0 .2rem rgba(219,235,251,.5);box-shadow:0 0 0 .2rem rgba(219,235,251,.5)}.btn-outline-light.disabled,.btn-outline-light:disabled{color:#dbebfb;background-color:transparent}.btn-outline-light:not(:disabled):not(.disabled).active,.btn-outline-light:not(:disabled):not(.disabled):active,.show>.btn-outline-light.dropdown-toggle{color:#0a0b14;background-color:#dbebfb;border-color:#dbebfb}.btn-outline-light:not(:disabled):not(.disabled).active:focus,.btn-outline-light:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-light.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(219,235,251,.5);box-shadow:0 0 0 .2rem rgba(219,235,251,.5)}.btn-outline-dark{color:#32334a;border-color:#32334a}.btn-outline-dark:hover{color:#fff;background-color:#32334a;border-color:#32334a}.btn-outline-dark.focus,.btn-outline-dark:focus{-webkit-box-shadow:0 0 0 .2rem rgba(50,51,74,.5);box-shadow:0 0 0 .2rem rgba(50,51,74,.5)}.btn-outline-dark.disabled,.btn-outline-dark:disabled{color:#32334a;background-color:transparent}.btn-outline-dark:not(:disabled):not(.disabled).active,.btn-outline-dark:not(:disabled):not(.disabled):active,.show>.btn-outline-dark.dropdown-toggle{color:#fff;background-color:#32334a;border-color:#32334a}.btn-outline-dark:not(:disabled):not(.disabled).active:focus,.btn-outline-dark:not(:disabled):not(.disabled):active:focus,.show>.btn-outline-dark.dropdown-toggle:focus{-webkit-box-shadow:0 0 0 .2rem rgba(50,51,74,.5);box-shadow:0 0 0 .2rem rgba(50,51,74,.5)}.btn-link{font-weight:400;color:#714cdf;text-decoration:none}.btn-link:hover{color:#4922bd;text-decoration:underline}.btn-link.focus,.btn-link:focus{text-decoration:underline;-webkit-box-shadow:none;box-shadow:none}.btn-link.disabled,.btn-link:disabled{color:#1d1e2f;pointer-events:none}.btn-group-lg>.btn,.btn-lg{padding:.5rem 1rem;font-size:1.25rem;line-height:1.5;border-radius:6px}.btn-group-sm>.btn,.btn-sm{padding:.25rem .5rem;font-size:.875rem;line-height:1.5;border-radius:.2rem}.btn-block{display:block;width:100%}.btn-block+.btn-block{margin-top:.5rem}input[type=button].btn-block,input[type=reset].btn-block,input[type=submit].btn-block{width:100%}.fade{-webkit-transition:opacity .15s linear;-o-transition:opacity .15s linear;transition:opacity .15s linear}@media (prefers-reduced-motion:reduce){.fade{-webkit-transition:none;-o-transition:none;transition:none}}.fade:not(.show){opacity:0}.collapse:not(.show){display:none}.collapsing{position:relative;height:0;overflow:hidden;-webkit-transition:height .35s ease;-o-transition:height .35s ease;transition:height .35s ease}@media (prefers-reduced-motion:reduce){.collapsing{-webkit-transition:none;-o-transition:none;transition:none}}.dropdown,.dropleft,.dropright,.dropup{position:relative}.dropdown-toggle{white-space:nowrap}.dropdown-toggle::after{display:inline-block;margin-left:.255em;vertical-align:.255em;content:"";border-top:.3em solid;border-right:.3em solid transparent;border-bottom:0;border-left:.3em solid transparent}.dropdown-toggle:empty::after{margin-left:0}.dropdown-menu{position:absolute;top:100%;left:0;z-index:1000;display:none;float:left;min-width:10rem;padding:.5rem 0;margin:.125rem 0 0;font-size:1rem;color:#e4e2ff;text-align:left;list-style:none;background-color:#32334a;background-clip:padding-box;border:1px solid rgba(0,0,0,.15);border-radius:6px}.dropdown-menu-left{right:auto;left:0}.dropdown-menu-right{right:0;left:auto}@media (min-width:576px){.dropdown-menu-sm-left{right:auto;left:0}.dropdown-menu-sm-right{right:0;left:auto}}@media (min-width:768px){.dropdown-menu-md-left{right:auto;left:0}.dropdown-menu-md-right{right:0;left:auto}}@media (min-width:992px){.dropdown-menu-lg-left{right:auto;left:0}.dropdown-menu-lg-right{right:0;left:auto}}@media (min-width:1200px){.dropdown-menu-xl-left{right:auto;left:0}.dropdown-menu-xl-right{right:0;left:auto}}.dropup .dropdown-menu{top:auto;bottom:100%;margin-top:0;margin-bottom:.125rem}.dropup .dropdown-toggle::after{display:inline-block;margin-left:.255em;vertical-align:.255em;content:"";border-top:0;border-right:.3em solid transparent;border-bottom:.3em solid;border-left:.3em solid transparent}.dropup .dropdown-toggle:empty::after{margin-left:0}.dropright .dropdown-menu{top:0;right:auto;left:100%;margin-top:0;margin-left:.125rem}.dropright .dropdown-toggle::after{display:inline-block;margin-left:.255em;vertical-align:.255em;content:"";border-top:.3em solid transparent;border-right:0;border-bottom:.3em solid transparent;border-left:.3em solid}.dropright .dropdown-toggle:empty::after{margin-left:0}.dropright .dropdown-toggle::after{vertical-align:0}.dropleft .dropdown-menu{top:0;right:100%;left:auto;margin-top:0;margin-right:.125rem}.dropleft .dropdown-toggle::after{display:inline-block;margin-left:.255em;vertical-align:.255em;content:""}.dropleft .dropdown-toggle::after{display:none}.dropleft .dropdown-toggle::before{display:inline-block;margin-right:.255em;vertical-align:.255em;content:"";border-top:.3em solid transparent;border-right:.3em solid;border-bottom:.3em solid transparent}.dropleft .dropdown-toggle:empty::after{margin-left:0}.dropleft .dropdown-toggle::before{vertical-align:0}.dropdown-menu[x-placement^=bottom],.dropdown-menu[x-placement^=left],.dropdown-menu[x-placement^=right],.dropdown-menu[x-placement^=top]{right:auto;bottom:auto}.dropdown-divider{height:0;margin:.5rem 0;overflow:hidden;border-top:1px solid #282a38}.dropdown-item{display:block;width:100%;padding:.25rem 1.5rem;clear:both;font-weight:400;color:#0a0b14;text-align:inherit;white-space:nowrap;background-color:transparent;border:0}.dropdown-item:focus,.dropdown-item:hover{color:#020203;text-decoration:none;background-color:#2d2e3f}.dropdown-item.active,.dropdown-item:active{color:#32334a;text-decoration:none;background-color:#714cdf}.dropdown-item.disabled,.dropdown-item:disabled{color:#1d1e2f;pointer-events:none;background-color:transparent}.dropdown-menu.show{display:block}.dropdown-header{display:block;padding:.5rem 1.5rem;margin-bottom:0;font-size:.875rem;color:#1d1e2f;white-space:nowrap}.dropdown-item-text{display:block;padding:.25rem 1.5rem;color:#0a0b14}.btn-group,.btn-group-vertical{position:relative;display:-webkit-inline-box;display:-webkit-inline-flex;display:-ms-inline-flexbox;display:inline-flex;vertical-align:middle}.btn-group-vertical>.btn,.btn-group>.btn{position:relative;-webkit-box-flex:1;-webkit-flex:1 1 auto;-ms-flex:1 1 auto;flex:1 1 auto}.btn-group-vertical>.btn:hover,.btn-group>.btn:hover{z-index:1}.btn-group-vertical>.btn.active,.btn-group-vertical>.btn:active,.btn-group-vertical>.btn:focus,.btn-group>.btn.active,.btn-group>.btn:active,.btn-group>.btn:focus{z-index:1}.btn-toolbar{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.btn-toolbar .input-group{width:auto}.btn-group>.btn-group:not(:first-child),.btn-group>.btn:not(:first-child){margin-left:-1px}.btn-group>.btn-group:not(:last-child)>.btn,.btn-group>.btn:not(:last-child):not(.dropdown-toggle){border-top-right-radius:0;border-bottom-right-radius:0}.btn-group>.btn-group:not(:first-child)>.btn,.btn-group>.btn:not(:first-child){border-top-left-radius:0;border-bottom-left-radius:0}.dropdown-toggle-split{padding-right:.5625rem;padding-left:.5625rem}.dropdown-toggle-split::after,.dropright .dropdown-toggle-split::after,.dropup .dropdown-toggle-split::after{margin-left:0}.dropleft .dropdown-toggle-split::before{margin-right:0}.btn-group-sm>.btn+.dropdown-toggle-split,.btn-sm+.dropdown-toggle-split{padding-right:.375rem;padding-left:.375rem}.btn-group-lg>.btn+.dropdown-toggle-split,.btn-lg+.dropdown-toggle-split{padding-right:.75rem;padding-left:.75rem}.btn-group-vertical{-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;-webkit-box-align:start;-webkit-align-items:flex-start;-ms-flex-align:start;align-items:flex-start;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center}.btn-group-vertical>.btn,.btn-group-vertical>.btn-group{width:100%}.btn-group-vertical>.btn-group:not(:first-child),.btn-group-vertical>.btn:not(:first-child){margin-top:-1px}.btn-group-vertical>.btn-group:not(:last-child)>.btn,.btn-group-vertical>.btn:not(:last-child):not(.dropdown-toggle){border-bottom-right-radius:0;border-bottom-left-radius:0}.btn-group-vertical>.btn-group:not(:first-child)>.btn,.btn-group-vertical>.btn:not(:first-child){border-top-left-radius:0;border-top-right-radius:0}.btn-group-toggle>.btn,.btn-group-toggle>.btn-group>.btn{margin-bottom:0}.btn-group-toggle>.btn input[type=checkbox],.btn-group-toggle>.btn input[type=radio],.btn-group-toggle>.btn-group>.btn input[type=checkbox],.btn-group-toggle>.btn-group>.btn input[type=radio]{position:absolute;clip:rect(0,0,0,0);pointer-events:none}.input-group{position:relative;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;-webkit-box-align:stretch;-webkit-align-items:stretch;-ms-flex-align:stretch;align-items:stretch;width:100%}.input-group>.custom-file,.input-group>.custom-select,.input-group>.form-control,.input-group>.form-control-plaintext{position:relative;-webkit-box-flex:1;-webkit-flex:1 1 auto;-ms-flex:1 1 auto;flex:1 1 auto;width:1%;margin-bottom:0}.input-group>.custom-file+.custom-file,.input-group>.custom-file+.custom-select,.input-group>.custom-file+.form-control,.input-group>.custom-select+.custom-file,.input-group>.custom-select+.custom-select,.input-group>.custom-select+.form-control,.input-group>.form-control+.custom-file,.input-group>.form-control+.custom-select,.input-group>.form-control+.form-control,.input-group>.form-control-plaintext+.custom-file,.input-group>.form-control-plaintext+.custom-select,.input-group>.form-control-plaintext+.form-control{margin-left:-1px}.input-group>.custom-file .custom-file-input:focus~.custom-file-label,.input-group>.custom-select:focus,.input-group>.form-control:focus{z-index:3}.input-group>.custom-file .custom-file-input:focus{z-index:4}.input-group>.custom-select:not(:last-child),.input-group>.form-control:not(:last-child){border-top-right-radius:0;border-bottom-right-radius:0}.input-group>.custom-select:not(:first-child),.input-group>.form-control:not(:first-child){border-top-left-radius:0;border-bottom-left-radius:0}.input-group>.custom-file{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center}.input-group>.custom-file:not(:last-child) .custom-file-label,.input-group>.custom-file:not(:last-child) .custom-file-label::after{border-top-right-radius:0;border-bottom-right-radius:0}.input-group>.custom-file:not(:first-child) .custom-file-label{border-top-left-radius:0;border-bottom-left-radius:0}.input-group-append,.input-group-prepend{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex}.input-group-append .btn,.input-group-prepend .btn{position:relative;z-index:2}.input-group-append .btn:focus,.input-group-prepend .btn:focus{z-index:3}.input-group-append .btn+.btn,.input-group-append .btn+.input-group-text,.input-group-append .input-group-text+.btn,.input-group-append .input-group-text+.input-group-text,.input-group-prepend .btn+.btn,.input-group-prepend .btn+.input-group-text,.input-group-prepend .input-group-text+.btn,.input-group-prepend .input-group-text+.input-group-text{margin-left:-1px}.input-group-prepend{margin-right:-1px}.input-group-append{margin-left:-1px}.input-group-text{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;padding:.375rem .75rem;margin-bottom:0;font-size:1rem;font-weight:400;line-height:1.5;color:#adabc6;text-align:center;white-space:nowrap;background-color:#282a38;border:1px solid #11111d;border-radius:6px}.input-group-text input[type=checkbox],.input-group-text input[type=radio]{margin-top:0}.input-group-lg>.custom-select,.input-group-lg>.form-control:not(textarea){height:calc(1.5em + 1rem + 2px)}.input-group-lg>.custom-select,.input-group-lg>.form-control,.input-group-lg>.input-group-append>.btn,.input-group-lg>.input-group-append>.input-group-text,.input-group-lg>.input-group-prepend>.btn,.input-group-lg>.input-group-prepend>.input-group-text{padding:.5rem 1rem;font-size:1.25rem;line-height:1.5;border-radius:6px}.input-group-sm>.custom-select,.input-group-sm>.form-control:not(textarea){height:calc(1.5em + .5rem + 2px)}.input-group-sm>.custom-select,.input-group-sm>.form-control,.input-group-sm>.input-group-append>.btn,.input-group-sm>.input-group-append>.input-group-text,.input-group-sm>.input-group-prepend>.btn,.input-group-sm>.input-group-prepend>.input-group-text{padding:.25rem .5rem;font-size:.875rem;line-height:1.5;border-radius:.2rem}.input-group-lg>.custom-select,.input-group-sm>.custom-select{padding-right:1.75rem}.input-group>.input-group-append:last-child>.btn:not(:last-child):not(.dropdown-toggle),.input-group>.input-group-append:last-child>.input-group-text:not(:last-child),.input-group>.input-group-append:not(:last-child)>.btn,.input-group>.input-group-append:not(:last-child)>.input-group-text,.input-group>.input-group-prepend>.btn,.input-group>.input-group-prepend>.input-group-text{border-top-right-radius:0;border-bottom-right-radius:0}.input-group>.input-group-append>.btn,.input-group>.input-group-append>.input-group-text,.input-group>.input-group-prepend:first-child>.btn:not(:first-child),.input-group>.input-group-prepend:first-child>.input-group-text:not(:first-child),.input-group>.input-group-prepend:not(:first-child)>.btn,.input-group>.input-group-prepend:not(:first-child)>.input-group-text{border-top-left-radius:0;border-bottom-left-radius:0}.custom-control{position:relative;display:block;min-height:1.5rem;padding-left:1.5rem}.custom-control-inline{display:-webkit-inline-box;display:-webkit-inline-flex;display:-ms-inline-flexbox;display:inline-flex;margin-right:1rem}.custom-control-input{position:absolute;z-index:-1;opacity:0}.custom-control-input:checked~.custom-control-label::before{color:#32334a;border-color:#714cdf;background-color:#714cdf}.custom-control-input:focus~.custom-control-label::before{-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 .2rem rgba(113,76,223,.25)}.custom-control-input:focus:not(:checked)~.custom-control-label::before{border-color:#c7b8f2}.custom-control-input:not(:disabled):active~.custom-control-label::before{color:#32334a;background-color:#e9e3fa;border-color:#e9e3fa}.custom-control-input:disabled~.custom-control-label{color:#1d1e2f}.custom-control-input:disabled~.custom-control-label::before{background-color:#282a38}.custom-control-label{position:relative;margin-bottom:0;vertical-align:top}.custom-control-label::before{position:absolute;top:.25rem;left:-1.5rem;display:block;width:1rem;height:1rem;pointer-events:none;content:"";background-color:#151623;border:#1c1d2c solid 1px}.custom-control-label::after{position:absolute;top:.25rem;left:-1.5rem;display:block;width:1rem;height:1rem;content:"";background:no-repeat 50%/50% 50%}.custom-checkbox .custom-control-label::before{border-radius:6px}.custom-checkbox .custom-control-input:checked~.custom-control-label::after{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2332334a' d='M6.564.75l-3.59 3.612-1.538-1.55L0 4.26 2.974 7.25 8 2.193z'/%3e%3c/svg%3e")}.custom-checkbox .custom-control-input:indeterminate~.custom-control-label::before{border-color:#714cdf;background-color:#714cdf}.custom-checkbox .custom-control-input:indeterminate~.custom-control-label::after{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 4'%3e%3cpath stroke='%2332334a' d='M0 2h4'/%3e%3c/svg%3e")}.custom-checkbox .custom-control-input:disabled:checked~.custom-control-label::before{background-color:rgba(113,76,223,.5)}.custom-checkbox .custom-control-input:disabled:indeterminate~.custom-control-label::before{background-color:rgba(113,76,223,.5)}.custom-radio .custom-control-label::before{border-radius:50%}.custom-radio .custom-control-input:checked~.custom-control-label::after{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='3' fill='%2332334a'/%3e%3c/svg%3e")}.custom-radio .custom-control-input:disabled:checked~.custom-control-label::before{background-color:rgba(113,76,223,.5)}.custom-switch{padding-left:2.25rem}.custom-switch .custom-control-label::before{left:-2.25rem;width:1.75rem;pointer-events:all;border-radius:.5rem}.custom-switch .custom-control-label::after{top:calc(.25rem + 2px);left:calc(-2.25rem + 2px);width:calc(1rem - 4px);height:calc(1rem - 4px);background-color:#1c1d2c;border-radius:.5rem;-webkit-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-transform .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-transform .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-o-transform .15s ease-in-out;transition:transform .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:transform .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-transform .15s ease-in-out,-o-transform .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}@media (prefers-reduced-motion:reduce){.custom-switch .custom-control-label::after{-webkit-transition:none;-o-transition:none;transition:none}}.custom-switch .custom-control-input:checked~.custom-control-label::after{background-color:#151623;-webkit-transform:translateX(.75rem);-o-transform:translateX(.75rem);transform:translateX(.75rem)}.custom-switch .custom-control-input:disabled:checked~.custom-control-label::before{background-color:rgba(113,76,223,.5)}.custom-select{display:inline-block;width:100%;height:calc(1.5em + .75rem + 2px);padding:.375rem 1.75rem .375rem .75rem;font-size:1rem;font-weight:400;line-height:1.5;color:#adabc6;vertical-align:middle;background:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'%3e%3cpath fill='%2311111d' d='M2 0L0 2h4zm0 5L0 3h4z'/%3e%3c/svg%3e") no-repeat right .75rem center/8px 10px;background-color:#32334a;border:1px solid #11111d;border-radius:6px;-webkit-appearance:none;-moz-appearance:none;appearance:none}.custom-select:focus{border-color:#c7b8f2;outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 .2rem rgba(113,76,223,.25)}.custom-select:focus::-ms-value{color:#adabc6;background-color:#28293e}.custom-select[multiple],.custom-select[size]:not([size="1"]){height:auto;padding-right:.75rem;background-image:none}.custom-select:disabled{color:#1d1e2f;background-color:#282a38}.custom-select::-ms-expand{display:none}.custom-select-sm{height:calc(1.5em + .5rem + 2px);padding-top:.25rem;padding-bottom:.25rem;padding-left:.5rem;font-size:.875rem}.custom-select-lg{height:calc(1.5em + 1rem + 2px);padding-top:.5rem;padding-bottom:.5rem;padding-left:1rem;font-size:1.25rem}.custom-file{position:relative;display:inline-block;width:100%;height:calc(1.5em + .75rem + 2px);margin-bottom:0}.custom-file-input{position:relative;z-index:2;width:100%;height:calc(1.5em + .75rem + 2px);margin:0;opacity:0}.custom-file-input:focus~.custom-file-label{border-color:#c7b8f2;-webkit-box-shadow:0 0 0 .075rem #32334a,0 0 0 .2rem theme-color("primary");box-shadow:0 0 0 .075rem #32334a,0 0 0 .2rem theme-color("primary")}.custom-file-input:disabled~.custom-file-label{background-color:#282a38}.custom-file-input:lang(en)~.custom-file-label::after{content:"Browse"}.custom-file-input~.custom-file-label[data-browse]::after{content:attr(data-browse)}.custom-file-label{position:absolute;top:0;right:0;left:0;z-index:1;height:calc(1.5em + .75rem + 2px);padding:.375rem .75rem;font-weight:400;line-height:1.5;color:#adabc6;background-color:#28293e;border:1px solid #11111d;border-radius:6px}.custom-file-label::after{position:absolute;top:0;right:0;bottom:0;z-index:3;display:block;height:calc(1.5em + .75rem);padding:.375rem .75rem;line-height:1.5;color:#adabc6;content:"Browse";background-color:#282a38;border-left:inherit;border-radius:0 6px 6px 0}.custom-range{width:100%;height:calc(1rem + .4rem);padding:0;background-color:transparent;-webkit-appearance:none;-moz-appearance:none;appearance:none}.custom-range:focus{outline:0}.custom-range:focus::-webkit-slider-thumb{-webkit-box-shadow:0 0 0 1px #0c0d16,0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 1px #0c0d16,0 0 0 .2rem rgba(113,76,223,.25)}.custom-range:focus::-moz-range-thumb{box-shadow:0 0 0 1px #0c0d16,0 0 0 .2rem rgba(113,76,223,.25)}.custom-range:focus::-ms-thumb{box-shadow:0 0 0 1px #0c0d16,0 0 0 .2rem rgba(113,76,223,.25)}.custom-range::-moz-focus-outer{border:0}.custom-range::-webkit-slider-thumb{width:1rem;height:1rem;margin-top:-.25rem;background-color:#714cdf;border:0;border-radius:1rem;-webkit-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-webkit-appearance:none;appearance:none}@media (prefers-reduced-motion:reduce){.custom-range::-webkit-slider-thumb{-webkit-transition:none;-o-transition:none;transition:none}}.custom-range::-webkit-slider-thumb:active{background-color:#e9e3fa}.custom-range::-webkit-slider-runnable-track{width:100%;height:.5rem;color:transparent;cursor:pointer;background-color:#28293e;border-color:transparent;border-radius:1rem}.custom-range::-moz-range-thumb{width:1rem;height:1rem;background-color:#714cdf;border:0;border-radius:1rem;-webkit-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-moz-appearance:none;appearance:none}@media (prefers-reduced-motion:reduce){.custom-range::-moz-range-thumb{-webkit-transition:none;-o-transition:none;transition:none}}.custom-range::-moz-range-thumb:active{background-color:#e9e3fa}.custom-range::-moz-range-track{width:100%;height:.5rem;color:transparent;cursor:pointer;background-color:#28293e;border-color:transparent;border-radius:1rem}.custom-range::-ms-thumb{width:1rem;height:1rem;margin-top:0;margin-right:.2rem;margin-left:.2rem;background-color:#714cdf;border:0;border-radius:1rem;-webkit-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;appearance:none}@media (prefers-reduced-motion:reduce){.custom-range::-ms-thumb{-webkit-transition:none;-o-transition:none;transition:none}}.custom-range::-ms-thumb:active{background-color:#e9e3fa}.custom-range::-ms-track{width:100%;height:.5rem;color:transparent;cursor:pointer;background-color:transparent;border-color:transparent;border-width:.5rem}.custom-range::-ms-fill-lower{background-color:#28293e;border-radius:1rem}.custom-range::-ms-fill-upper{margin-right:15px;background-color:#28293e;border-radius:1rem}.custom-range:disabled::-webkit-slider-thumb{background-color:#1c1d2c}.custom-range:disabled::-webkit-slider-runnable-track{cursor:default}.custom-range:disabled::-moz-range-thumb{background-color:#1c1d2c}.custom-range:disabled::-moz-range-track{cursor:default}.custom-range:disabled::-ms-thumb{background-color:#1c1d2c}.custom-control-label::before,.custom-file-label,.custom-select{-webkit-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}@media (prefers-reduced-motion:reduce){.custom-control-label::before,.custom-file-label,.custom-select{-webkit-transition:none;-o-transition:none;transition:none}}.nav{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;padding-left:0;margin-bottom:0;list-style:none}.nav-link{display:block;padding:.5rem 1rem}.nav-link:focus,.nav-link:hover{text-decoration:none}.nav-link.disabled{color:#1d1e2f;pointer-events:none;cursor:default}.nav-tabs{border-bottom:1px solid #151623}.nav-tabs .nav-item{margin-bottom:-1px}.nav-tabs .nav-link{border:1px solid transparent;border-top-left-radius:6px;border-top-right-radius:6px}.nav-tabs .nav-link:focus,.nav-tabs .nav-link:hover{border-color:#282a38 #282a38 #151623}.nav-tabs .nav-link.disabled{color:#1d1e2f;background-color:transparent;border-color:transparent}.nav-tabs .nav-item.show .nav-link,.nav-tabs .nav-link.active{color:#e4e2ff;background-color:#0c0d16;border-color:#151623}.nav-tabs .dropdown-menu{margin-top:-1px;border-top-left-radius:0;border-top-right-radius:0}.nav-pills .nav-link{border-radius:6px}.nav-pills .nav-link.active,.nav-pills .show>.nav-link{color:#32334a;background-color:#714cdf}.nav-fill .nav-item{-webkit-box-flex:1;-webkit-flex:1 1 auto;-ms-flex:1 1 auto;flex:1 1 auto;text-align:center}.nav-justified .nav-item{-webkit-flex-basis:0;-ms-flex-preferred-size:0;flex-basis:0;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;text-align:center}.tab-content>.tab-pane{display:none}.tab-content>.active{display:block}.navbar{position:relative;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:justify;-webkit-justify-content:space-between;-ms-flex-pack:justify;justify-content:space-between;padding:.5rem 1rem}.navbar>.container,.navbar>.container-fluid{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:justify;-webkit-justify-content:space-between;-ms-flex-pack:justify;justify-content:space-between}.navbar-brand{display:inline-block;padding-top:.3125rem;padding-bottom:.3125rem;margin-right:1rem;font-size:1.25rem;line-height:inherit;white-space:nowrap}.navbar-brand:focus,.navbar-brand:hover{text-decoration:none}.navbar-nav{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;padding-left:0;margin-bottom:0;list-style:none}.navbar-nav .nav-link{padding-right:0;padding-left:0}.navbar-nav .dropdown-menu{position:static;float:none}.navbar-text{display:inline-block;padding-top:.5rem;padding-bottom:.5rem}.navbar-collapse{-webkit-flex-basis:100%;-ms-flex-preferred-size:100%;flex-basis:100%;-webkit-box-flex:1;-webkit-flex-grow:1;-ms-flex-positive:1;flex-grow:1;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center}.navbar-toggler{padding:.25rem .75rem;font-size:1.25rem;line-height:1;background-color:transparent;border:1px solid transparent;border-radius:6px}.navbar-toggler:focus,.navbar-toggler:hover{text-decoration:none}.navbar-toggler-icon{display:inline-block;width:1.5em;height:1.5em;vertical-align:middle;content:"";background:no-repeat center center;-webkit-background-size:100% 100%;background-size:100% 100%}@media (max-width:575.98px){.navbar-expand-sm>.container,.navbar-expand-sm>.container-fluid{padding-right:0;padding-left:0}}@media (min-width:576px){.navbar-expand-sm{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row nowrap;-ms-flex-flow:row nowrap;flex-flow:row nowrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.navbar-expand-sm .navbar-nav{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.navbar-expand-sm .navbar-nav .dropdown-menu{position:absolute}.navbar-expand-sm .navbar-nav .nav-link{padding-right:.5rem;padding-left:.5rem}.navbar-expand-sm>.container,.navbar-expand-sm>.container-fluid{-webkit-flex-wrap:nowrap;-ms-flex-wrap:nowrap;flex-wrap:nowrap}.navbar-expand-sm .navbar-collapse{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important;-webkit-flex-basis:auto;-ms-flex-preferred-size:auto;flex-basis:auto}.navbar-expand-sm .navbar-toggler{display:none}}@media (max-width:767.98px){.navbar-expand-md>.container,.navbar-expand-md>.container-fluid{padding-right:0;padding-left:0}}@media (min-width:768px){.navbar-expand-md{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row nowrap;-ms-flex-flow:row nowrap;flex-flow:row nowrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.navbar-expand-md .navbar-nav{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.navbar-expand-md .navbar-nav .dropdown-menu{position:absolute}.navbar-expand-md .navbar-nav .nav-link{padding-right:.5rem;padding-left:.5rem}.navbar-expand-md>.container,.navbar-expand-md>.container-fluid{-webkit-flex-wrap:nowrap;-ms-flex-wrap:nowrap;flex-wrap:nowrap}.navbar-expand-md .navbar-collapse{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important;-webkit-flex-basis:auto;-ms-flex-preferred-size:auto;flex-basis:auto}.navbar-expand-md .navbar-toggler{display:none}}@media (max-width:991.98px){.navbar-expand-lg>.container,.navbar-expand-lg>.container-fluid{padding-right:0;padding-left:0}}@media (min-width:992px){.navbar-expand-lg{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row nowrap;-ms-flex-flow:row nowrap;flex-flow:row nowrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.navbar-expand-lg .navbar-nav{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.navbar-expand-lg .navbar-nav .dropdown-menu{position:absolute}.navbar-expand-lg .navbar-nav .nav-link{padding-right:.5rem;padding-left:.5rem}.navbar-expand-lg>.container,.navbar-expand-lg>.container-fluid{-webkit-flex-wrap:nowrap;-ms-flex-wrap:nowrap;flex-wrap:nowrap}.navbar-expand-lg .navbar-collapse{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important;-webkit-flex-basis:auto;-ms-flex-preferred-size:auto;flex-basis:auto}.navbar-expand-lg .navbar-toggler{display:none}}@media (max-width:1199.98px){.navbar-expand-xl>.container,.navbar-expand-xl>.container-fluid{padding-right:0;padding-left:0}}@media (min-width:1200px){.navbar-expand-xl{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row nowrap;-ms-flex-flow:row nowrap;flex-flow:row nowrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.navbar-expand-xl .navbar-nav{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.navbar-expand-xl .navbar-nav .dropdown-menu{position:absolute}.navbar-expand-xl .navbar-nav .nav-link{padding-right:.5rem;padding-left:.5rem}.navbar-expand-xl>.container,.navbar-expand-xl>.container-fluid{-webkit-flex-wrap:nowrap;-ms-flex-wrap:nowrap;flex-wrap:nowrap}.navbar-expand-xl .navbar-collapse{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important;-webkit-flex-basis:auto;-ms-flex-preferred-size:auto;flex-basis:auto}.navbar-expand-xl .navbar-toggler{display:none}}.navbar-expand{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row nowrap;-ms-flex-flow:row nowrap;flex-flow:row nowrap;-webkit-box-pack:start;-webkit-justify-content:flex-start;-ms-flex-pack:start;justify-content:flex-start}.navbar-expand>.container,.navbar-expand>.container-fluid{padding-right:0;padding-left:0}.navbar-expand .navbar-nav{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.navbar-expand .navbar-nav .dropdown-menu{position:absolute}.navbar-expand .navbar-nav .nav-link{padding-right:.5rem;padding-left:.5rem}.navbar-expand>.container,.navbar-expand>.container-fluid{-webkit-flex-wrap:nowrap;-ms-flex-wrap:nowrap;flex-wrap:nowrap}.navbar-expand .navbar-collapse{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important;-webkit-flex-basis:auto;-ms-flex-preferred-size:auto;flex-basis:auto}.navbar-expand .navbar-toggler{display:none}.navbar-light .navbar-brand{color:rgba(0,0,0,.9)}.navbar-light .navbar-brand:focus,.navbar-light .navbar-brand:hover{color:rgba(0,0,0,.9)}.navbar-light .navbar-nav .nav-link{color:rgba(0,0,0,.5)}.navbar-light .navbar-nav .nav-link:focus,.navbar-light .navbar-nav .nav-link:hover{color:rgba(0,0,0,.7)}.navbar-light .navbar-nav .nav-link.disabled{color:rgba(0,0,0,.3)}.navbar-light .navbar-nav .active>.nav-link,.navbar-light .navbar-nav .nav-link.active,.navbar-light .navbar-nav .nav-link.show,.navbar-light .navbar-nav .show>.nav-link{color:rgba(0,0,0,.9)}.navbar-light .navbar-toggler{color:rgba(0,0,0,.5);border-color:rgba(0,0,0,.1)}.navbar-light .navbar-toggler-icon{background-image:url("data:image/svg+xml,%3csvg viewBox='0 0 30 30' xmlns='http://www.w3.org/2000/svg'%3e%3cpath stroke='rgba(0, 0, 0, 0.5)' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e")}.navbar-light .navbar-text{color:rgba(0,0,0,.5)}.navbar-light .navbar-text a{color:rgba(0,0,0,.9)}.navbar-light .navbar-text a:focus,.navbar-light .navbar-text a:hover{color:rgba(0,0,0,.9)}.navbar-dark .navbar-brand{color:#32334a}.navbar-dark .navbar-brand:focus,.navbar-dark .navbar-brand:hover{color:#32334a}.navbar-dark .navbar-nav .nav-link{color:rgba(50,51,74,.5)}.navbar-dark .navbar-nav .nav-link:focus,.navbar-dark .navbar-nav .nav-link:hover{color:rgba(50,51,74,.75)}.navbar-dark .navbar-nav .nav-link.disabled{color:rgba(50,51,74,.25)}.navbar-dark .navbar-nav .active>.nav-link,.navbar-dark .navbar-nav .nav-link.active,.navbar-dark .navbar-nav .nav-link.show,.navbar-dark .navbar-nav .show>.nav-link{color:#32334a}.navbar-dark .navbar-toggler{color:rgba(50,51,74,.5);border-color:rgba(50,51,74,.1)}.navbar-dark .navbar-toggler-icon{background-image:url("data:image/svg+xml,%3csvg viewBox='0 0 30 30' xmlns='http://www.w3.org/2000/svg'%3e%3cpath stroke='rgba(50, 51, 74, 0.5)' stroke-width='2' stroke-linecap='round' stroke-miterlimit='10' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e")}.navbar-dark .navbar-text{color:rgba(50,51,74,.5)}.navbar-dark .navbar-text a{color:#32334a}.navbar-dark .navbar-text a:focus,.navbar-dark .navbar-text a:hover{color:#32334a}.card{position:relative;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;min-width:0;word-wrap:break-word;background-color:#32334a;background-clip:border-box;border:1px solid #151623;border-radius:6px}.card>hr{margin-right:0;margin-left:0}.card>.list-group:first-child .list-group-item:first-child{border-top-left-radius:6px;border-top-right-radius:6px}.card>.list-group:last-child .list-group-item:last-child{border-bottom-right-radius:6px;border-bottom-left-radius:6px}.card-body{-webkit-box-flex:1;-webkit-flex:1 1 auto;-ms-flex:1 1 auto;flex:1 1 auto;padding:1.25rem}.card-title{margin-bottom:.75rem}.card-subtitle{margin-top:-.375rem;margin-bottom:0}.card-text:last-child{margin-bottom:0}.card-link:hover{text-decoration:none}.card-link+.card-link{margin-left:1.25rem}.card-header{padding:.75rem 1.25rem;margin-bottom:0;background-color:#1e2037;border-bottom:1px solid #151623}.card-header:first-child{border-radius:calc(6px - 1px) calc(6px - 1px) 0 0}.card-header+.list-group .list-group-item:first-child{border-top:0}.card-footer{padding:.75rem 1.25rem;background-color:#1e2037;border-top:1px solid #151623}.card-footer:last-child{border-radius:0 0 calc(6px - 1px) calc(6px - 1px)}.card-header-tabs{margin-right:-.625rem;margin-bottom:-.75rem;margin-left:-.625rem;border-bottom:0}.card-header-pills{margin-right:-.625rem;margin-left:-.625rem}.card-img-overlay{position:absolute;top:0;right:0;bottom:0;left:0;padding:1.25rem}.card-img{width:100%;border-radius:calc(6px - 1px)}.card-img-top{width:100%;border-top-left-radius:calc(6px - 1px);border-top-right-radius:calc(6px - 1px)}.card-img-bottom{width:100%;border-bottom-right-radius:calc(6px - 1px);border-bottom-left-radius:calc(6px - 1px)}.card-deck{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column}.card-deck .card{margin-bottom:15px}@media (min-width:576px){.card-deck{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row wrap;-ms-flex-flow:row wrap;flex-flow:row wrap;margin-right:-15px;margin-left:-15px}.card-deck .card{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-flex:1;-webkit-flex:1 0 0%;-ms-flex:1 0 0%;flex:1 0 0%;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;margin-right:15px;margin-bottom:0;margin-left:15px}}.card-group{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column}.card-group>.card{margin-bottom:15px}@media (min-width:576px){.card-group{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-flow:row wrap;-ms-flex-flow:row wrap;flex-flow:row wrap}.card-group>.card{-webkit-box-flex:1;-webkit-flex:1 0 0%;-ms-flex:1 0 0%;flex:1 0 0%;margin-bottom:0}.card-group>.card+.card{margin-left:0;border-left:0}.card-group>.card:not(:last-child){border-top-right-radius:0;border-bottom-right-radius:0}.card-group>.card:not(:last-child) .card-header,.card-group>.card:not(:last-child) .card-img-top{border-top-right-radius:0}.card-group>.card:not(:last-child) .card-footer,.card-group>.card:not(:last-child) .card-img-bottom{border-bottom-right-radius:0}.card-group>.card:not(:first-child){border-top-left-radius:0;border-bottom-left-radius:0}.card-group>.card:not(:first-child) .card-header,.card-group>.card:not(:first-child) .card-img-top{border-top-left-radius:0}.card-group>.card:not(:first-child) .card-footer,.card-group>.card:not(:first-child) .card-img-bottom{border-bottom-left-radius:0}}.card-columns .card{margin-bottom:.75rem}@media (min-width:576px){.card-columns{-webkit-column-count:3;-moz-column-count:3;column-count:3;-webkit-column-gap:1.25rem;-moz-column-gap:1.25rem;column-gap:1.25rem;orphans:1;widows:1}.card-columns .card{display:inline-block;width:100%}}.accordion>.card{overflow:hidden}.accordion>.card:not(:first-of-type) .card-header:first-child{border-radius:0}.accordion>.card:not(:first-of-type):not(:last-of-type){border-bottom:0;border-radius:0}.accordion>.card:first-of-type{border-bottom:0;border-bottom-right-radius:0;border-bottom-left-radius:0}.accordion>.card:last-of-type{border-top-left-radius:0;border-top-right-radius:0}.accordion>.card .card-header{margin-bottom:-1px}.breadcrumb{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-flex-wrap:wrap;-ms-flex-wrap:wrap;flex-wrap:wrap;padding:.75rem 1rem;margin-bottom:1rem;list-style:none;background-color:#282a38;border-radius:6px}.breadcrumb-item+.breadcrumb-item{padding-left:.5rem}.breadcrumb-item+.breadcrumb-item::before{display:inline-block;padding-right:.5rem;color:#1d1e2f;content:"/"}.breadcrumb-item+.breadcrumb-item:hover::before{text-decoration:underline}.breadcrumb-item+.breadcrumb-item:hover::before{text-decoration:none}.breadcrumb-item.active{color:#1d1e2f}.pagination{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;padding-left:0;list-style:none;border-radius:6px}.page-link{position:relative;display:block;padding:.5rem .75rem;margin-left:-1px;line-height:1.25;color:#714cdf;background-color:#32334a;border:1px solid #151623}.page-link:hover{z-index:2;color:#4922bd;text-decoration:none;background-color:#282a38;border-color:#151623}.page-link:focus{z-index:2;outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.25);box-shadow:0 0 0 .2rem rgba(113,76,223,.25)}.page-item:first-child .page-link{margin-left:0;border-top-left-radius:6px;border-bottom-left-radius:6px}.page-item:last-child .page-link{border-top-right-radius:6px;border-bottom-right-radius:6px}.page-item.active .page-link{z-index:1;color:#fff;background-color:#714cdf;border-color:#714cdf}.page-item.disabled .page-link{color:#11111d;pointer-events:none;cursor:auto;background-color:#32334a;border-color:#151623}.pagination-lg .page-link{padding:.75rem 1.5rem;font-size:1.25rem;line-height:1.5}.pagination-lg .page-item:first-child .page-link{border-top-left-radius:6px;border-bottom-left-radius:6px}.pagination-lg .page-item:last-child .page-link{border-top-right-radius:6px;border-bottom-right-radius:6px}.pagination-sm .page-link{padding:.25rem .5rem;font-size:.875rem;line-height:1.5}.pagination-sm .page-item:first-child .page-link{border-top-left-radius:.2rem;border-bottom-left-radius:.2rem}.pagination-sm .page-item:last-child .page-link{border-top-right-radius:.2rem;border-bottom-right-radius:.2rem}.badge{display:inline-block;padding:.25em .4em;font-size:75%;font-weight:700;line-height:1;text-align:center;white-space:nowrap;vertical-align:baseline;border-radius:6px;-webkit-transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,-webkit-box-shadow .15s ease-in-out;-o-transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out,-webkit-box-shadow .15s ease-in-out}@media (prefers-reduced-motion:reduce){.badge{-webkit-transition:none;-o-transition:none;transition:none}}a.badge:focus,a.badge:hover{text-decoration:none}.badge:empty{display:none}.btn .badge{position:relative;top:-1px}.badge-pill{padding-right:.6em;padding-left:.6em;border-radius:10rem}.badge-primary{color:#fff;background-color:#714cdf}a.badge-primary:focus,a.badge-primary:hover{color:#fff;background-color:#5126d2}a.badge-primary.focus,a.badge-primary:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(113,76,223,.5);box-shadow:0 0 0 .2rem rgba(113,76,223,.5)}.badge-secondary{color:#fff;background-color:#16a4de}a.badge-secondary:focus,a.badge-secondary:hover{color:#fff;background-color:#1182b0}a.badge-secondary.focus,a.badge-secondary:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(22,164,222,.5);box-shadow:0 0 0 .2rem rgba(22,164,222,.5)}.badge-success{color:#fff;background-color:#17b06b}a.badge-success:focus,a.badge-success:hover{color:#fff;background-color:#118350}a.badge-success.focus,a.badge-success:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(23,176,107,.5);box-shadow:0 0 0 .2rem rgba(23,176,107,.5)}.badge-info{color:#fff;background-color:#2983fe}a.badge-info:focus,a.badge-info:hover{color:#fff;background-color:#0167f3}a.badge-info.focus,a.badge-info:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(41,131,254,.5);box-shadow:0 0 0 .2rem rgba(41,131,254,.5)}.badge-warning{color:#fff;background-color:#f97515}a.badge-warning:focus,a.badge-warning:hover{color:#fff;background-color:#d65d05}a.badge-warning.focus,a.badge-warning:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(249,117,21,.5);box-shadow:0 0 0 .2rem rgba(249,117,21,.5)}.badge-danger{color:#fff;background-color:#ff3c5c}a.badge-danger:focus,a.badge-danger:hover{color:#fff;background-color:#ff0931}a.badge-danger.focus,a.badge-danger:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(255,60,92,.5);box-shadow:0 0 0 .2rem rgba(255,60,92,.5)}.badge-light{color:#0a0b14;background-color:#dbebfb}a.badge-light:focus,a.badge-light:hover{color:#0a0b14;background-color:#add2f6}a.badge-light.focus,a.badge-light:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(219,235,251,.5);box-shadow:0 0 0 .2rem rgba(219,235,251,.5)}.badge-dark{color:#fff;background-color:#32334a}a.badge-dark:focus,a.badge-dark:hover{color:#fff;background-color:#1d1e2c}a.badge-dark.focus,a.badge-dark:focus{outline:0;-webkit-box-shadow:0 0 0 .2rem rgba(50,51,74,.5);box-shadow:0 0 0 .2rem rgba(50,51,74,.5)}.jumbotron{padding:2rem 1rem;margin-bottom:2rem;background-color:#282a38;border-radius:6px}@media (min-width:576px){.jumbotron{padding:4rem 2rem}}.jumbotron-fluid{padding-right:0;padding-left:0;border-radius:0}.alert{position:relative;padding:.75rem 1.25rem;margin-bottom:1rem;border:1px solid transparent;border-radius:6px}.alert-heading{color:inherit}.alert-link{font-weight:700}.alert-dismissible{padding-right:4rem}.alert-dismissible .close{position:absolute;top:0;right:0;padding:.75rem 1.25rem;color:inherit}.alert-primary{color:#3b2874;background-color:#e3dbf9;border-color:#d7cdf6}.alert-primary hr{border-top-color:#c6b7f2}.alert-primary .alert-link{color:#281b4e}.alert-secondary{color:#0b5573;background-color:#d0edf8;border-color:#bee6f6}.alert-secondary hr{border-top-color:#a8ddf3}.alert-secondary .alert-link{color:#073344}.alert-success{color:#0c5c38;background-color:#d1efe1;border-color:#bee9d6}.alert-success hr{border-top-color:#abe3ca}.alert-success .alert-link{color:#062f1d}.alert-info{color:#154484;background-color:#d4e6ff;border-color:#c3dcff}.alert-info hr{border-top-color:#aacdff}.alert-info .alert-link{color:#0e2d58}.alert-warning{color:#813d0b;background-color:#fee3d0;border-color:#fdd8bd}.alert-warning hr{border-top-color:#fcc9a4}.alert-warning .alert-link{color:#522707}.alert-danger{color:#851f30;background-color:#ffd8de;border-color:#ffc8d1}.alert-danger hr{border-top-color:#ffafbc}.alert-danger .alert-link{color:#5c1521}.alert-light{color:#727a83;background-color:#f8fbfe;border-color:#f5f9fe}.alert-light hr{border-top-color:#deebfc}.alert-light .alert-link{color:#5a6168}.alert-dark{color:#1a1b26;background-color:#d6d6db;border-color:#c6c6cc}.alert-dark hr{border-top-color:#b9b9c0}.alert-dark .alert-link{color:#050508}@-webkit-keyframes progress-bar-stripes{from{background-position:1rem 0}to{background-position:0 0}}@-o-keyframes progress-bar-stripes{from{background-position:1rem 0}to{background-position:0 0}}@keyframes progress-bar-stripes{from{background-position:1rem 0}to{background-position:0 0}}.progress{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;height:1rem;overflow:hidden;font-size:.75rem;background-color:#282a38;border-radius:6px}.progress-bar{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;color:#32334a;text-align:center;white-space:nowrap;background-color:#714cdf;-webkit-transition:width .6s ease;-o-transition:width .6s ease;transition:width .6s ease}@media (prefers-reduced-motion:reduce){.progress-bar{-webkit-transition:none;-o-transition:none;transition:none}}.progress-bar-striped{background-image:-webkit-linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent);background-image:-o-linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent);background-image:linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent);-webkit-background-size:1rem 1rem;background-size:1rem 1rem}.progress-bar-animated{-webkit-animation:progress-bar-stripes 1s linear infinite;-o-animation:progress-bar-stripes 1s linear infinite;animation:progress-bar-stripes 1s linear infinite}@media (prefers-reduced-motion:reduce){.progress-bar-animated{-webkit-animation:none;-o-animation:none;animation:none}}.media{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:start;-webkit-align-items:flex-start;-ms-flex-align:start;align-items:flex-start}.media-body{-webkit-box-flex:1;-webkit-flex:1;-ms-flex:1;flex:1}.list-group{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;padding-left:0;margin-bottom:0}.list-group-item-action{width:100%;color:#e4e2ff;text-align:inherit}.list-group-item-action:focus,.list-group-item-action:hover{z-index:1;color:#e4e2ff;text-decoration:none;background-color:#2d2e3f}.list-group-item-action:active{color:#e4e2ff;background-color:#282a38}.list-group-item{position:relative;display:block;padding:.75rem 1.25rem;margin-bottom:-1px;background-color:#32334a;border:1px solid rgba(0,0,0,.125)}.list-group-item:first-child{border-top-left-radius:6px;border-top-right-radius:6px}.list-group-item:last-child{margin-bottom:0;border-bottom-right-radius:6px;border-bottom-left-radius:6px}.list-group-item.disabled,.list-group-item:disabled{color:#1d1e2f;pointer-events:none;background-color:#32334a}.list-group-item.active{z-index:2;color:#32334a;background-color:#714cdf;border-color:#714cdf}.list-group-horizontal{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.list-group-horizontal .list-group-item{margin-right:-1px;margin-bottom:0}.list-group-horizontal .list-group-item:first-child{border-top-left-radius:6px;border-bottom-left-radius:6px;border-top-right-radius:0}.list-group-horizontal .list-group-item:last-child{margin-right:0;border-top-right-radius:6px;border-bottom-right-radius:6px;border-bottom-left-radius:0}@media (min-width:576px){.list-group-horizontal-sm{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.list-group-horizontal-sm .list-group-item{margin-right:-1px;margin-bottom:0}.list-group-horizontal-sm .list-group-item:first-child{border-top-left-radius:6px;border-bottom-left-radius:6px;border-top-right-radius:0}.list-group-horizontal-sm .list-group-item:last-child{margin-right:0;border-top-right-radius:6px;border-bottom-right-radius:6px;border-bottom-left-radius:0}}@media (min-width:768px){.list-group-horizontal-md{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.list-group-horizontal-md .list-group-item{margin-right:-1px;margin-bottom:0}.list-group-horizontal-md .list-group-item:first-child{border-top-left-radius:6px;border-bottom-left-radius:6px;border-top-right-radius:0}.list-group-horizontal-md .list-group-item:last-child{margin-right:0;border-top-right-radius:6px;border-bottom-right-radius:6px;border-bottom-left-radius:0}}@media (min-width:992px){.list-group-horizontal-lg{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.list-group-horizontal-lg .list-group-item{margin-right:-1px;margin-bottom:0}.list-group-horizontal-lg .list-group-item:first-child{border-top-left-radius:6px;border-bottom-left-radius:6px;border-top-right-radius:0}.list-group-horizontal-lg .list-group-item:last-child{margin-right:0;border-top-right-radius:6px;border-bottom-right-radius:6px;border-bottom-left-radius:0}}@media (min-width:1200px){.list-group-horizontal-xl{-webkit-box-orient:horizontal;-webkit-box-direction:normal;-webkit-flex-direction:row;-ms-flex-direction:row;flex-direction:row}.list-group-horizontal-xl .list-group-item{margin-right:-1px;margin-bottom:0}.list-group-horizontal-xl .list-group-item:first-child{border-top-left-radius:6px;border-bottom-left-radius:6px;border-top-right-radius:0}.list-group-horizontal-xl .list-group-item:last-child{margin-right:0;border-top-right-radius:6px;border-bottom-right-radius:6px;border-bottom-left-radius:0}}.list-group-flush .list-group-item{border-right:0;border-left:0;border-radius:0}.list-group-flush .list-group-item:last-child{margin-bottom:-1px}.list-group-flush:first-child .list-group-item:first-child{border-top:0}.list-group-flush:last-child .list-group-item:last-child{margin-bottom:0;border-bottom:0}.list-group-item-primary{color:#3b2874;background-color:#d7cdf6}.list-group-item-primary.list-group-item-action:focus,.list-group-item-primary.list-group-item-action:hover{color:#3b2874;background-color:#c6b7f2}.list-group-item-primary.list-group-item-action.active{color:#fff;background-color:#3b2874;border-color:#3b2874}.list-group-item-secondary{color:#0b5573;background-color:#bee6f6}.list-group-item-secondary.list-group-item-action:focus,.list-group-item-secondary.list-group-item-action:hover{color:#0b5573;background-color:#a8ddf3}.list-group-item-secondary.list-group-item-action.active{color:#fff;background-color:#0b5573;border-color:#0b5573}.list-group-item-success{color:#0c5c38;background-color:#bee9d6}.list-group-item-success.list-group-item-action:focus,.list-group-item-success.list-group-item-action:hover{color:#0c5c38;background-color:#abe3ca}.list-group-item-success.list-group-item-action.active{color:#fff;background-color:#0c5c38;border-color:#0c5c38}.list-group-item-info{color:#154484;background-color:#c3dcff}.list-group-item-info.list-group-item-action:focus,.list-group-item-info.list-group-item-action:hover{color:#154484;background-color:#aacdff}.list-group-item-info.list-group-item-action.active{color:#fff;background-color:#154484;border-color:#154484}.list-group-item-warning{color:#813d0b;background-color:#fdd8bd}.list-group-item-warning.list-group-item-action:focus,.list-group-item-warning.list-group-item-action:hover{color:#813d0b;background-color:#fcc9a4}.list-group-item-warning.list-group-item-action.active{color:#fff;background-color:#813d0b;border-color:#813d0b}.list-group-item-danger{color:#851f30;background-color:#ffc8d1}.list-group-item-danger.list-group-item-action:focus,.list-group-item-danger.list-group-item-action:hover{color:#851f30;background-color:#ffafbc}.list-group-item-danger.list-group-item-action.active{color:#fff;background-color:#851f30;border-color:#851f30}.list-group-item-light{color:#727a83;background-color:#f5f9fe}.list-group-item-light.list-group-item-action:focus,.list-group-item-light.list-group-item-action:hover{color:#727a83;background-color:#deebfc}.list-group-item-light.list-group-item-action.active{color:#fff;background-color:#727a83;border-color:#727a83}.list-group-item-dark{color:#1a1b26;background-color:#c6c6cc}.list-group-item-dark.list-group-item-action:focus,.list-group-item-dark.list-group-item-action:hover{color:#1a1b26;background-color:#b9b9c0}.list-group-item-dark.list-group-item-action.active{color:#fff;background-color:#1a1b26;border-color:#1a1b26}.close{float:right;font-size:1.5rem;font-weight:700;line-height:1;color:#000;text-shadow:0 1px 0 #32334a;opacity:.5}.close:hover{color:#000;text-decoration:none}.close:not(:disabled):not(.disabled):focus,.close:not(:disabled):not(.disabled):hover{opacity:.75}button.close{padding:0;background-color:transparent;border:0;-webkit-appearance:none;-moz-appearance:none;appearance:none}a.close.disabled{pointer-events:none}.toast{max-width:350px;overflow:hidden;font-size:.875rem;background-color:rgba(255,255,255,.85);background-clip:padding-box;border:1px solid rgba(0,0,0,.1);-webkit-box-shadow:0 .25rem .75rem rgba(0,0,0,.1);box-shadow:0 .25rem .75rem rgba(0,0,0,.1);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);opacity:0;border-radius:.25rem}.toast:not(:last-child){margin-bottom:.75rem}.toast.showing{opacity:1}.toast.show{display:block;opacity:1}.toast.hide{display:none}.toast-header{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;padding:.25rem .75rem;color:#1d1e2f;background-color:rgba(255,255,255,.85);background-clip:padding-box;border-bottom:1px solid rgba(0,0,0,.05)}.toast-body{padding:.75rem}.modal-open{overflow:hidden}.modal-open .modal{overflow-x:hidden;overflow-y:auto}.modal{position:fixed;top:0;left:0;z-index:1050;display:none;width:100%;height:100%;overflow:hidden;outline:0}.modal-dialog{position:relative;width:auto;margin:.5rem;pointer-events:none}.modal.fade .modal-dialog{-webkit-transition:-webkit-transform .3s ease-out;transition:-webkit-transform .3s ease-out;-o-transition:-o-transform .3s ease-out;transition:transform .3s ease-out;transition:transform .3s ease-out,-webkit-transform .3s ease-out,-o-transform .3s ease-out;-webkit-transform:translate(0,-50px);-o-transform:translate(0,-50px);transform:translate(0,-50px)}@media (prefers-reduced-motion:reduce){.modal.fade .modal-dialog{-webkit-transition:none;-o-transition:none;transition:none}}.modal.show .modal-dialog{-webkit-transform:none;-o-transform:none;transform:none}.modal-dialog-scrollable{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;max-height:calc(100% - 1rem)}.modal-dialog-scrollable .modal-content{max-height:calc(100vh - 1rem);overflow:hidden}.modal-dialog-scrollable .modal-footer,.modal-dialog-scrollable .modal-header{-webkit-flex-shrink:0;-ms-flex-negative:0;flex-shrink:0}.modal-dialog-scrollable .modal-body{overflow-y:auto}.modal-dialog-centered{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;min-height:calc(100% - 1rem)}.modal-dialog-centered::before{display:block;height:calc(100vh - 1rem);content:""}.modal-dialog-centered.modal-dialog-scrollable{-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;height:100%}.modal-dialog-centered.modal-dialog-scrollable .modal-content{max-height:none}.modal-dialog-centered.modal-dialog-scrollable::before{content:none}.modal-content{position:relative;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-orient:vertical;-webkit-box-direction:normal;-webkit-flex-direction:column;-ms-flex-direction:column;flex-direction:column;width:100%;pointer-events:auto;background-color:#32334a;background-clip:padding-box;border:1px solid rgba(0,0,0,.2);border-radius:6px;outline:0}.modal-backdrop{position:fixed;top:0;left:0;z-index:1040;width:100vw;height:100vh;background-color:#000}.modal-backdrop.fade{opacity:0}.modal-backdrop.show{opacity:.5}.modal-header{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:start;-webkit-align-items:flex-start;-ms-flex-align:start;align-items:flex-start;-webkit-box-pack:justify;-webkit-justify-content:space-between;-ms-flex-pack:justify;justify-content:space-between;padding:1rem 1rem;border-bottom:1px solid #28293e;border-top-left-radius:6px;border-top-right-radius:6px}.modal-header .close{padding:1rem 1rem;margin:-1rem -1rem -1rem auto}.modal-title{margin-bottom:0;line-height:1.5}.modal-body{position:relative;-webkit-box-flex:1;-webkit-flex:1 1 auto;-ms-flex:1 1 auto;flex:1 1 auto;padding:1rem}.modal-footer{display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:end;-webkit-justify-content:flex-end;-ms-flex-pack:end;justify-content:flex-end;padding:1rem;border-top:1px solid #28293e;border-bottom-right-radius:6px;border-bottom-left-radius:6px}.modal-footer>:not(:first-child){margin-left:.25rem}.modal-footer>:not(:last-child){margin-right:.25rem}.modal-scrollbar-measure{position:absolute;top:-9999px;width:50px;height:50px;overflow:scroll}@media (min-width:576px){.modal-dialog{max-width:500px;margin:1.75rem auto}.modal-dialog-scrollable{max-height:calc(100% - 3.5rem)}.modal-dialog-scrollable .modal-content{max-height:calc(100vh - 3.5rem)}.modal-dialog-centered{min-height:calc(100% - 3.5rem)}.modal-dialog-centered::before{height:calc(100vh - 3.5rem)}.modal-sm{max-width:300px}}@media (min-width:992px){.modal-lg,.modal-xl{max-width:800px}}@media (min-width:1200px){.modal-xl{max-width:1140px}}.tooltip{position:absolute;z-index:1070;display:block;margin:0;font-family:Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-style:normal;font-weight:400;line-height:1.5;text-align:left;text-align:start;text-decoration:none;text-shadow:none;text-transform:none;letter-spacing:normal;word-break:normal;word-spacing:normal;white-space:normal;line-break:auto;font-size:.875rem;word-wrap:break-word;opacity:0}.tooltip.show{opacity:.9}.tooltip .arrow{position:absolute;display:block;width:.8rem;height:.4rem}.tooltip .arrow::before{position:absolute;content:"";border-color:transparent;border-style:solid}.bs-tooltip-auto[x-placement^=top],.bs-tooltip-top{padding:.4rem 0}.bs-tooltip-auto[x-placement^=top] .arrow,.bs-tooltip-top .arrow{bottom:0}.bs-tooltip-auto[x-placement^=top] .arrow::before,.bs-tooltip-top .arrow::before{top:0;border-width:.4rem .4rem 0;border-top-color:#000}.bs-tooltip-auto[x-placement^=right],.bs-tooltip-right{padding:0 .4rem}.bs-tooltip-auto[x-placement^=right] .arrow,.bs-tooltip-right .arrow{left:0;width:.4rem;height:.8rem}.bs-tooltip-auto[x-placement^=right] .arrow::before,.bs-tooltip-right .arrow::before{right:0;border-width:.4rem .4rem .4rem 0;border-right-color:#000}.bs-tooltip-auto[x-placement^=bottom],.bs-tooltip-bottom{padding:.4rem 0}.bs-tooltip-auto[x-placement^=bottom] .arrow,.bs-tooltip-bottom .arrow{top:0}.bs-tooltip-auto[x-placement^=bottom] .arrow::before,.bs-tooltip-bottom .arrow::before{bottom:0;border-width:0 .4rem .4rem;border-bottom-color:#000}.bs-tooltip-auto[x-placement^=left],.bs-tooltip-left{padding:0 .4rem}.bs-tooltip-auto[x-placement^=left] .arrow,.bs-tooltip-left .arrow{right:0;width:.4rem;height:.8rem}.bs-tooltip-auto[x-placement^=left] .arrow::before,.bs-tooltip-left .arrow::before{left:0;border-width:.4rem 0 .4rem .4rem;border-left-color:#000}.tooltip-inner{max-width:200px;padding:.25rem .5rem;color:#e4e2ff;text-align:center;background-color:#000;border-radius:6px}.popover{position:absolute;top:0;left:0;z-index:1060;display:block;max-width:276px;font-family:Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-style:normal;font-weight:400;line-height:1.5;text-align:left;text-align:start;text-decoration:none;text-shadow:none;text-transform:none;letter-spacing:normal;word-break:normal;word-spacing:normal;white-space:normal;line-break:auto;font-size:.875rem;word-wrap:break-word;background-color:#32334a;background-clip:padding-box;border:1px solid rgba(0,0,0,.2);border-radius:6px}.popover .arrow{position:absolute;display:block;width:1rem;height:.5rem;margin:0 6px}.popover .arrow::after,.popover .arrow::before{position:absolute;display:block;content:"";border-color:transparent;border-style:solid}.bs-popover-auto[x-placement^=top],.bs-popover-top{margin-bottom:.5rem}.bs-popover-auto[x-placement^=top]>.arrow,.bs-popover-top>.arrow{bottom:calc((.5rem + 1px) * -1)}.bs-popover-auto[x-placement^=top]>.arrow::before,.bs-popover-top>.arrow::before{bottom:0;border-width:.5rem .5rem 0;border-top-color:rgba(0,0,0,.25)}.bs-popover-auto[x-placement^=top]>.arrow::after,.bs-popover-top>.arrow::after{bottom:1px;border-width:.5rem .5rem 0;border-top-color:#32334a}.bs-popover-auto[x-placement^=right],.bs-popover-right{margin-left:.5rem}.bs-popover-auto[x-placement^=right]>.arrow,.bs-popover-right>.arrow{left:calc((.5rem + 1px) * -1);width:.5rem;height:1rem;margin:6px 0}.bs-popover-auto[x-placement^=right]>.arrow::before,.bs-popover-right>.arrow::before{left:0;border-width:.5rem .5rem .5rem 0;border-right-color:rgba(0,0,0,.25)}.bs-popover-auto[x-placement^=right]>.arrow::after,.bs-popover-right>.arrow::after{left:1px;border-width:.5rem .5rem .5rem 0;border-right-color:#32334a}.bs-popover-auto[x-placement^=bottom],.bs-popover-bottom{margin-top:.5rem}.bs-popover-auto[x-placement^=bottom]>.arrow,.bs-popover-bottom>.arrow{top:calc((.5rem + 1px) * -1)}.bs-popover-auto[x-placement^=bottom]>.arrow::before,.bs-popover-bottom>.arrow::before{top:0;border-width:0 .5rem .5rem .5rem;border-bottom-color:rgba(0,0,0,.25)}.bs-popover-auto[x-placement^=bottom]>.arrow::after,.bs-popover-bottom>.arrow::after{top:1px;border-width:0 .5rem .5rem .5rem;border-bottom-color:#32334a}.bs-popover-auto[x-placement^=bottom] .popover-header::before,.bs-popover-bottom .popover-header::before{position:absolute;top:0;left:50%;display:block;width:1rem;margin-left:-.5rem;content:"";border-bottom:1px solid #2c2d41}.bs-popover-auto[x-placement^=left],.bs-popover-left{margin-right:.5rem}.bs-popover-auto[x-placement^=left]>.arrow,.bs-popover-left>.arrow{right:calc((.5rem + 1px) * -1);width:.5rem;height:1rem;margin:6px 0}.bs-popover-auto[x-placement^=left]>.arrow::before,.bs-popover-left>.arrow::before{right:0;border-width:.5rem 0 .5rem .5rem;border-left-color:rgba(0,0,0,.25)}.bs-popover-auto[x-placement^=left]>.arrow::after,.bs-popover-left>.arrow::after{right:1px;border-width:.5rem 0 .5rem .5rem;border-left-color:#32334a}.popover-header{padding:.5rem .75rem;margin-bottom:0;font-size:1rem;background-color:#2c2d41;border-bottom:1px solid #222232;border-top-left-radius:calc(6px - 1px);border-top-right-radius:calc(6px - 1px)}.popover-header:empty{display:none}.popover-body{padding:.5rem .75rem;color:#e4e2ff}.carousel{position:relative}.carousel.pointer-event{-ms-touch-action:pan-y;touch-action:pan-y}.carousel-inner{position:relative;width:100%;overflow:hidden}.carousel-inner::after{display:block;clear:both;content:""}.carousel-item{position:relative;display:none;float:left;width:100%;margin-right:-100%;-webkit-backface-visibility:hidden;backface-visibility:hidden;-webkit-transition:-webkit-transform .6s ease-in-out;transition:-webkit-transform .6s ease-in-out;-o-transition:-o-transform .6s ease-in-out;transition:transform .6s ease-in-out;transition:transform .6s ease-in-out,-webkit-transform .6s ease-in-out,-o-transform .6s ease-in-out}@media (prefers-reduced-motion:reduce){.carousel-item{-webkit-transition:none;-o-transition:none;transition:none}}.carousel-item-next,.carousel-item-prev,.carousel-item.active{display:block}.active.carousel-item-right,.carousel-item-next:not(.carousel-item-left){-webkit-transform:translateX(100%);-o-transform:translateX(100%);transform:translateX(100%)}.active.carousel-item-left,.carousel-item-prev:not(.carousel-item-right){-webkit-transform:translateX(-100%);-o-transform:translateX(-100%);transform:translateX(-100%)}.carousel-fade .carousel-item{opacity:0;-webkit-transition-property:opacity;-o-transition-property:opacity;transition-property:opacity;-webkit-transform:none;-o-transform:none;transform:none}.carousel-fade .carousel-item-next.carousel-item-left,.carousel-fade .carousel-item-prev.carousel-item-right,.carousel-fade .carousel-item.active{z-index:1;opacity:1}.carousel-fade .active.carousel-item-left,.carousel-fade .active.carousel-item-right{z-index:0;opacity:0;-webkit-transition:0s .6s opacity;-o-transition:0s .6s opacity;transition:0s .6s opacity}@media (prefers-reduced-motion:reduce){.carousel-fade .active.carousel-item-left,.carousel-fade .active.carousel-item-right{-webkit-transition:none;-o-transition:none;transition:none}}.carousel-control-next,.carousel-control-prev{position:absolute;top:0;bottom:0;z-index:1;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-align:center;-webkit-align-items:center;-ms-flex-align:center;align-items:center;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;width:15%;color:#32334a;text-align:center;opacity:.5;-webkit-transition:opacity .15s ease;-o-transition:opacity .15s ease;transition:opacity .15s ease}@media (prefers-reduced-motion:reduce){.carousel-control-next,.carousel-control-prev{-webkit-transition:none;-o-transition:none;transition:none}}.carousel-control-next:focus,.carousel-control-next:hover,.carousel-control-prev:focus,.carousel-control-prev:hover{color:#32334a;text-decoration:none;outline:0;opacity:.9}.carousel-control-prev{left:0}.carousel-control-next{right:0}.carousel-control-next-icon,.carousel-control-prev-icon{display:inline-block;width:20px;height:20px;background:no-repeat 50%/100% 100%}.carousel-control-prev-icon{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%2332334a' viewBox='0 0 8 8'%3e%3cpath d='M5.25 0l-4 4 4 4 1.5-1.5-2.5-2.5 2.5-2.5-1.5-1.5z'/%3e%3c/svg%3e")}.carousel-control-next-icon{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%2332334a' viewBox='0 0 8 8'%3e%3cpath d='M2.75 0l-1.5 1.5 2.5 2.5-2.5 2.5 1.5 1.5 4-4-4-4z'/%3e%3c/svg%3e")}.carousel-indicators{position:absolute;right:0;bottom:0;left:0;z-index:15;display:-webkit-box;display:-webkit-flex;display:-ms-flexbox;display:flex;-webkit-box-pack:center;-webkit-justify-content:center;-ms-flex-pack:center;justify-content:center;padding-left:0;margin-right:15%;margin-left:15%;list-style:none}.carousel-indicators li{-webkit-box-sizing:content-box;box-sizing:content-box;-webkit-box-flex:0;-webkit-flex:0 1 auto;-ms-flex:0 1 auto;flex:0 1 auto;width:30px;height:3px;margin-right:3px;margin-left:3px;text-indent:-999px;cursor:pointer;background-color:#32334a;background-clip:padding-box;border-top:10px solid transparent;border-bottom:10px solid transparent;opacity:.5;-webkit-transition:opacity .6s ease;-o-transition:opacity .6s ease;transition:opacity .6s ease}@media (prefers-reduced-motion:reduce){.carousel-indicators li{-webkit-transition:none;-o-transition:none;transition:none}}.carousel-indicators .active{opacity:1}.carousel-caption{position:absolute;right:15%;bottom:20px;left:15%;z-index:10;padding-top:20px;padding-bottom:20px;color:#32334a;text-align:center}@-webkit-keyframes spinner-border{to{-webkit-transform:rotate(360deg);transform:rotate(360deg)}}@-o-keyframes spinner-border{to{-o-transform:rotate(360deg);transform:rotate(360deg)}}@keyframes spinner-border{to{-webkit-transform:rotate(360deg);-o-transform:rotate(360deg);transform:rotate(360deg)}}.spinner-border{display:inline-block;width:2rem;height:2rem;vertical-align:text-bottom;border:.25em solid currentColor;border-right-color:transparent;border-radius:50%;-webkit-animation:spinner-border .75s linear infinite;-o-animation:spinner-border .75s linear infinite;animation:spinner-border .75s linear infinite}.spinner-border-sm{width:1rem;height:1rem;border-width:.2em}@-webkit-keyframes spinner-grow{0%{-webkit-transform:scale(0);transform:scale(0)}50%{opacity:1}}@-o-keyframes spinner-grow{0%{-o-transform:scale(0);transform:scale(0)}50%{opacity:1}}@keyframes spinner-grow{0%{-webkit-transform:scale(0);-o-transform:scale(0);transform:scale(0)}50%{opacity:1}}.spinner-grow{display:inline-block;width:2rem;height:2rem;vertical-align:text-bottom;background-color:currentColor;border-radius:50%;opacity:0;-webkit-animation:spinner-grow .75s linear infinite;-o-animation:spinner-grow .75s linear infinite;animation:spinner-grow .75s linear infinite}.spinner-grow-sm{width:1rem;height:1rem}.align-baseline{vertical-align:baseline!important}.align-top{vertical-align:top!important}.align-middle{vertical-align:middle!important}.align-bottom{vertical-align:bottom!important}.align-text-bottom{vertical-align:text-bottom!important}.align-text-top{vertical-align:text-top!important}.bg-primary{background-color:#714cdf!important}a.bg-primary:focus,a.bg-primary:hover,button.bg-primary:focus,button.bg-primary:hover{background-color:#5126d2!important}.bg-secondary{background-color:#16a4de!important}a.bg-secondary:focus,a.bg-secondary:hover,button.bg-secondary:focus,button.bg-secondary:hover{background-color:#1182b0!important}.bg-success{background-color:#17b06b!important}a.bg-success:focus,a.bg-success:hover,button.bg-success:focus,button.bg-success:hover{background-color:#118350!important}.bg-info{background-color:#2983fe!important}a.bg-info:focus,a.bg-info:hover,button.bg-info:focus,button.bg-info:hover{background-color:#0167f3!important}.bg-warning{background-color:#f97515!important}a.bg-warning:focus,a.bg-warning:hover,button.bg-warning:focus,button.bg-warning:hover{background-color:#d65d05!important}.bg-danger{background-color:#ff3c5c!important}a.bg-danger:focus,a.bg-danger:hover,button.bg-danger:focus,button.bg-danger:hover{background-color:#ff0931!important}.bg-light{background-color:#dbebfb!important}a.bg-light:focus,a.bg-light:hover,button.bg-light:focus,button.bg-light:hover{background-color:#add2f6!important}.bg-dark{background-color:#32334a!important}a.bg-dark:focus,a.bg-dark:hover,button.bg-dark:focus,button.bg-dark:hover{background-color:#1d1e2c!important}.bg-white{background-color:#fff!important}.bg-transparent{background-color:transparent!important}.border{border:1px solid #28293e!important}.border-top{border-top:1px solid #28293e!important}.border-right{border-right:1px solid #28293e!important}.border-bottom{border-bottom:1px solid #28293e!important}.border-left{border-left:1px solid #28293e!important}.border-0{border:0!important}.border-top-0{border-top:0!important}.border-right-0{border-right:0!important}.border-bottom-0{border-bottom:0!important}.border-left-0{border-left:0!important}.border-primary{border-color:#714cdf!important}.border-secondary{border-color:#16a4de!important}.border-success{border-color:#17b06b!important}.border-info{border-color:#2983fe!important}.border-warning{border-color:#f97515!important}.border-danger{border-color:#ff3c5c!important}.border-light{border-color:#dbebfb!important}.border-dark{border-color:#32334a!important}.border-white{border-color:#fff!important}.rounded-sm{border-radius:.2rem!important}.rounded{border-radius:6px!important}.rounded-top{border-top-left-radius:6px!important;border-top-right-radius:6px!important}.rounded-right{border-top-right-radius:6px!important;border-bottom-right-radius:6px!important}.rounded-bottom{border-bottom-right-radius:6px!important;border-bottom-left-radius:6px!important}.rounded-left{border-top-left-radius:6px!important;border-bottom-left-radius:6px!important}.rounded-lg{border-radius:6px!important}.rounded-circle{border-radius:50%!important}.rounded-pill{border-radius:50rem!important}.rounded-0{border-radius:0!important}.clearfix::after{display:block;clear:both;content:""}.d-none{display:none!important}.d-inline{display:inline!important}.d-inline-block{display:inline-block!important}.d-block{display:block!important}.d-table{display:table!important}.d-table-row{display:table-row!important}.d-table-cell{display:table-cell!important}.d-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}@media (min-width:576px){.d-sm-none{display:none!important}.d-sm-inline{display:inline!important}.d-sm-inline-block{display:inline-block!important}.d-sm-block{display:block!important}.d-sm-table{display:table!important}.d-sm-table-row{display:table-row!important}.d-sm-table-cell{display:table-cell!important}.d-sm-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-sm-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}}@media (min-width:768px){.d-md-none{display:none!important}.d-md-inline{display:inline!important}.d-md-inline-block{display:inline-block!important}.d-md-block{display:block!important}.d-md-table{display:table!important}.d-md-table-row{display:table-row!important}.d-md-table-cell{display:table-cell!important}.d-md-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-md-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}}@media (min-width:992px){.d-lg-none{display:none!important}.d-lg-inline{display:inline!important}.d-lg-inline-block{display:inline-block!important}.d-lg-block{display:block!important}.d-lg-table{display:table!important}.d-lg-table-row{display:table-row!important}.d-lg-table-cell{display:table-cell!important}.d-lg-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-lg-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}}@media (min-width:1200px){.d-xl-none{display:none!important}.d-xl-inline{display:inline!important}.d-xl-inline-block{display:inline-block!important}.d-xl-block{display:block!important}.d-xl-table{display:table!important}.d-xl-table-row{display:table-row!important}.d-xl-table-cell{display:table-cell!important}.d-xl-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-xl-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}}@media print{.d-print-none{display:none!important}.d-print-inline{display:inline!important}.d-print-inline-block{display:inline-block!important}.d-print-block{display:block!important}.d-print-table{display:table!important}.d-print-table-row{display:table-row!important}.d-print-table-cell{display:table-cell!important}.d-print-flex{display:-webkit-box!important;display:-webkit-flex!important;display:-ms-flexbox!important;display:flex!important}.d-print-inline-flex{display:-webkit-inline-box!important;display:-webkit-inline-flex!important;display:-ms-inline-flexbox!important;display:inline-flex!important}}.embed-responsive{position:relative;display:block;width:100%;padding:0;overflow:hidden}.embed-responsive::before{display:block;content:""}.embed-responsive .embed-responsive-item,.embed-responsive embed,.embed-responsive iframe,.embed-responsive object,.embed-responsive video{position:absolute;top:0;bottom:0;left:0;width:100%;height:100%;border:0}.embed-responsive-21by9::before{padding-top:42.85714%}.embed-responsive-16by9::before{padding-top:56.25%}.embed-responsive-4by3::before{padding-top:75%}.embed-responsive-1by1::before{padding-top:100%}.flex-row{-webkit-box-orient:horizontal!important;-webkit-box-direction:normal!important;-webkit-flex-direction:row!important;-ms-flex-direction:row!important;flex-direction:row!important}.flex-column{-webkit-box-orient:vertical!important;-webkit-box-direction:normal!important;-webkit-flex-direction:column!important;-ms-flex-direction:column!important;flex-direction:column!important}.flex-row-reverse{-webkit-box-orient:horizontal!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:row-reverse!important;-ms-flex-direction:row-reverse!important;flex-direction:row-reverse!important}.flex-column-reverse{-webkit-box-orient:vertical!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:column-reverse!important;-ms-flex-direction:column-reverse!important;flex-direction:column-reverse!important}.flex-wrap{-webkit-flex-wrap:wrap!important;-ms-flex-wrap:wrap!important;flex-wrap:wrap!important}.flex-nowrap{-webkit-flex-wrap:nowrap!important;-ms-flex-wrap:nowrap!important;flex-wrap:nowrap!important}.flex-wrap-reverse{-webkit-flex-wrap:wrap-reverse!important;-ms-flex-wrap:wrap-reverse!important;flex-wrap:wrap-reverse!important}.flex-fill{-webkit-box-flex:1!important;-webkit-flex:1 1 auto!important;-ms-flex:1 1 auto!important;flex:1 1 auto!important}.flex-grow-0{-webkit-box-flex:0!important;-webkit-flex-grow:0!important;-ms-flex-positive:0!important;flex-grow:0!important}.flex-grow-1{-webkit-box-flex:1!important;-webkit-flex-grow:1!important;-ms-flex-positive:1!important;flex-grow:1!important}.flex-shrink-0{-webkit-flex-shrink:0!important;-ms-flex-negative:0!important;flex-shrink:0!important}.flex-shrink-1{-webkit-flex-shrink:1!important;-ms-flex-negative:1!important;flex-shrink:1!important}.justify-content-start{-webkit-box-pack:start!important;-webkit-justify-content:flex-start!important;-ms-flex-pack:start!important;justify-content:flex-start!important}.justify-content-end{-webkit-box-pack:end!important;-webkit-justify-content:flex-end!important;-ms-flex-pack:end!important;justify-content:flex-end!important}.justify-content-center{-webkit-box-pack:center!important;-webkit-justify-content:center!important;-ms-flex-pack:center!important;justify-content:center!important}.justify-content-between{-webkit-box-pack:justify!important;-webkit-justify-content:space-between!important;-ms-flex-pack:justify!important;justify-content:space-between!important}.justify-content-around{-webkit-justify-content:space-around!important;-ms-flex-pack:distribute!important;justify-content:space-around!important}.align-items-start{-webkit-box-align:start!important;-webkit-align-items:flex-start!important;-ms-flex-align:start!important;align-items:flex-start!important}.align-items-end{-webkit-box-align:end!important;-webkit-align-items:flex-end!important;-ms-flex-align:end!important;align-items:flex-end!important}.align-items-center{-webkit-box-align:center!important;-webkit-align-items:center!important;-ms-flex-align:center!important;align-items:center!important}.align-items-baseline{-webkit-box-align:baseline!important;-webkit-align-items:baseline!important;-ms-flex-align:baseline!important;align-items:baseline!important}.align-items-stretch{-webkit-box-align:stretch!important;-webkit-align-items:stretch!important;-ms-flex-align:stretch!important;align-items:stretch!important}.align-content-start{-webkit-align-content:flex-start!important;-ms-flex-line-pack:start!important;align-content:flex-start!important}.align-content-end{-webkit-align-content:flex-end!important;-ms-flex-line-pack:end!important;align-content:flex-end!important}.align-content-center{-webkit-align-content:center!important;-ms-flex-line-pack:center!important;align-content:center!important}.align-content-between{-webkit-align-content:space-between!important;-ms-flex-line-pack:justify!important;align-content:space-between!important}.align-content-around{-webkit-align-content:space-around!important;-ms-flex-line-pack:distribute!important;align-content:space-around!important}.align-content-stretch{-webkit-align-content:stretch!important;-ms-flex-line-pack:stretch!important;align-content:stretch!important}.align-self-auto{-webkit-align-self:auto!important;-ms-flex-item-align:auto!important;align-self:auto!important}.align-self-start{-webkit-align-self:flex-start!important;-ms-flex-item-align:start!important;align-self:flex-start!important}.align-self-end{-webkit-align-self:flex-end!important;-ms-flex-item-align:end!important;align-self:flex-end!important}.align-self-center{-webkit-align-self:center!important;-ms-flex-item-align:center!important;align-self:center!important}.align-self-baseline{-webkit-align-self:baseline!important;-ms-flex-item-align:baseline!important;align-self:baseline!important}.align-self-stretch{-webkit-align-self:stretch!important;-ms-flex-item-align:stretch!important;align-self:stretch!important}@media (min-width:576px){.flex-sm-row{-webkit-box-orient:horizontal!important;-webkit-box-direction:normal!important;-webkit-flex-direction:row!important;-ms-flex-direction:row!important;flex-direction:row!important}.flex-sm-column{-webkit-box-orient:vertical!important;-webkit-box-direction:normal!important;-webkit-flex-direction:column!important;-ms-flex-direction:column!important;flex-direction:column!important}.flex-sm-row-reverse{-webkit-box-orient:horizontal!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:row-reverse!important;-ms-flex-direction:row-reverse!important;flex-direction:row-reverse!important}.flex-sm-column-reverse{-webkit-box-orient:vertical!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:column-reverse!important;-ms-flex-direction:column-reverse!important;flex-direction:column-reverse!important}.flex-sm-wrap{-webkit-flex-wrap:wrap!important;-ms-flex-wrap:wrap!important;flex-wrap:wrap!important}.flex-sm-nowrap{-webkit-flex-wrap:nowrap!important;-ms-flex-wrap:nowrap!important;flex-wrap:nowrap!important}.flex-sm-wrap-reverse{-webkit-flex-wrap:wrap-reverse!important;-ms-flex-wrap:wrap-reverse!important;flex-wrap:wrap-reverse!important}.flex-sm-fill{-webkit-box-flex:1!important;-webkit-flex:1 1 auto!important;-ms-flex:1 1 auto!important;flex:1 1 auto!important}.flex-sm-grow-0{-webkit-box-flex:0!important;-webkit-flex-grow:0!important;-ms-flex-positive:0!important;flex-grow:0!important}.flex-sm-grow-1{-webkit-box-flex:1!important;-webkit-flex-grow:1!important;-ms-flex-positive:1!important;flex-grow:1!important}.flex-sm-shrink-0{-webkit-flex-shrink:0!important;-ms-flex-negative:0!important;flex-shrink:0!important}.flex-sm-shrink-1{-webkit-flex-shrink:1!important;-ms-flex-negative:1!important;flex-shrink:1!important}.justify-content-sm-start{-webkit-box-pack:start!important;-webkit-justify-content:flex-start!important;-ms-flex-pack:start!important;justify-content:flex-start!important}.justify-content-sm-end{-webkit-box-pack:end!important;-webkit-justify-content:flex-end!important;-ms-flex-pack:end!important;justify-content:flex-end!important}.justify-content-sm-center{-webkit-box-pack:center!important;-webkit-justify-content:center!important;-ms-flex-pack:center!important;justify-content:center!important}.justify-content-sm-between{-webkit-box-pack:justify!important;-webkit-justify-content:space-between!important;-ms-flex-pack:justify!important;justify-content:space-between!important}.justify-content-sm-around{-webkit-justify-content:space-around!important;-ms-flex-pack:distribute!important;justify-content:space-around!important}.align-items-sm-start{-webkit-box-align:start!important;-webkit-align-items:flex-start!important;-ms-flex-align:start!important;align-items:flex-start!important}.align-items-sm-end{-webkit-box-align:end!important;-webkit-align-items:flex-end!important;-ms-flex-align:end!important;align-items:flex-end!important}.align-items-sm-center{-webkit-box-align:center!important;-webkit-align-items:center!important;-ms-flex-align:center!important;align-items:center!important}.align-items-sm-baseline{-webkit-box-align:baseline!important;-webkit-align-items:baseline!important;-ms-flex-align:baseline!important;align-items:baseline!important}.align-items-sm-stretch{-webkit-box-align:stretch!important;-webkit-align-items:stretch!important;-ms-flex-align:stretch!important;align-items:stretch!important}.align-content-sm-start{-webkit-align-content:flex-start!important;-ms-flex-line-pack:start!important;align-content:flex-start!important}.align-content-sm-end{-webkit-align-content:flex-end!important;-ms-flex-line-pack:end!important;align-content:flex-end!important}.align-content-sm-center{-webkit-align-content:center!important;-ms-flex-line-pack:center!important;align-content:center!important}.align-content-sm-between{-webkit-align-content:space-between!important;-ms-flex-line-pack:justify!important;align-content:space-between!important}.align-content-sm-around{-webkit-align-content:space-around!important;-ms-flex-line-pack:distribute!important;align-content:space-around!important}.align-content-sm-stretch{-webkit-align-content:stretch!important;-ms-flex-line-pack:stretch!important;align-content:stretch!important}.align-self-sm-auto{-webkit-align-self:auto!important;-ms-flex-item-align:auto!important;align-self:auto!important}.align-self-sm-start{-webkit-align-self:flex-start!important;-ms-flex-item-align:start!important;align-self:flex-start!important}.align-self-sm-end{-webkit-align-self:flex-end!important;-ms-flex-item-align:end!important;align-self:flex-end!important}.align-self-sm-center{-webkit-align-self:center!important;-ms-flex-item-align:center!important;align-self:center!important}.align-self-sm-baseline{-webkit-align-self:baseline!important;-ms-flex-item-align:baseline!important;align-self:baseline!important}.align-self-sm-stretch{-webkit-align-self:stretch!important;-ms-flex-item-align:stretch!important;align-self:stretch!important}}@media (min-width:768px){.flex-md-row{-webkit-box-orient:horizontal!important;-webkit-box-direction:normal!important;-webkit-flex-direction:row!important;-ms-flex-direction:row!important;flex-direction:row!important}.flex-md-column{-webkit-box-orient:vertical!important;-webkit-box-direction:normal!important;-webkit-flex-direction:column!important;-ms-flex-direction:column!important;flex-direction:column!important}.flex-md-row-reverse{-webkit-box-orient:horizontal!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:row-reverse!important;-ms-flex-direction:row-reverse!important;flex-direction:row-reverse!important}.flex-md-column-reverse{-webkit-box-orient:vertical!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:column-reverse!important;-ms-flex-direction:column-reverse!important;flex-direction:column-reverse!important}.flex-md-wrap{-webkit-flex-wrap:wrap!important;-ms-flex-wrap:wrap!important;flex-wrap:wrap!important}.flex-md-nowrap{-webkit-flex-wrap:nowrap!important;-ms-flex-wrap:nowrap!important;flex-wrap:nowrap!important}.flex-md-wrap-reverse{-webkit-flex-wrap:wrap-reverse!important;-ms-flex-wrap:wrap-reverse!important;flex-wrap:wrap-reverse!important}.flex-md-fill{-webkit-box-flex:1!important;-webkit-flex:1 1 auto!important;-ms-flex:1 1 auto!important;flex:1 1 auto!important}.flex-md-grow-0{-webkit-box-flex:0!important;-webkit-flex-grow:0!important;-ms-flex-positive:0!important;flex-grow:0!important}.flex-md-grow-1{-webkit-box-flex:1!important;-webkit-flex-grow:1!important;-ms-flex-positive:1!important;flex-grow:1!important}.flex-md-shrink-0{-webkit-flex-shrink:0!important;-ms-flex-negative:0!important;flex-shrink:0!important}.flex-md-shrink-1{-webkit-flex-shrink:1!important;-ms-flex-negative:1!important;flex-shrink:1!important}.justify-content-md-start{-webkit-box-pack:start!important;-webkit-justify-content:flex-start!important;-ms-flex-pack:start!important;justify-content:flex-start!important}.justify-content-md-end{-webkit-box-pack:end!important;-webkit-justify-content:flex-end!important;-ms-flex-pack:end!important;justify-content:flex-end!important}.justify-content-md-center{-webkit-box-pack:center!important;-webkit-justify-content:center!important;-ms-flex-pack:center!important;justify-content:center!important}.justify-content-md-between{-webkit-box-pack:justify!important;-webkit-justify-content:space-between!important;-ms-flex-pack:justify!important;justify-content:space-between!important}.justify-content-md-around{-webkit-justify-content:space-around!important;-ms-flex-pack:distribute!important;justify-content:space-around!important}.align-items-md-start{-webkit-box-align:start!important;-webkit-align-items:flex-start!important;-ms-flex-align:start!important;align-items:flex-start!important}.align-items-md-end{-webkit-box-align:end!important;-webkit-align-items:flex-end!important;-ms-flex-align:end!important;align-items:flex-end!important}.align-items-md-center{-webkit-box-align:center!important;-webkit-align-items:center!important;-ms-flex-align:center!important;align-items:center!important}.align-items-md-baseline{-webkit-box-align:baseline!important;-webkit-align-items:baseline!important;-ms-flex-align:baseline!important;align-items:baseline!important}.align-items-md-stretch{-webkit-box-align:stretch!important;-webkit-align-items:stretch!important;-ms-flex-align:stretch!important;align-items:stretch!important}.align-content-md-start{-webkit-align-content:flex-start!important;-ms-flex-line-pack:start!important;align-content:flex-start!important}.align-content-md-end{-webkit-align-content:flex-end!important;-ms-flex-line-pack:end!important;align-content:flex-end!important}.align-content-md-center{-webkit-align-content:center!important;-ms-flex-line-pack:center!important;align-content:center!important}.align-content-md-between{-webkit-align-content:space-between!important;-ms-flex-line-pack:justify!important;align-content:space-between!important}.align-content-md-around{-webkit-align-content:space-around!important;-ms-flex-line-pack:distribute!important;align-content:space-around!important}.align-content-md-stretch{-webkit-align-content:stretch!important;-ms-flex-line-pack:stretch!important;align-content:stretch!important}.align-self-md-auto{-webkit-align-self:auto!important;-ms-flex-item-align:auto!important;align-self:auto!important}.align-self-md-start{-webkit-align-self:flex-start!important;-ms-flex-item-align:start!important;align-self:flex-start!important}.align-self-md-end{-webkit-align-self:flex-end!important;-ms-flex-item-align:end!important;align-self:flex-end!important}.align-self-md-center{-webkit-align-self:center!important;-ms-flex-item-align:center!important;align-self:center!important}.align-self-md-baseline{-webkit-align-self:baseline!important;-ms-flex-item-align:baseline!important;align-self:baseline!important}.align-self-md-stretch{-webkit-align-self:stretch!important;-ms-flex-item-align:stretch!important;align-self:stretch!important}}@media (min-width:992px){.flex-lg-row{-webkit-box-orient:horizontal!important;-webkit-box-direction:normal!important;-webkit-flex-direction:row!important;-ms-flex-direction:row!important;flex-direction:row!important}.flex-lg-column{-webkit-box-orient:vertical!important;-webkit-box-direction:normal!important;-webkit-flex-direction:column!important;-ms-flex-direction:column!important;flex-direction:column!important}.flex-lg-row-reverse{-webkit-box-orient:horizontal!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:row-reverse!important;-ms-flex-direction:row-reverse!important;flex-direction:row-reverse!important}.flex-lg-column-reverse{-webkit-box-orient:vertical!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:column-reverse!important;-ms-flex-direction:column-reverse!important;flex-direction:column-reverse!important}.flex-lg-wrap{-webkit-flex-wrap:wrap!important;-ms-flex-wrap:wrap!important;flex-wrap:wrap!important}.flex-lg-nowrap{-webkit-flex-wrap:nowrap!important;-ms-flex-wrap:nowrap!important;flex-wrap:nowrap!important}.flex-lg-wrap-reverse{-webkit-flex-wrap:wrap-reverse!important;-ms-flex-wrap:wrap-reverse!important;flex-wrap:wrap-reverse!important}.flex-lg-fill{-webkit-box-flex:1!important;-webkit-flex:1 1 auto!important;-ms-flex:1 1 auto!important;flex:1 1 auto!important}.flex-lg-grow-0{-webkit-box-flex:0!important;-webkit-flex-grow:0!important;-ms-flex-positive:0!important;flex-grow:0!important}.flex-lg-grow-1{-webkit-box-flex:1!important;-webkit-flex-grow:1!important;-ms-flex-positive:1!important;flex-grow:1!important}.flex-lg-shrink-0{-webkit-flex-shrink:0!important;-ms-flex-negative:0!important;flex-shrink:0!important}.flex-lg-shrink-1{-webkit-flex-shrink:1!important;-ms-flex-negative:1!important;flex-shrink:1!important}.justify-content-lg-start{-webkit-box-pack:start!important;-webkit-justify-content:flex-start!important;-ms-flex-pack:start!important;justify-content:flex-start!important}.justify-content-lg-end{-webkit-box-pack:end!important;-webkit-justify-content:flex-end!important;-ms-flex-pack:end!important;justify-content:flex-end!important}.justify-content-lg-center{-webkit-box-pack:center!important;-webkit-justify-content:center!important;-ms-flex-pack:center!important;justify-content:center!important}.justify-content-lg-between{-webkit-box-pack:justify!important;-webkit-justify-content:space-between!important;-ms-flex-pack:justify!important;justify-content:space-between!important}.justify-content-lg-around{-webkit-justify-content:space-around!important;-ms-flex-pack:distribute!important;justify-content:space-around!important}.align-items-lg-start{-webkit-box-align:start!important;-webkit-align-items:flex-start!important;-ms-flex-align:start!important;align-items:flex-start!important}.align-items-lg-end{-webkit-box-align:end!important;-webkit-align-items:flex-end!important;-ms-flex-align:end!important;align-items:flex-end!important}.align-items-lg-center{-webkit-box-align:center!important;-webkit-align-items:center!important;-ms-flex-align:center!important;align-items:center!important}.align-items-lg-baseline{-webkit-box-align:baseline!important;-webkit-align-items:baseline!important;-ms-flex-align:baseline!important;align-items:baseline!important}.align-items-lg-stretch{-webkit-box-align:stretch!important;-webkit-align-items:stretch!important;-ms-flex-align:stretch!important;align-items:stretch!important}.align-content-lg-start{-webkit-align-content:flex-start!important;-ms-flex-line-pack:start!important;align-content:flex-start!important}.align-content-lg-end{-webkit-align-content:flex-end!important;-ms-flex-line-pack:end!important;align-content:flex-end!important}.align-content-lg-center{-webkit-align-content:center!important;-ms-flex-line-pack:center!important;align-content:center!important}.align-content-lg-between{-webkit-align-content:space-between!important;-ms-flex-line-pack:justify!important;align-content:space-between!important}.align-content-lg-around{-webkit-align-content:space-around!important;-ms-flex-line-pack:distribute!important;align-content:space-around!important}.align-content-lg-stretch{-webkit-align-content:stretch!important;-ms-flex-line-pack:stretch!important;align-content:stretch!important}.align-self-lg-auto{-webkit-align-self:auto!important;-ms-flex-item-align:auto!important;align-self:auto!important}.align-self-lg-start{-webkit-align-self:flex-start!important;-ms-flex-item-align:start!important;align-self:flex-start!important}.align-self-lg-end{-webkit-align-self:flex-end!important;-ms-flex-item-align:end!important;align-self:flex-end!important}.align-self-lg-center{-webkit-align-self:center!important;-ms-flex-item-align:center!important;align-self:center!important}.align-self-lg-baseline{-webkit-align-self:baseline!important;-ms-flex-item-align:baseline!important;align-self:baseline!important}.align-self-lg-stretch{-webkit-align-self:stretch!important;-ms-flex-item-align:stretch!important;align-self:stretch!important}}@media (min-width:1200px){.flex-xl-row{-webkit-box-orient:horizontal!important;-webkit-box-direction:normal!important;-webkit-flex-direction:row!important;-ms-flex-direction:row!important;flex-direction:row!important}.flex-xl-column{-webkit-box-orient:vertical!important;-webkit-box-direction:normal!important;-webkit-flex-direction:column!important;-ms-flex-direction:column!important;flex-direction:column!important}.flex-xl-row-reverse{-webkit-box-orient:horizontal!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:row-reverse!important;-ms-flex-direction:row-reverse!important;flex-direction:row-reverse!important}.flex-xl-column-reverse{-webkit-box-orient:vertical!important;-webkit-box-direction:reverse!important;-webkit-flex-direction:column-reverse!important;-ms-flex-direction:column-reverse!important;flex-direction:column-reverse!important}.flex-xl-wrap{-webkit-flex-wrap:wrap!important;-ms-flex-wrap:wrap!important;flex-wrap:wrap!important}.flex-xl-nowrap{-webkit-flex-wrap:nowrap!important;-ms-flex-wrap:nowrap!important;flex-wrap:nowrap!important}.flex-xl-wrap-reverse{-webkit-flex-wrap:wrap-reverse!important;-ms-flex-wrap:wrap-reverse!important;flex-wrap:wrap-reverse!important}.flex-xl-fill{-webkit-box-flex:1!important;-webkit-flex:1 1 auto!important;-ms-flex:1 1 auto!important;flex:1 1 auto!important}.flex-xl-grow-0{-webkit-box-flex:0!important;-webkit-flex-grow:0!important;-ms-flex-positive:0!important;flex-grow:0!important}.flex-xl-grow-1{-webkit-box-flex:1!important;-webkit-flex-grow:1!important;-ms-flex-positive:1!important;flex-grow:1!important}.flex-xl-shrink-0{-webkit-flex-shrink:0!important;-ms-flex-negative:0!important;flex-shrink:0!important}.flex-xl-shrink-1{-webkit-flex-shrink:1!important;-ms-flex-negative:1!important;flex-shrink:1!important}.justify-content-xl-start{-webkit-box-pack:start!important;-webkit-justify-content:flex-start!important;-ms-flex-pack:start!important;justify-content:flex-start!important}.justify-content-xl-end{-webkit-box-pack:end!important;-webkit-justify-content:flex-end!important;-ms-flex-pack:end!important;justify-content:flex-end!important}.justify-content-xl-center{-webkit-box-pack:center!important;-webkit-justify-content:center!important;-ms-flex-pack:center!important;justify-content:center!important}.justify-content-xl-between{-webkit-box-pack:justify!important;-webkit-justify-content:space-between!important;-ms-flex-pack:justify!important;justify-content:space-between!important}.justify-content-xl-around{-webkit-justify-content:space-around!important;-ms-flex-pack:distribute!important;justify-content:space-around!important}.align-items-xl-start{-webkit-box-align:start!important;-webkit-align-items:flex-start!important;-ms-flex-align:start!important;align-items:flex-start!important}.align-items-xl-end{-webkit-box-align:end!important;-webkit-align-items:flex-end!important;-ms-flex-align:end!important;align-items:flex-end!important}.align-items-xl-center{-webkit-box-align:center!important;-webkit-align-items:center!important;-ms-flex-align:center!important;align-items:center!important}.align-items-xl-baseline{-webkit-box-align:baseline!important;-webkit-align-items:baseline!important;-ms-flex-align:baseline!important;align-items:baseline!important}.align-items-xl-stretch{-webkit-box-align:stretch!important;-webkit-align-items:stretch!important;-ms-flex-align:stretch!important;align-items:stretch!important}.align-content-xl-start{-webkit-align-content:flex-start!important;-ms-flex-line-pack:start!important;align-content:flex-start!important}.align-content-xl-end{-webkit-align-content:flex-end!important;-ms-flex-line-pack:end!important;align-content:flex-end!important}.align-content-xl-center{-webkit-align-content:center!important;-ms-flex-line-pack:center!important;align-content:center!important}.align-content-xl-between{-webkit-align-content:space-between!important;-ms-flex-line-pack:justify!important;align-content:space-between!important}.align-content-xl-around{-webkit-align-content:space-around!important;-ms-flex-line-pack:distribute!important;align-content:space-around!important}.align-content-xl-stretch{-webkit-align-content:stretch!important;-ms-flex-line-pack:stretch!important;align-content:stretch!important}.align-self-xl-auto{-webkit-align-self:auto!important;-ms-flex-item-align:auto!important;align-self:auto!important}.align-self-xl-start{-webkit-align-self:flex-start!important;-ms-flex-item-align:start!important;align-self:flex-start!important}.align-self-xl-end{-webkit-align-self:flex-end!important;-ms-flex-item-align:end!important;align-self:flex-end!important}.align-self-xl-center{-webkit-align-self:center!important;-ms-flex-item-align:center!important;align-self:center!important}.align-self-xl-baseline{-webkit-align-self:baseline!important;-ms-flex-item-align:baseline!important;align-self:baseline!important}.align-self-xl-stretch{-webkit-align-self:stretch!important;-ms-flex-item-align:stretch!important;align-self:stretch!important}}.float-left{float:left!important}.float-right{float:right!important}.float-none{float:none!important}@media (min-width:576px){.float-sm-left{float:left!important}.float-sm-right{float:right!important}.float-sm-none{float:none!important}}@media (min-width:768px){.float-md-left{float:left!important}.float-md-right{float:right!important}.float-md-none{float:none!important}}@media (min-width:992px){.float-lg-left{float:left!important}.float-lg-right{float:right!important}.float-lg-none{float:none!important}}@media (min-width:1200px){.float-xl-left{float:left!important}.float-xl-right{float:right!important}.float-xl-none{float:none!important}}.overflow-auto{overflow:auto!important}.overflow-hidden{overflow:hidden!important}.position-static{position:static!important}.position-relative{position:relative!important}.position-absolute{position:absolute!important}.position-fixed{position:fixed!important}.position-sticky{position:-webkit-sticky!important;position:sticky!important}.fixed-top{position:fixed;top:0;right:0;left:0;z-index:1030}.fixed-bottom{position:fixed;right:0;bottom:0;left:0;z-index:1030}@supports ((position:-webkit-sticky) or (position:sticky)){.sticky-top{position:-webkit-sticky;position:sticky;top:0;z-index:1020}}.sr-only{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.sr-only-focusable:active,.sr-only-focusable:focus{position:static;width:auto;height:auto;overflow:visible;clip:auto;white-space:normal}.shadow-sm{-webkit-box-shadow:0 .125rem .25rem rgba(0,0,0,.075)!important;box-shadow:0 .125rem .25rem rgba(0,0,0,.075)!important}.shadow{-webkit-box-shadow:0 .5rem 1rem rgba(0,0,0,.15)!important;box-shadow:0 .5rem 1rem rgba(0,0,0,.15)!important}.shadow-lg{-webkit-box-shadow:0 1rem 3rem rgba(0,0,0,.175)!important;box-shadow:0 1rem 3rem rgba(0,0,0,.175)!important}.shadow-none{-webkit-box-shadow:none!important;box-shadow:none!important}.w-25{width:25%!important}.w-50{width:50%!important}.w-75{width:75%!important}.w-100{width:100%!important}.w-auto{width:auto!important}.h-25{height:25%!important}.h-50{height:50%!important}.h-75{height:75%!important}.h-100{height:100%!important}.h-auto{height:auto!important}.mw-100{max-width:100%!important}.mh-100{max-height:100%!important}.min-vw-100{min-width:100vw!important}.min-vh-100{min-height:100vh!important}.vw-100{width:100vw!important}.vh-100{height:100vh!important}.stretched-link::after{position:absolute;top:0;right:0;bottom:0;left:0;z-index:1;pointer-events:auto;content:"";background-color:rgba(0,0,0,0)}.m-0{margin:0!important}.mt-0,.my-0{margin-top:0!important}.mr-0,.mx-0{margin-right:0!important}.mb-0,.my-0{margin-bottom:0!important}.ml-0,.mx-0{margin-left:0!important}.m-1{margin:.25rem!important}.mt-1,.my-1{margin-top:.25rem!important}.mr-1,.mx-1{margin-right:.25rem!important}.mb-1,.my-1{margin-bottom:.25rem!important}.ml-1,.mx-1{margin-left:.25rem!important}.m-2{margin:.5rem!important}.mt-2,.my-2{margin-top:.5rem!important}.mr-2,.mx-2{margin-right:.5rem!important}.mb-2,.my-2{margin-bottom:.5rem!important}.ml-2,.mx-2{margin-left:.5rem!important}.m-3{margin:1rem!important}.mt-3,.my-3{margin-top:1rem!important}.mr-3,.mx-3{margin-right:1rem!important}.mb-3,.my-3{margin-bottom:1rem!important}.ml-3,.mx-3{margin-left:1rem!important}.m-4{margin:1.5rem!important}.mt-4,.my-4{margin-top:1.5rem!important}.mr-4,.mx-4{margin-right:1.5rem!important}.mb-4,.my-4{margin-bottom:1.5rem!important}.ml-4,.mx-4{margin-left:1.5rem!important}.m-5{margin:3rem!important}.mt-5,.my-5{margin-top:3rem!important}.mr-5,.mx-5{margin-right:3rem!important}.mb-5,.my-5{margin-bottom:3rem!important}.ml-5,.mx-5{margin-left:3rem!important}.p-0{padding:0!important}.pt-0,.py-0{padding-top:0!important}.pr-0,.px-0{padding-right:0!important}.pb-0,.py-0{padding-bottom:0!important}.pl-0,.px-0{padding-left:0!important}.p-1{padding:.25rem!important}.pt-1,.py-1{padding-top:.25rem!important}.pr-1,.px-1{padding-right:.25rem!important}.pb-1,.py-1{padding-bottom:.25rem!important}.pl-1,.px-1{padding-left:.25rem!important}.p-2{padding:.5rem!important}.pt-2,.py-2{padding-top:.5rem!important}.pr-2,.px-2{padding-right:.5rem!important}.pb-2,.py-2{padding-bottom:.5rem!important}.pl-2,.px-2{padding-left:.5rem!important}.p-3{padding:1rem!important}.pt-3,.py-3{padding-top:1rem!important}.pr-3,.px-3{padding-right:1rem!important}.pb-3,.py-3{padding-bottom:1rem!important}.pl-3,.px-3{padding-left:1rem!important}.p-4{padding:1.5rem!important}.pt-4,.py-4{padding-top:1.5rem!important}.pr-4,.px-4{padding-right:1.5rem!important}.pb-4,.py-4{padding-bottom:1.5rem!important}.pl-4,.px-4{padding-left:1.5rem!important}.p-5{padding:3rem!important}.pt-5,.py-5{padding-top:3rem!important}.pr-5,.px-5{padding-right:3rem!important}.pb-5,.py-5{padding-bottom:3rem!important}.pl-5,.px-5{padding-left:3rem!important}.m-n1{margin:-.25rem!important}.mt-n1,.my-n1{margin-top:-.25rem!important}.mr-n1,.mx-n1{margin-right:-.25rem!important}.mb-n1,.my-n1{margin-bottom:-.25rem!important}.ml-n1,.mx-n1{margin-left:-.25rem!important}.m-n2{margin:-.5rem!important}.mt-n2,.my-n2{margin-top:-.5rem!important}.mr-n2,.mx-n2{margin-right:-.5rem!important}.mb-n2,.my-n2{margin-bottom:-.5rem!important}.ml-n2,.mx-n2{margin-left:-.5rem!important}.m-n3{margin:-1rem!important}.mt-n3,.my-n3{margin-top:-1rem!important}.mr-n3,.mx-n3{margin-right:-1rem!important}.mb-n3,.my-n3{margin-bottom:-1rem!important}.ml-n3,.mx-n3{margin-left:-1rem!important}.m-n4{margin:-1.5rem!important}.mt-n4,.my-n4{margin-top:-1.5rem!important}.mr-n4,.mx-n4{margin-right:-1.5rem!important}.mb-n4,.my-n4{margin-bottom:-1.5rem!important}.ml-n4,.mx-n4{margin-left:-1.5rem!important}.m-n5{margin:-3rem!important}.mt-n5,.my-n5{margin-top:-3rem!important}.mr-n5,.mx-n5{margin-right:-3rem!important}.mb-n5,.my-n5{margin-bottom:-3rem!important}.ml-n5,.mx-n5{margin-left:-3rem!important}.m-auto{margin:auto!important}.mt-auto,.my-auto{margin-top:auto!important}.mr-auto,.mx-auto{margin-right:auto!important}.mb-auto,.my-auto{margin-bottom:auto!important}.ml-auto,.mx-auto{margin-left:auto!important}@media (min-width:576px){.m-sm-0{margin:0!important}.mt-sm-0,.my-sm-0{margin-top:0!important}.mr-sm-0,.mx-sm-0{margin-right:0!important}.mb-sm-0,.my-sm-0{margin-bottom:0!important}.ml-sm-0,.mx-sm-0{margin-left:0!important}.m-sm-1{margin:.25rem!important}.mt-sm-1,.my-sm-1{margin-top:.25rem!important}.mr-sm-1,.mx-sm-1{margin-right:.25rem!important}.mb-sm-1,.my-sm-1{margin-bottom:.25rem!important}.ml-sm-1,.mx-sm-1{margin-left:.25rem!important}.m-sm-2{margin:.5rem!important}.mt-sm-2,.my-sm-2{margin-top:.5rem!important}.mr-sm-2,.mx-sm-2{margin-right:.5rem!important}.mb-sm-2,.my-sm-2{margin-bottom:.5rem!important}.ml-sm-2,.mx-sm-2{margin-left:.5rem!important}.m-sm-3{margin:1rem!important}.mt-sm-3,.my-sm-3{margin-top:1rem!important}.mr-sm-3,.mx-sm-3{margin-right:1rem!important}.mb-sm-3,.my-sm-3{margin-bottom:1rem!important}.ml-sm-3,.mx-sm-3{margin-left:1rem!important}.m-sm-4{margin:1.5rem!important}.mt-sm-4,.my-sm-4{margin-top:1.5rem!important}.mr-sm-4,.mx-sm-4{margin-right:1.5rem!important}.mb-sm-4,.my-sm-4{margin-bottom:1.5rem!important}.ml-sm-4,.mx-sm-4{margin-left:1.5rem!important}.m-sm-5{margin:3rem!important}.mt-sm-5,.my-sm-5{margin-top:3rem!important}.mr-sm-5,.mx-sm-5{margin-right:3rem!important}.mb-sm-5,.my-sm-5{margin-bottom:3rem!important}.ml-sm-5,.mx-sm-5{margin-left:3rem!important}.p-sm-0{padding:0!important}.pt-sm-0,.py-sm-0{padding-top:0!important}.pr-sm-0,.px-sm-0{padding-right:0!important}.pb-sm-0,.py-sm-0{padding-bottom:0!important}.pl-sm-0,.px-sm-0{padding-left:0!important}.p-sm-1{padding:.25rem!important}.pt-sm-1,.py-sm-1{padding-top:.25rem!important}.pr-sm-1,.px-sm-1{padding-right:.25rem!important}.pb-sm-1,.py-sm-1{padding-bottom:.25rem!important}.pl-sm-1,.px-sm-1{padding-left:.25rem!important}.p-sm-2{padding:.5rem!important}.pt-sm-2,.py-sm-2{padding-top:.5rem!important}.pr-sm-2,.px-sm-2{padding-right:.5rem!important}.pb-sm-2,.py-sm-2{padding-bottom:.5rem!important}.pl-sm-2,.px-sm-2{padding-left:.5rem!important}.p-sm-3{padding:1rem!important}.pt-sm-3,.py-sm-3{padding-top:1rem!important}.pr-sm-3,.px-sm-3{padding-right:1rem!important}.pb-sm-3,.py-sm-3{padding-bottom:1rem!important}.pl-sm-3,.px-sm-3{padding-left:1rem!important}.p-sm-4{padding:1.5rem!important}.pt-sm-4,.py-sm-4{padding-top:1.5rem!important}.pr-sm-4,.px-sm-4{padding-right:1.5rem!important}.pb-sm-4,.py-sm-4{padding-bottom:1.5rem!important}.pl-sm-4,.px-sm-4{padding-left:1.5rem!important}.p-sm-5{padding:3rem!important}.pt-sm-5,.py-sm-5{padding-top:3rem!important}.pr-sm-5,.px-sm-5{padding-right:3rem!important}.pb-sm-5,.py-sm-5{padding-bottom:3rem!important}.pl-sm-5,.px-sm-5{padding-left:3rem!important}.m-sm-n1{margin:-.25rem!important}.mt-sm-n1,.my-sm-n1{margin-top:-.25rem!important}.mr-sm-n1,.mx-sm-n1{margin-right:-.25rem!important}.mb-sm-n1,.my-sm-n1{margin-bottom:-.25rem!important}.ml-sm-n1,.mx-sm-n1{margin-left:-.25rem!important}.m-sm-n2{margin:-.5rem!important}.mt-sm-n2,.my-sm-n2{margin-top:-.5rem!important}.mr-sm-n2,.mx-sm-n2{margin-right:-.5rem!important}.mb-sm-n2,.my-sm-n2{margin-bottom:-.5rem!important}.ml-sm-n2,.mx-sm-n2{margin-left:-.5rem!important}.m-sm-n3{margin:-1rem!important}.mt-sm-n3,.my-sm-n3{margin-top:-1rem!important}.mr-sm-n3,.mx-sm-n3{margin-right:-1rem!important}.mb-sm-n3,.my-sm-n3{margin-bottom:-1rem!important}.ml-sm-n3,.mx-sm-n3{margin-left:-1rem!important}.m-sm-n4{margin:-1.5rem!important}.mt-sm-n4,.my-sm-n4{margin-top:-1.5rem!important}.mr-sm-n4,.mx-sm-n4{margin-right:-1.5rem!important}.mb-sm-n4,.my-sm-n4{margin-bottom:-1.5rem!important}.ml-sm-n4,.mx-sm-n4{margin-left:-1.5rem!important}.m-sm-n5{margin:-3rem!important}.mt-sm-n5,.my-sm-n5{margin-top:-3rem!important}.mr-sm-n5,.mx-sm-n5{margin-right:-3rem!important}.mb-sm-n5,.my-sm-n5{margin-bottom:-3rem!important}.ml-sm-n5,.mx-sm-n5{margin-left:-3rem!important}.m-sm-auto{margin:auto!important}.mt-sm-auto,.my-sm-auto{margin-top:auto!important}.mr-sm-auto,.mx-sm-auto{margin-right:auto!important}.mb-sm-auto,.my-sm-auto{margin-bottom:auto!important}.ml-sm-auto,.mx-sm-auto{margin-left:auto!important}}@media (min-width:768px){.m-md-0{margin:0!important}.mt-md-0,.my-md-0{margin-top:0!important}.mr-md-0,.mx-md-0{margin-right:0!important}.mb-md-0,.my-md-0{margin-bottom:0!important}.ml-md-0,.mx-md-0{margin-left:0!important}.m-md-1{margin:.25rem!important}.mt-md-1,.my-md-1{margin-top:.25rem!important}.mr-md-1,.mx-md-1{margin-right:.25rem!important}.mb-md-1,.my-md-1{margin-bottom:.25rem!important}.ml-md-1,.mx-md-1{margin-left:.25rem!important}.m-md-2{margin:.5rem!important}.mt-md-2,.my-md-2{margin-top:.5rem!important}.mr-md-2,.mx-md-2{margin-right:.5rem!important}.mb-md-2,.my-md-2{margin-bottom:.5rem!important}.ml-md-2,.mx-md-2{margin-left:.5rem!important}.m-md-3{margin:1rem!important}.mt-md-3,.my-md-3{margin-top:1rem!important}.mr-md-3,.mx-md-3{margin-right:1rem!important}.mb-md-3,.my-md-3{margin-bottom:1rem!important}.ml-md-3,.mx-md-3{margin-left:1rem!important}.m-md-4{margin:1.5rem!important}.mt-md-4,.my-md-4{margin-top:1.5rem!important}.mr-md-4,.mx-md-4{margin-right:1.5rem!important}.mb-md-4,.my-md-4{margin-bottom:1.5rem!important}.ml-md-4,.mx-md-4{margin-left:1.5rem!important}.m-md-5{margin:3rem!important}.mt-md-5,.my-md-5{margin-top:3rem!important}.mr-md-5,.mx-md-5{margin-right:3rem!important}.mb-md-5,.my-md-5{margin-bottom:3rem!important}.ml-md-5,.mx-md-5{margin-left:3rem!important}.p-md-0{padding:0!important}.pt-md-0,.py-md-0{padding-top:0!important}.pr-md-0,.px-md-0{padding-right:0!important}.pb-md-0,.py-md-0{padding-bottom:0!important}.pl-md-0,.px-md-0{padding-left:0!important}.p-md-1{padding:.25rem!important}.pt-md-1,.py-md-1{padding-top:.25rem!important}.pr-md-1,.px-md-1{padding-right:.25rem!important}.pb-md-1,.py-md-1{padding-bottom:.25rem!important}.pl-md-1,.px-md-1{padding-left:.25rem!important}.p-md-2{padding:.5rem!important}.pt-md-2,.py-md-2{padding-top:.5rem!important}.pr-md-2,.px-md-2{padding-right:.5rem!important}.pb-md-2,.py-md-2{padding-bottom:.5rem!important}.pl-md-2,.px-md-2{padding-left:.5rem!important}.p-md-3{padding:1rem!important}.pt-md-3,.py-md-3{padding-top:1rem!important}.pr-md-3,.px-md-3{padding-right:1rem!important}.pb-md-3,.py-md-3{padding-bottom:1rem!important}.pl-md-3,.px-md-3{padding-left:1rem!important}.p-md-4{padding:1.5rem!important}.pt-md-4,.py-md-4{padding-top:1.5rem!important}.pr-md-4,.px-md-4{padding-right:1.5rem!important}.pb-md-4,.py-md-4{padding-bottom:1.5rem!important}.pl-md-4,.px-md-4{padding-left:1.5rem!important}.p-md-5{padding:3rem!important}.pt-md-5,.py-md-5{padding-top:3rem!important}.pr-md-5,.px-md-5{padding-right:3rem!important}.pb-md-5,.py-md-5{padding-bottom:3rem!important}.pl-md-5,.px-md-5{padding-left:3rem!important}.m-md-n1{margin:-.25rem!important}.mt-md-n1,.my-md-n1{margin-top:-.25rem!important}.mr-md-n1,.mx-md-n1{margin-right:-.25rem!important}.mb-md-n1,.my-md-n1{margin-bottom:-.25rem!important}.ml-md-n1,.mx-md-n1{margin-left:-.25rem!important}.m-md-n2{margin:-.5rem!important}.mt-md-n2,.my-md-n2{margin-top:-.5rem!important}.mr-md-n2,.mx-md-n2{margin-right:-.5rem!important}.mb-md-n2,.my-md-n2{margin-bottom:-.5rem!important}.ml-md-n2,.mx-md-n2{margin-left:-.5rem!important}.m-md-n3{margin:-1rem!important}.mt-md-n3,.my-md-n3{margin-top:-1rem!important}.mr-md-n3,.mx-md-n3{margin-right:-1rem!important}.mb-md-n3,.my-md-n3{margin-bottom:-1rem!important}.ml-md-n3,.mx-md-n3{margin-left:-1rem!important}.m-md-n4{margin:-1.5rem!important}.mt-md-n4,.my-md-n4{margin-top:-1.5rem!important}.mr-md-n4,.mx-md-n4{margin-right:-1.5rem!important}.mb-md-n4,.my-md-n4{margin-bottom:-1.5rem!important}.ml-md-n4,.mx-md-n4{margin-left:-1.5rem!important}.m-md-n5{margin:-3rem!important}.mt-md-n5,.my-md-n5{margin-top:-3rem!important}.mr-md-n5,.mx-md-n5{margin-right:-3rem!important}.mb-md-n5,.my-md-n5{margin-bottom:-3rem!important}.ml-md-n5,.mx-md-n5{margin-left:-3rem!important}.m-md-auto{margin:auto!important}.mt-md-auto,.my-md-auto{margin-top:auto!important}.mr-md-auto,.mx-md-auto{margin-right:auto!important}.mb-md-auto,.my-md-auto{margin-bottom:auto!important}.ml-md-auto,.mx-md-auto{margin-left:auto!important}}@media (min-width:992px){.m-lg-0{margin:0!important}.mt-lg-0,.my-lg-0{margin-top:0!important}.mr-lg-0,.mx-lg-0{margin-right:0!important}.mb-lg-0,.my-lg-0{margin-bottom:0!important}.ml-lg-0,.mx-lg-0{margin-left:0!important}.m-lg-1{margin:.25rem!important}.mt-lg-1,.my-lg-1{margin-top:.25rem!important}.mr-lg-1,.mx-lg-1{margin-right:.25rem!important}.mb-lg-1,.my-lg-1{margin-bottom:.25rem!important}.ml-lg-1,.mx-lg-1{margin-left:.25rem!important}.m-lg-2{margin:.5rem!important}.mt-lg-2,.my-lg-2{margin-top:.5rem!important}.mr-lg-2,.mx-lg-2{margin-right:.5rem!important}.mb-lg-2,.my-lg-2{margin-bottom:.5rem!important}.ml-lg-2,.mx-lg-2{margin-left:.5rem!important}.m-lg-3{margin:1rem!important}.mt-lg-3,.my-lg-3{margin-top:1rem!important}.mr-lg-3,.mx-lg-3{margin-right:1rem!important}.mb-lg-3,.my-lg-3{margin-bottom:1rem!important}.ml-lg-3,.mx-lg-3{margin-left:1rem!important}.m-lg-4{margin:1.5rem!important}.mt-lg-4,.my-lg-4{margin-top:1.5rem!important}.mr-lg-4,.mx-lg-4{margin-right:1.5rem!important}.mb-lg-4,.my-lg-4{margin-bottom:1.5rem!important}.ml-lg-4,.mx-lg-4{margin-left:1.5rem!important}.m-lg-5{margin:3rem!important}.mt-lg-5,.my-lg-5{margin-top:3rem!important}.mr-lg-5,.mx-lg-5{margin-right:3rem!important}.mb-lg-5,.my-lg-5{margin-bottom:3rem!important}.ml-lg-5,.mx-lg-5{margin-left:3rem!important}.p-lg-0{padding:0!important}.pt-lg-0,.py-lg-0{padding-top:0!important}.pr-lg-0,.px-lg-0{padding-right:0!important}.pb-lg-0,.py-lg-0{padding-bottom:0!important}.pl-lg-0,.px-lg-0{padding-left:0!important}.p-lg-1{padding:.25rem!important}.pt-lg-1,.py-lg-1{padding-top:.25rem!important}.pr-lg-1,.px-lg-1{padding-right:.25rem!important}.pb-lg-1,.py-lg-1{padding-bottom:.25rem!important}.pl-lg-1,.px-lg-1{padding-left:.25rem!important}.p-lg-2{padding:.5rem!important}.pt-lg-2,.py-lg-2{padding-top:.5rem!important}.pr-lg-2,.px-lg-2{padding-right:.5rem!important}.pb-lg-2,.py-lg-2{padding-bottom:.5rem!important}.pl-lg-2,.px-lg-2{padding-left:.5rem!important}.p-lg-3{padding:1rem!important}.pt-lg-3,.py-lg-3{padding-top:1rem!important}.pr-lg-3,.px-lg-3{padding-right:1rem!important}.pb-lg-3,.py-lg-3{padding-bottom:1rem!important}.pl-lg-3,.px-lg-3{padding-left:1rem!important}.p-lg-4{padding:1.5rem!important}.pt-lg-4,.py-lg-4{padding-top:1.5rem!important}.pr-lg-4,.px-lg-4{padding-right:1.5rem!important}.pb-lg-4,.py-lg-4{padding-bottom:1.5rem!important}.pl-lg-4,.px-lg-4{padding-left:1.5rem!important}.p-lg-5{padding:3rem!important}.pt-lg-5,.py-lg-5{padding-top:3rem!important}.pr-lg-5,.px-lg-5{padding-right:3rem!important}.pb-lg-5,.py-lg-5{padding-bottom:3rem!important}.pl-lg-5,.px-lg-5{padding-left:3rem!important}.m-lg-n1{margin:-.25rem!important}.mt-lg-n1,.my-lg-n1{margin-top:-.25rem!important}.mr-lg-n1,.mx-lg-n1{margin-right:-.25rem!important}.mb-lg-n1,.my-lg-n1{margin-bottom:-.25rem!important}.ml-lg-n1,.mx-lg-n1{margin-left:-.25rem!important}.m-lg-n2{margin:-.5rem!important}.mt-lg-n2,.my-lg-n2{margin-top:-.5rem!important}.mr-lg-n2,.mx-lg-n2{margin-right:-.5rem!important}.mb-lg-n2,.my-lg-n2{margin-bottom:-.5rem!important}.ml-lg-n2,.mx-lg-n2{margin-left:-.5rem!important}.m-lg-n3{margin:-1rem!important}.mt-lg-n3,.my-lg-n3{margin-top:-1rem!important}.mr-lg-n3,.mx-lg-n3{margin-right:-1rem!important}.mb-lg-n3,.my-lg-n3{margin-bottom:-1rem!important}.ml-lg-n3,.mx-lg-n3{margin-left:-1rem!important}.m-lg-n4{margin:-1.5rem!important}.mt-lg-n4,.my-lg-n4{margin-top:-1.5rem!important}.mr-lg-n4,.mx-lg-n4{margin-right:-1.5rem!important}.mb-lg-n4,.my-lg-n4{margin-bottom:-1.5rem!important}.ml-lg-n4,.mx-lg-n4{margin-left:-1.5rem!important}.m-lg-n5{margin:-3rem!important}.mt-lg-n5,.my-lg-n5{margin-top:-3rem!important}.mr-lg-n5,.mx-lg-n5{margin-right:-3rem!important}.mb-lg-n5,.my-lg-n5{margin-bottom:-3rem!important}.ml-lg-n5,.mx-lg-n5{margin-left:-3rem!important}.m-lg-auto{margin:auto!important}.mt-lg-auto,.my-lg-auto{margin-top:auto!important}.mr-lg-auto,.mx-lg-auto{margin-right:auto!important}.mb-lg-auto,.my-lg-auto{margin-bottom:auto!important}.ml-lg-auto,.mx-lg-auto{margin-left:auto!important}}@media (min-width:1200px){.m-xl-0{margin:0!important}.mt-xl-0,.my-xl-0{margin-top:0!important}.mr-xl-0,.mx-xl-0{margin-right:0!important}.mb-xl-0,.my-xl-0{margin-bottom:0!important}.ml-xl-0,.mx-xl-0{margin-left:0!important}.m-xl-1{margin:.25rem!important}.mt-xl-1,.my-xl-1{margin-top:.25rem!important}.mr-xl-1,.mx-xl-1{margin-right:.25rem!important}.mb-xl-1,.my-xl-1{margin-bottom:.25rem!important}.ml-xl-1,.mx-xl-1{margin-left:.25rem!important}.m-xl-2{margin:.5rem!important}.mt-xl-2,.my-xl-2{margin-top:.5rem!important}.mr-xl-2,.mx-xl-2{margin-right:.5rem!important}.mb-xl-2,.my-xl-2{margin-bottom:.5rem!important}.ml-xl-2,.mx-xl-2{margin-left:.5rem!important}.m-xl-3{margin:1rem!important}.mt-xl-3,.my-xl-3{margin-top:1rem!important}.mr-xl-3,.mx-xl-3{margin-right:1rem!important}.mb-xl-3,.my-xl-3{margin-bottom:1rem!important}.ml-xl-3,.mx-xl-3{margin-left:1rem!important}.m-xl-4{margin:1.5rem!important}.mt-xl-4,.my-xl-4{margin-top:1.5rem!important}.mr-xl-4,.mx-xl-4{margin-right:1.5rem!important}.mb-xl-4,.my-xl-4{margin-bottom:1.5rem!important}.ml-xl-4,.mx-xl-4{margin-left:1.5rem!important}.m-xl-5{margin:3rem!important}.mt-xl-5,.my-xl-5{margin-top:3rem!important}.mr-xl-5,.mx-xl-5{margin-right:3rem!important}.mb-xl-5,.my-xl-5{margin-bottom:3rem!important}.ml-xl-5,.mx-xl-5{margin-left:3rem!important}.p-xl-0{padding:0!important}.pt-xl-0,.py-xl-0{padding-top:0!important}.pr-xl-0,.px-xl-0{padding-right:0!important}.pb-xl-0,.py-xl-0{padding-bottom:0!important}.pl-xl-0,.px-xl-0{padding-left:0!important}.p-xl-1{padding:.25rem!important}.pt-xl-1,.py-xl-1{padding-top:.25rem!important}.pr-xl-1,.px-xl-1{padding-right:.25rem!important}.pb-xl-1,.py-xl-1{padding-bottom:.25rem!important}.pl-xl-1,.px-xl-1{padding-left:.25rem!important}.p-xl-2{padding:.5rem!important}.pt-xl-2,.py-xl-2{padding-top:.5rem!important}.pr-xl-2,.px-xl-2{padding-right:.5rem!important}.pb-xl-2,.py-xl-2{padding-bottom:.5rem!important}.pl-xl-2,.px-xl-2{padding-left:.5rem!important}.p-xl-3{padding:1rem!important}.pt-xl-3,.py-xl-3{padding-top:1rem!important}.pr-xl-3,.px-xl-3{padding-right:1rem!important}.pb-xl-3,.py-xl-3{padding-bottom:1rem!important}.pl-xl-3,.px-xl-3{padding-left:1rem!important}.p-xl-4{padding:1.5rem!important}.pt-xl-4,.py-xl-4{padding-top:1.5rem!important}.pr-xl-4,.px-xl-4{padding-right:1.5rem!important}.pb-xl-4,.py-xl-4{padding-bottom:1.5rem!important}.pl-xl-4,.px-xl-4{padding-left:1.5rem!important}.p-xl-5{padding:3rem!important}.pt-xl-5,.py-xl-5{padding-top:3rem!important}.pr-xl-5,.px-xl-5{padding-right:3rem!important}.pb-xl-5,.py-xl-5{padding-bottom:3rem!important}.pl-xl-5,.px-xl-5{padding-left:3rem!important}.m-xl-n1{margin:-.25rem!important}.mt-xl-n1,.my-xl-n1{margin-top:-.25rem!important}.mr-xl-n1,.mx-xl-n1{margin-right:-.25rem!important}.mb-xl-n1,.my-xl-n1{margin-bottom:-.25rem!important}.ml-xl-n1,.mx-xl-n1{margin-left:-.25rem!important}.m-xl-n2{margin:-.5rem!important}.mt-xl-n2,.my-xl-n2{margin-top:-.5rem!important}.mr-xl-n2,.mx-xl-n2{margin-right:-.5rem!important}.mb-xl-n2,.my-xl-n2{margin-bottom:-.5rem!important}.ml-xl-n2,.mx-xl-n2{margin-left:-.5rem!important}.m-xl-n3{margin:-1rem!important}.mt-xl-n3,.my-xl-n3{margin-top:-1rem!important}.mr-xl-n3,.mx-xl-n3{margin-right:-1rem!important}.mb-xl-n3,.my-xl-n3{margin-bottom:-1rem!important}.ml-xl-n3,.mx-xl-n3{margin-left:-1rem!important}.m-xl-n4{margin:-1.5rem!important}.mt-xl-n4,.my-xl-n4{margin-top:-1.5rem!important}.mr-xl-n4,.mx-xl-n4{margin-right:-1.5rem!important}.mb-xl-n4,.my-xl-n4{margin-bottom:-1.5rem!important}.ml-xl-n4,.mx-xl-n4{margin-left:-1.5rem!important}.m-xl-n5{margin:-3rem!important}.mt-xl-n5,.my-xl-n5{margin-top:-3rem!important}.mr-xl-n5,.mx-xl-n5{margin-right:-3rem!important}.mb-xl-n5,.my-xl-n5{margin-bottom:-3rem!important}.ml-xl-n5,.mx-xl-n5{margin-left:-3rem!important}.m-xl-auto{margin:auto!important}.mt-xl-auto,.my-xl-auto{margin-top:auto!important}.mr-xl-auto,.mx-xl-auto{margin-right:auto!important}.mb-xl-auto,.my-xl-auto{margin-bottom:auto!important}.ml-xl-auto,.mx-xl-auto{margin-left:auto!important}}.text-monospace{font-family:SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace!important}.text-justify{text-align:justify!important}.text-wrap{white-space:normal!important}.text-nowrap{white-space:nowrap!important}.text-truncate{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.text-left{text-align:left!important}.text-right{text-align:right!important}.text-center{text-align:center!important}@media (min-width:576px){.text-sm-left{text-align:left!important}.text-sm-right{text-align:right!important}.text-sm-center{text-align:center!important}}@media (min-width:768px){.text-md-left{text-align:left!important}.text-md-right{text-align:right!important}.text-md-center{text-align:center!important}}@media (min-width:992px){.text-lg-left{text-align:left!important}.text-lg-right{text-align:right!important}.text-lg-center{text-align:center!important}}@media (min-width:1200px){.text-xl-left{text-align:left!important}.text-xl-right{text-align:right!important}.text-xl-center{text-align:center!important}}.text-lowercase{text-transform:lowercase!important}.text-uppercase{text-transform:uppercase!important}.text-capitalize{text-transform:capitalize!important}.font-weight-light{font-weight:300!important}.font-weight-lighter{font-weight:lighter!important}.font-weight-normal{font-weight:400!important}.font-weight-bold{font-weight:700!important}.font-weight-bolder{font-weight:bolder!important}.font-italic{font-style:italic!important}.text-white{color:#fff!important}.text-primary{color:#714cdf!important}a.text-primary:focus,a.text-primary:hover{color:#4922bd!important}.text-secondary{color:#16a4de!important}a.text-secondary:focus,a.text-secondary:hover{color:#0f7198!important}.text-success{color:#17b06b!important}a.text-success:focus,a.text-success:hover{color:#0e6c42!important}.text-info{color:#2983fe!important}a.text-info:focus,a.text-info:hover{color:#015cd9!important}.text-warning{color:#f97515!important}a.text-warning:focus,a.text-warning:hover{color:#bd5205!important}.text-danger{color:#ff3c5c!important}a.text-danger:focus,a.text-danger:hover{color:#ef0027!important}.text-light{color:#dbebfb!important}a.text-light:focus,a.text-light:hover{color:#96c5f3!important}.text-dark{color:#32334a!important}a.text-dark:focus,a.text-dark:hover{color:#13141c!important}.text-body{color:#e4e2ff!important}.text-muted{color:#81839a!important}.text-black-50{color:rgba(0,0,0,.5)!important}.text-white-50{color:rgba(255,255,255,.5)!important}.text-hide{font:0/0 a;color:transparent;text-shadow:none;background-color:transparent;border:0}.text-decoration-none{text-decoration:none!important}.text-break{word-break:break-word!important;overflow-wrap:break-word!important}.text-reset{color:inherit!important}.visible{visibility:visible!important}.invisible{visibility:hidden!important}@media print{*,::after,::before{text-shadow:none!important;-webkit-box-shadow:none!important;box-shadow:none!important}a:not(.btn){text-decoration:underline}abbr[title]::after{content:" (" attr(title) ")"}pre{white-space:pre-wrap!important}blockquote,pre{border:1px solid #1c1d2c;page-break-inside:avoid}thead{display:table-header-group}img,tr{page-break-inside:avoid}h2,h3,p{orphans:3;widows:3}h2,h3{page-break-after:avoid}@page{size:a3}body{min-width:992px!important}.container{min-width:992px!important}.navbar{display:none}.badge{border:1px solid #000}.table{border-collapse:collapse!important}.table td,.table th{background-color:#fff!important}.table-bordered td,.table-bordered th{border:1px solid #28293e!important}.table-dark{color:inherit}.table-dark tbody+tbody,.table-dark td,.table-dark th,.table-dark thead th{border-color:#28293e}.table .thead-dark th{color:inherit;border-color:#28293e}}.btn-hover-text-primary:active,.btn-hover-text-primary:hover{color:#714cdf!important}.btn-hover-text-secondary:active,.btn-hover-text-secondary:hover{color:#16a4de!important}.btn-hover-text-success:active,.btn-hover-text-success:hover{color:#17b06b!important}.btn-hover-text-info:active,.btn-hover-text-info:hover{color:#2983fe!important}.btn-hover-text-warning:active,.btn-hover-text-warning:hover{color:#f97515!important}.btn-hover-text-danger:active,.btn-hover-text-danger:hover{color:#ff3c5c!important}.btn-hover-text-light:active,.btn-hover-text-light:hover{color:#dbebfb!important}.btn-hover-text-dark:active,.btn-hover-text-dark:hover{color:#32334a!important}.btn-wide{padding-left:50px;padding-right:50px}.display-fix{margin-left:-4px}.btn-pill{border-radius:100px}.lead-lg{font-size:35px}.radius-0{border-radius:0}.text-spacey{line-height:28px}@media (max-width:767.98px){.display-1{font-size:4rem}}@media (max-width:767.98px){.display-2{font-size:3.5rem}}/*body{background-image:url(../images/ng-background-dot.png)}.btn-shadow{margin-left:8px}.btn-shadow.btn-outline-primary,.btn-shadow.btn-primary{border-color:#986edf;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-outline-primary,.btn-shadow.btn-outline-primary.focus,.btn-shadow.btn-outline-primary:focus,.btn-shadow.btn-primary,.btn-shadow.btn-primary.focus,.btn-shadow.btn-primary:focus{-webkit-box-shadow:3px 3px 0 #986edf,2px 2px 0 #986edf,1px 1px 0 #986edf;box-shadow:3px 3px 0 #986edf,2px 2px 0 #986edf,1px 1px 0 #986edf}.btn-shadow.btn-outline-primary:hover,.btn-shadow.btn-primary:hover{-webkit-box-shadow:5px 5px 0 #986edf,4px 4px 0 #986edf,3px 3px 0 #986edf,2px 2px 0 #986edf,1px 1px 0 #986edf;box-shadow:5px 5px 0 #986edf,4px 4px 0 #986edf,3px 3px 0 #986edf,2px 2px 0 #986edf,1px 1px 0 #986edf;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-outline-primary:active,.btn-shadow.btn-primary:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-outline-secondary,.btn-shadow.btn-secondary{border-color:#87c4f2;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-outline-secondary,.btn-shadow.btn-outline-secondary.focus,.btn-shadow.btn-outline-secondary:focus,.btn-shadow.btn-secondary,.btn-shadow.btn-secondary.focus,.btn-shadow.btn-secondary:focus{-webkit-box-shadow:3px 3px 0 #87c4f2,2px 2px 0 #87c4f2,1px 1px 0 #87c4f2;box-shadow:3px 3px 0 #87c4f2,2px 2px 0 #87c4f2,1px 1px 0 #87c4f2}.btn-shadow.btn-outline-secondary:hover,.btn-shadow.btn-secondary:hover{-webkit-box-shadow:5px 5px 0 #87c4f2,4px 4px 0 #87c4f2,3px 3px 0 #87c4f2,2px 2px 0 #87c4f2,1px 1px 0 #87c4f2;box-shadow:5px 5px 0 #87c4f2,4px 4px 0 #87c4f2,3px 3px 0 #87c4f2,2px 2px 0 #87c4f2,1px 1px 0 #87c4f2;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-outline-secondary:active,.btn-shadow.btn-secondary:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-outline-success,.btn-shadow.btn-success{border-color:#43cb8e;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-outline-success,.btn-shadow.btn-outline-success.focus,.btn-shadow.btn-outline-success:focus,.btn-shadow.btn-success,.btn-shadow.btn-success.focus,.btn-shadow.btn-success:focus{-webkit-box-shadow:3px 3px 0 #43cb8e,2px 2px 0 #43cb8e,1px 1px 0 #43cb8e;box-shadow:3px 3px 0 #43cb8e,2px 2px 0 #43cb8e,1px 1px 0 #43cb8e}.btn-shadow.btn-outline-success:hover,.btn-shadow.btn-success:hover{-webkit-box-shadow:5px 5px 0 #43cb8e,4px 4px 0 #43cb8e,3px 3px 0 #43cb8e,2px 2px 0 #43cb8e,1px 1px 0 #43cb8e;box-shadow:5px 5px 0 #43cb8e,4px 4px 0 #43cb8e,3px 3px 0 #43cb8e,2px 2px 0 #43cb8e,1px 1px 0 #43cb8e;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-outline-success:active,.btn-shadow.btn-success:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-info,.btn-shadow.btn-outline-info{border-color:#25a8eb;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-info,.btn-shadow.btn-info.focus,.btn-shadow.btn-info:focus,.btn-shadow.btn-outline-info,.btn-shadow.btn-outline-info.focus,.btn-shadow.btn-outline-info:focus{-webkit-box-shadow:3px 3px 0 #25a8eb,2px 2px 0 #25a8eb,1px 1px 0 #25a8eb;box-shadow:3px 3px 0 #25a8eb,2px 2px 0 #25a8eb,1px 1px 0 #25a8eb}.btn-shadow.btn-info:hover,.btn-shadow.btn-outline-info:hover{-webkit-box-shadow:5px 5px 0 #25a8eb,4px 4px 0 #25a8eb,3px 3px 0 #25a8eb,2px 2px 0 #25a8eb,1px 1px 0 #25a8eb;box-shadow:5px 5px 0 #25a8eb,4px 4px 0 #25a8eb,3px 3px 0 #25a8eb,2px 2px 0 #25a8eb,1px 1px 0 #25a8eb;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-info:active,.btn-shadow.btn-outline-info:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-outline-warning,.btn-shadow.btn-warning{border-color:#f99511;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-outline-warning,.btn-shadow.btn-outline-warning.focus,.btn-shadow.btn-outline-warning:focus,.btn-shadow.btn-warning,.btn-shadow.btn-warning.focus,.btn-shadow.btn-warning:focus{-webkit-box-shadow:3px 3px 0 #f99511,2px 2px 0 #f99511,1px 1px 0 #f99511;box-shadow:3px 3px 0 #f99511,2px 2px 0 #f99511,1px 1px 0 #f99511}.btn-shadow.btn-outline-warning:hover,.btn-shadow.btn-warning:hover{-webkit-box-shadow:5px 5px 0 #f99511,4px 4px 0 #f99511,3px 3px 0 #f99511,2px 2px 0 #f99511,1px 1px 0 #f99511;box-shadow:5px 5px 0 #f99511,4px 4px 0 #f99511,3px 3px 0 #f99511,2px 2px 0 #f99511,1px 1px 0 #f99511;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-outline-warning:active,.btn-shadow.btn-warning:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-danger,.btn-shadow.btn-outline-danger{border-color:#ff707f;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-danger,.btn-shadow.btn-danger.focus,.btn-shadow.btn-danger:focus,.btn-shadow.btn-outline-danger,.btn-shadow.btn-outline-danger.focus,.btn-shadow.btn-outline-danger:focus{-webkit-box-shadow:3px 3px 0 #ff707f,2px 2px 0 #ff707f,1px 1px 0 #ff707f;box-shadow:3px 3px 0 #ff707f,2px 2px 0 #ff707f,1px 1px 0 #ff707f}.btn-shadow.btn-danger:hover,.btn-shadow.btn-outline-danger:hover{-webkit-box-shadow:5px 5px 0 #ff707f,4px 4px 0 #ff707f,3px 3px 0 #ff707f,2px 2px 0 #ff707f,1px 1px 0 #ff707f;box-shadow:5px 5px 0 #ff707f,4px 4px 0 #ff707f,3px 3px 0 #ff707f,2px 2px 0 #ff707f,1px 1px 0 #ff707f;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-danger:active,.btn-shadow.btn-outline-danger:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-light,.btn-shadow.btn-outline-light{border-color:#9ea9b6;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-light,.btn-shadow.btn-light.focus,.btn-shadow.btn-light:focus,.btn-shadow.btn-outline-light,.btn-shadow.btn-outline-light.focus,.btn-shadow.btn-outline-light:focus{-webkit-box-shadow:3px 3px 0 #9ea9b6,2px 2px 0 #9ea9b6,1px 1px 0 #9ea9b6;box-shadow:3px 3px 0 #9ea9b6,2px 2px 0 #9ea9b6,1px 1px 0 #9ea9b6}.btn-shadow.btn-light:hover,.btn-shadow.btn-outline-light:hover{-webkit-box-shadow:5px 5px 0 #9ea9b6,4px 4px 0 #9ea9b6,3px 3px 0 #9ea9b6,2px 2px 0 #9ea9b6,1px 1px 0 #9ea9b6;box-shadow:5px 5px 0 #9ea9b6,4px 4px 0 #9ea9b6,3px 3px 0 #9ea9b6,2px 2px 0 #9ea9b6,1px 1px 0 #9ea9b6;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-light:active,.btn-shadow.btn-outline-light:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-dark,.btn-shadow.btn-outline-dark{border-color:#191a2d;-webkit-transition:none;-o-transition:none;transition:none}.btn-shadow.btn-dark,.btn-shadow.btn-dark.focus,.btn-shadow.btn-dark:focus,.btn-shadow.btn-outline-dark,.btn-shadow.btn-outline-dark.focus,.btn-shadow.btn-outline-dark:focus{-webkit-box-shadow:3px 3px 0 #191a2d,2px 2px 0 #191a2d,1px 1px 0 #191a2d;box-shadow:3px 3px 0 #191a2d,2px 2px 0 #191a2d,1px 1px 0 #191a2d}.btn-shadow.btn-dark:hover,.btn-shadow.btn-outline-dark:hover{-webkit-box-shadow:5px 5px 0 #191a2d,4px 4px 0 #191a2d,3px 3px 0 #191a2d,2px 2px 0 #191a2d,1px 1px 0 #191a2d;box-shadow:5px 5px 0 #191a2d,4px 4px 0 #191a2d,3px 3px 0 #191a2d,2px 2px 0 #191a2d,1px 1px 0 #191a2d;-webkit-transform:translate(-2px,-2px);-o-transform:translate(-2px,-2px);transform:translate(-2px,-2px);-webkit-transition:all .3s ease;-o-transition:all .3s ease;transition:all .3s ease}.btn-shadow.btn-dark:active,.btn-shadow.btn-outline-dark:active{-webkit-box-shadow:none;box-shadow:none;-webkit-transform:translate(4px,4px)!important;-o-transform:translate(4px,4px)!important;transform:translate(4px,4px)!important;-webkit-transition:all .1s ease;-o-transition:all .1s ease;transition:all .1s ease}.btn-shadow.btn-outline-primary:hover,.btn-shadow.btn-primary:hover{background-color:#714cdf}.btn-shadow.btn-outline-secondary:hover,.btn-shadow.btn-secondary:hover{background-color:#16a4de}.btn-shadow.btn-outline-success:hover,.btn-shadow.btn-success:hover{background-color:#17b06b}.btn-shadow.btn-info:hover,.btn-shadow.btn-outline-info:hover{background-color:#2983fe}.btn-shadow.btn-outline-warning:hover,.btn-shadow.btn-warning:hover{background-color:#f97515}.btn-shadow.btn-danger:hover,.btn-shadow.btn-outline-danger:hover{background-color:#ff3c5c}.btn-shadow.btn-light:hover,.btn-shadow.btn-outline-light:hover{background-color:#dbebfb}.btn-shadow.btn-dark:hover,.btn-shadow.btn-outline-dark:hover{background-color:#32334a}.display-1,.display-2,.display-3,.display-4{font-family:Hack,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"}.display-1.text-white,.display-2.text-white,.display-3.text-white,.display-4.text-white,.text-white .display-1,.text-white .display-2,.text-white .display-3,.text-white .display-4{text-shadow:-1px -1px rgba(255,255,255,.2)}.text-reduced-opacity{opacity:.5}.text-grey{color:#a0a0a0}.text-darkblue{color:#4d4d74}.text-darkgrey{color:#6f6974}.text-mono{font-family:Hack,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"}.btn-success,.btn-success:active,.btn-success:focus,.btn-success:hover{color:#c1f8c2}.vim-caret{-webkit-animation:vimCaret 1s linear infinite;-o-animation:vimCaret 1s linear infinite;animation:vimCaret 1s linear infinite}@-webkit-keyframes vimCaret{0%{background-color:transparent}49%{background-color:transparent}50%{background-color:rgba(255,255,255,.2)}100%{background-color:rgba(255,255,255,.2)}}@-o-keyframes vimCaret{0%{background-color:transparent}49%{background-color:transparent}50%{background-color:rgba(255,255,255,.2)}100%{background-color:rgba(255,255,255,.2)}}@keyframes vimCaret{0%{background-color:transparent}49%{background-color:transparent}50%{background-color:rgba(255,255,255,.2)}100%{background-color:rgba(255,255,255,.2)}}.list-group-item-primary{color:#3b2874;background-color:#8869e4}.list-group-item-primary.list-group-item-action:focus,.list-group-item-primary.list-group-item-action:hover{color:#3b2874;background-color:#7753e0}.list-group-item-primary.list-group-item-action.active{color:#fff;background-color:#3b2874;border-color:#3b2874}.list-group-item-secondary{color:#0b5573;background-color:#3bb3e3}.list-group-item-secondary.list-group-item-action:focus,.list-group-item-secondary.list-group-item-action:hover{color:#0b5573;background-color:#25aae0}.list-group-item-secondary.list-group-item-action.active{color:#fff;background-color:#0b5573;border-color:#0b5573}.list-group-item-success{color:#0c5c38;background-color:#3cbd83}.list-group-item-success.list-group-item-action:focus,.list-group-item-success.list-group-item-action:hover{color:#0c5c38;background-color:#36aa76}.list-group-item-success.list-group-item-action.active{color:#fff;background-color:#0c5c38;border-color:#0c5c38}.list-group-item-info{color:#154484;background-color:#4b97fe}.list-group-item-info.list-group-item-action:focus,.list-group-item-info.list-group-item-action:hover{color:#154484;background-color:#3288fe}.list-group-item-info.list-group-item-action.active{color:#fff;background-color:#154484;border-color:#154484}.list-group-item-warning{color:#813d0b;background-color:#fa8b3a}.list-group-item-warning.list-group-item-action:focus,.list-group-item-warning.list-group-item-action:hover{color:#813d0b;background-color:#f97c21}.list-group-item-warning.list-group-item-action.active{color:#fff;background-color:#813d0b;border-color:#813d0b}.list-group-item-danger{color:#851f30;background-color:#ff5b76}.list-group-item-danger.list-group-item-action:focus,.list-group-item-danger.list-group-item-action:hover{color:#851f30;background-color:#ff4261}.list-group-item-danger.list-group-item-action.active{color:#fff;background-color:#851f30;border-color:#851f30}.list-group-item-light{color:#727a83;background-color:#e1eefc}.list-group-item-light.list-group-item-action:focus,.list-group-item-light.list-group-item-action:hover{color:#727a83;background-color:#cae1fa}.list-group-item-light.list-group-item-action.active{color:#fff;background-color:#727a83;border-color:#727a83}.list-group-item-dark{color:#1a1b26;background-color:#535467}.list-group-item-dark.list-group-item-action:focus,.list-group-item-dark.list-group-item-action:hover{color:#1a1b26;background-color:#484859}.list-group-item-dark.list-group-item-action.active{color:#fff;background-color:#1a1b26;border-color:#1a1b26}.alert-primary{color:#322162;background-color:#aa94ec;border-color:#8869e4}.alert-primary hr{border-top-color:#7753e0}.alert-primary .alert-link{color:#1f143c}.alert-secondary{color:#0a4862;background-color:#73c8eb;border-color:#3bb3e3}.alert-secondary hr{border-top-color:#25aae0}.alert-secondary .alert-link{color:#052634}.alert-success{color:#0a4d2f;background-color:#74d0a6;border-color:#3cbd83}.alert-success hr{border-top-color:#36aa76}.alert-success .alert-link{color:#042013}.alert-info{color:#123a70;background-color:#7fb5fe;border-color:#4b97fe}.alert-info hr{border-top-color:#3288fe}.alert-info .alert-link{color:#0b2344}.alert-warning{color:#6e3309;background-color:#fbac73;border-color:#fa8b3a}.alert-warning hr{border-top-color:#f97c21}.alert-warning .alert-link{color:#3f1d05}.alert-danger{color:#701a28;background-color:#ff8a9d;border-color:#ff5b76}.alert-danger hr{border-top-color:#ff4261}.alert-danger .alert-link{color:#471019}.alert-light{color:#60676e;background-color:#e9f3fd;border-color:#e1eefc}.alert-light hr{border-top-color:#cae1fa}.alert-light .alert-link{color:#484e53}.alert-dark{color:#161621;background-color:#848592;border-color:#535467}.alert-dark hr{border-top-color:#484859}.alert-dark .alert-link{color:#020202}.table-primary,.table-primary>td,.table-primary>th{background-color:#8869e4}.table-hover .table-primary:hover{background-color:#7753e0}.table-hover .table-primary:hover>td,.table-hover .table-primary:hover>th{background-color:#7753e0}.table-secondary,.table-secondary>td,.table-secondary>th{background-color:#3bb3e3}.table-hover .table-secondary:hover{background-color:#25aae0}.table-hover .table-secondary:hover>td,.table-hover .table-secondary:hover>th{background-color:#25aae0}.table-success,.table-success>td,.table-success>th{background-color:#3cbd83}.table-hover .table-success:hover{background-color:#36aa76}.table-hover .table-success:hover>td,.table-hover .table-success:hover>th{background-color:#36aa76}.table-info,.table-info>td,.table-info>th{background-color:#4b97fe}.table-hover .table-info:hover{background-color:#3288fe}.table-hover .table-info:hover>td,.table-hover .table-info:hover>th{background-color:#3288fe}.table-warning,.table-warning>td,.table-warning>th{background-color:#fa8b3a}.table-hover .table-warning:hover{background-color:#f97c21}.table-hover .table-warning:hover>td,.table-hover .table-warning:hover>th{background-color:#f97c21}.table-danger,.table-danger>td,.table-danger>th{background-color:#ff5b76}.table-hover .table-danger:hover{background-color:#ff4261}.table-hover .table-danger:hover>td,.table-hover .table-danger:hover>th{background-color:#ff4261}.table-light,.table-light>td,.table-light>th{background-color:#e1eefc}.table-hover .table-light:hover{background-color:#cae1fa}.table-hover .table-light:hover>td,.table-hover .table-light:hover>th{background-color:#cae1fa}.table-dark,.table-dark>td,.table-dark>th{background-color:#535467}.table-hover .table-dark:hover{background-color:#484859}.table-hover .table-dark:hover>td,.table-hover .table-dark:hover>th{background-color:#484859}.hal-9000{background:#f9d080;border:12px #ff3c5c solid;border-radius:90px;-webkit-box-shadow:0 0 40px #ff3c5c;box-shadow:0 0 40px #ff3c5c;display:inline-block;height:40px;width:40px}

/* Container */
.container{
   margin: 0 auto;
   border: 0px solid black;
   width: 50%;
   height: 250px;
   border-radius: 3px;
   background-color: ghostwhite;
   text-align: center;
}



/* Button */
.button{
   border: 0px;
   background-color: deepskyblue;
   color: white;
   padding: 5px 15px;
   margin-left: 10px;
}

/*#res, #res th, #res td {
  border: 1px solid black;
  border-collapse: collapse;
}*/
html body {
    background-color: rgba(0,0,0,1.00);

}

</style>
<style>
html body {
    background-color: rgba(0,0,0,1.00);

}
@media (max-width: 767.98px) {
	body{font-size: 12px;}
	}

	@media only screen and (max-width: 768px) {
	/* For mobile phones: */
	[class*="col-"] {
		width: 100%;
	}

</style>
<style>
        div.list {
            text-align: center;
        }
    </style>
<style media = "screen">
        .ads {
            text-align: center;
            max-width:33% !important; 
            max- height:1% !important;
            display: inline-block;
            left: 1%;
            right: 1%;
        }
    </style>

    <meta name="Title" CONTENT="flask_man's project manager">
    <title>Flask's project manager """+__version__+"""</title>
</head>
<body><br>
<center><h1>Flask's project manager:<br>v"""+__version__+"""</h1></center>


<center>
<br><br>  <br>    
     <center><h3>Create/Reset project</h3>
     <br>   
         <form enctype="multipart/form-data" id="myform" action = "/create" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Database: &nbsp;  &nbsp; </p></b> </td><td>
         <select class="form-control" name="db" id="db">
         <option value="sqlite">SQLite</option>
         <option value="mysql">MySQL/MariaDB</option>
         <option value="postgresql">PostgreSQL</option>
         <option value="oracle">Oracle SQL</option>
         <option value="mssql">MS SQL</option>
         </select></td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Create/Reset" /></div></td></tr>
      </center>
      </table>
      </div>
      </form>  
       
      </center>
<br><br><br>   
<center><h3>Production/Development</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/go" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Mode:&nbsp;  &nbsp;</p></b> </td><td>
         <select class="form-control" name="go" id="go">
         <option value="dev">Development</option>
         <option value="pro">Production</option>
         </select></td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Go" /></div></td></tr>
      </center>
      </table>
      </div>
      </form>  
       
      </center>
<br><br><br>   
<center><h3>Change Database</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/db" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Database:&nbsp;  &nbsp;</p></b> </td><td>
         <select class="form-control" name="db" id="db">
         <option value="sqlite">SQLite</option>
         <option value="mysql">MySQL/MariaDB</option>
         <option value="postgresql">PostgreSQL</option>
         <option value="oracle">Oracle SQL</option>
         <option value="mssql">MS SQL</option>
         </select></td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Change" /></div></td></tr>
      </center>
      </table>
      </div>
      </form>  
       
      </center>
<br><br><br>   
     <center><h3>Add Template/Route</h3>
     <br>   
         <form enctype="multipart/form-data" id="myform" action = "/add" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Path(s):&nbsp;  &nbsp;</p></b> </td>
         <td><input size="40" value='' placeholder="/welcome.html , /admin/home.html" class="form-control" id="template" type = "text" name = "template" required/>
         <td><select class="form-control" name="type" id="type">
         <option value="template">Template</option>
         <option value="route">Route</option>
         </select></td>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Add" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br> <br>       
 
     <center><h3>Delete Template/Route</h3>
     <br>   
         <form enctype="multipart/form-data" id="myform" action = "/delete" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Path:&nbsp;  &nbsp;</p></b> </td>
         <td><select class="form-control" name="template" id="template">
         """+tr+"""
         
         </select></td>
         <td><select class="form-control" name="type" id="type">
         <option value="template">Template</option>
         <option value="route">Route</option>
         </select></td>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Delete" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center><br><br><br>   
     <center><h3>Add Model</h3>
     <br>   
         <form enctype="multipart/form-data" id="myform" action = "/add_m" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Model(s):&nbsp;  &nbsp;</p></b> </td>
         <td><input size="40" class="form-control"  value='' placeholder="users , posts , ..." id="template" type = "text" name = "model" required/>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Add" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br> <br>       
 
     <center><h3>Delete Model</h3>
     <br>   
         <form enctype="multipart/form-data" id="myform" action = "/delete_m" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Model:&nbsp;  &nbsp;</p></b> </td>
         <td><select class="form-control" name="model" id="template">
         """+mo+"""
         
         </select></td>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Delete" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br>    <br>    
<center><h3>Set Firebase APIKey</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/fb_key" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Key:&nbsp;  &nbsp;</p></b> </td>
         <td><input size="40" value='' placeholder="jhgfdfghjklkjhgfgh" class="form-control" id="name" type = "text" name = "key" required/>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Set" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center><br><br>    <br>    
<center><h3>Set Firebase Storage Bucket</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/fsb" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>Name:&nbsp;  &nbsp;</p></b> </td>
         <td><input size="40" value='' placeholder="myfbbucket.appspot.com" class="form-control" id="name" type = "text" name = "name" required/>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Set" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br>   <br>     
<center><h3>Set Firebase Storage Bucket's Config file</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/fsb_conf" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td style="text-align: center; vertical-align: middle;"><b><p style='color:green'>File:&nbsp;  &nbsp;</p></b> </td>
         <td><input size="40" value='' class="form-control" id="path" type = "file" name = "path" required/>
         </td><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Set" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br>   <br>   
<center><h3>Backup</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/backup" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="backup" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center><br><br>   <br>   
<center><h3>Upgrade the package</h3>
<br>   
         <form enctype="multipart/form-data" id="myform" action = "/upgrade" method = "POST" 
         enctype = "multipart/form-data"><table id="form_" cellspacing="0" cellpadding="0">
         <div class="input-group input-group-lg">
         <tr><td><div class="col text-center"><input id="btn" type="submit" class="button btn-block btn-lg" value="Upgrade" /></div></td></tr>
      </table>
      </div>
      </form>  
        
      </center>
<br><br> 
<br> <br>   
</center>
<center><h4>&copy; Copyright <a href="https://github.com/AlaBouali" target="_blank">Ala Bouali</a><br><br></h4><h6><center>Python/PHP Dev since 2017, Pentester, Linux<br> System Administrator and Freelancer since 2019
<br><br><br>See Also:&nbsp;&nbsp;<a href="https://github.com/AlaBouali/bane" target="_blank">Bane</a>&nbsp;,&nbsp;<a href="https://github.com/AlaBouali/xtelnet" target="_blank">Xtelnet</a>&nbsp;,&nbsp;<a href="https://github.com/AlaBouali/sanitizy" target="_blank">Sanitizy</a><br></h6></center><br>"""
 
 app.run(port=12345)


def main():
 if len(sys.argv)<2:
  help_msg("Missing arguments")
  sys.exit()
 if sys.argv[1] not in supported_args:
  help_msg('Unknown arguments')
  sys.exit()
 if sys.argv[1]=="upgrade":
  upgrade()
  sys.exit()
 if sys.argv[1]=="pro":
  go_pro()
  sys.exit()
 if sys.argv[1]=="dev":
  go_dev()
  sys.exit()
 if sys.argv[1]=="manager":
  manager()
  sys.exit()
 if sys.argv[1]=="examples":
  examples_msg()
  sys.exit()
 if sys.argv[1]=="add_model":
  add_model(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="delete_model":
  delete_model(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="add_template":
  add_template(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="delete_template":
  delete_template(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="add_route":
  add_route(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="delete_route":
  delete_route(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="firebase_bucket":
  set_firebase_bucket(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="firebase_apikey":
  set_firebase_apikey(sys.argv[2])
  sys.exit()
 if sys.argv[1]=="firebase_configs":
  file_=sys.argv[2]
  write_firebase_configs_(file_)
  sys.exit()
 if sys.argv[2] not in supported_dbs and sys.argv[2] not in supported_inits:
  help_msg('Unknown arguments')
  sys.exit()
 if sys.argv[1]=="init" and sys.argv[2]=="config":
  init_configs()
  sys.exit()
 if sys.argv[1]=="init" and sys.argv[2]=="app":
  try:
    init_app()
  except Exception as e:
   print(e)
   help_msg('Missing configs ! Try runing: flask_man init config')
  sys.exit()
 if sys.argv[1]=="init" and sys.argv[2]=="install":
  try:
   install()
  except Exception as e:
   print(e)
   help_msg('Missing configs ! Try runing: flask_man init config')
  sys.exit()
 if sys.argv[1]=="db" and sys.argv[2] in supported_dbs:
  try:
   conf=read_configs()
  except Exception as ex:
   print(ex)
   print('Failed to load configs !! Try to run first: flask_man init')
   sys.exit()
  if  sys.argv[2]=="sqlite":
   set_sqlite_database(conf)
  else:
   set_database(conf,sys.argv[2])
  if file_exists('database.py')==True:
   write_file('database.py',get_db_code(conf))
 else:
  help_msg('Unknown Database type')
 sys.exit() 
