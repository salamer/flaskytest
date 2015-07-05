from datetime import datetime
from flask import Flask,request,make_response,redirect,abort,render_template,session,url_for,flash
from flask.ext.script import Manager,Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from flask.ext.migrate import Migrate,MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import StringField,SubmitField
from wtforms.validators import Required
import os

basedir=os.path.abspath(os.path.dirname(__file__))

#初始化flask应用
app=Flask(__name__)

#表单的密匙
app.config['SECRET_KEY']='hard to guess string'

#sqlalchemy的数据库配置
app.config['SQLALCHEMY_DATABASE_URI']='mysql://@localhost/flaskytest'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True

db=SQLAlchemy(app)
manager=Manager(app)
bootstrap=Bootstrap(app)
moment=Moment(app)

app.debug=True

#flask-wtf的表单的初始化
class NameForm(Form):
    name=StringField('What is your name?',validators=[Required()])
    submit=SubmitField('submit')

#alchemy的数据库初始化
class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role',lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name
        
class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    
    def __repr__(self):
        return '<User %r>' % self.username



#@app.route('/')
#def index():
#    user_agent=request,headers.get('User-Agent')
#    return '<p> your browser is %s</p>' % user_agent
    
#@app.route('/',methods=['GET','POST'])
#def index():
#    form=NameForm()
#    if form.validate_on_submit():
#        old_name=session.get('name')
#        if old_name is not None and old_name != form.name.data:
#            flash('you change your name?')
#        session['name']=form.name.data
#        return redirect(url_for('index'))
#    return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'))



#简单的注册登录逻辑，基于flask的session
@app.route('/',methods=['GET','POST'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user=User(username=form.name.data)
            db.session.add(user)
            session['known']=False
        else:
            session['known']=True
        session['name']=form.name.data
        form.name.data=''
        return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'),known=session.get('known',False))
    return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'),known=session.get('known',False))
    
@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)
    
@app.route('/setcookies')
def setcookies():
    response=make_response('<h1>here got the cookies!</h1>')
    response.set_cookie('answer','42')
    return response
    
    
#这个版本的flask的redirect有问题（flask版本0.10.0）
@app.route('/redirect')
def redirect():
    return redirect(url_for('setcookies'))
    
#@app.route('/abort/user/<id>')
#def abort(id):
#    user=load_user(id)
#    if not user:
#        abort(404)
#    return 'hello %s' % user.name

@app.route('/render/<name>/')
def render(name):
    return render_template('user.html',name=name)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
    
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

#将这里的文件加载进shell里面，不用再import
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))


#数据迁移，保存在migration文件夹里面
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)
    
    
#script的类似django的manage.py 的命令行控制器
if __name__=='__main__':
    manager.run()
