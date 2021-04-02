from flask import Flask, render_template, request, redirect, url_for, session, jsonify 
import sqlite3
import re
import os
import magic
from identify.extensions import EXTENSIONS
app = Flask(__name__)
app.secret_key = 'ChidozieNnajiMySQLAdminDbhost2005@gmail.com#codewithcn.com'
@app.route('/', methods=['GET', 'POST'])
def home():
    msg=''
    if request.method=='POST' and 'User-Name' in request.form and 'Password' in request.form:
        usernames = request.form['User-Name']
        passwords = request.form['Password']
        try:
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = "select * from users where name='{}' and password='{}' ".format(usernames, passwords)
            cursor.execute(query)
            account = cursor.fetchone()
        except Exception as e:
            print(e)
            account=False
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('user_home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)
def detect_type(lists, direct):
    new_list=[]
    for i in lists:
        direct = direct if direct.endswith('/') else direct+'/'
        print(direct)
        if os.path.isfile(direct+i):
            if os.path.isdir(direct+i):
                new_list.append([i, 'Folder'])
            else:
                name, ext = os.path.splitext(i)
                if ext != '.db':
                    text=''
                    for it in EXTENSIONS[ext.split('.')[1]]:
                        if it !='text':
                            text+=it+'/'
                    new_list.append([i, text])
                else:
                    new_list.append([i,'db'])
    new_list.append(direct)
    return new_list
@app.route('/home', methods=['GET', 'POST'])
def user_home():
    msg=''
    directory =[]
    if session['loggedin']:
        print('logged in')
        if request.method=='POST' and 'query' in request.form:
            print('post')
            query = request.form['query']
            try:
                directory = os.listdir(query)
            except Exception as e:
                print(e)
                directory=[]
            print('directory', directory)
            directory = detect_type(directory, query)
            print('directory', directory)
        return render_template('home.html', msg=msg, name=session['username'], directory=directory)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg=''
    if request.method=='POST' and 'name' in request.form and 'email' in request.form:
        username = request.form['name']
        password = request.form['email']
        try:
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = "select * from users where name='{}' and password='{}' ".format(usernames, passwords)
            cursor.execute(query)
            account = cursor.fetchone()
            conn.close()
        except Exception as e:
            print('error',e)
            account =False
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg ='Please fill out the form!'
        else:
            print('Running else')
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            query = "insert into users (name, password) values ('{}', '{}')".format(username, password)
            cursor.execute(query)
            conn.commit()
            msg ='You have successfully registered!'
    return render_template('signup.html', msg=msg)
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')
@app.route('/edit/@"<path:document>"/', methods=['GET'])
def edit_document(document):
    try:
        if session['loggedin']:
            print(document)
            contents = os.listdir(document)
            direct = document if document.endswith('/') else document+'/'
            content={}
            for i in contents:
                if os.path.isfile(direct+i):
                    if not os.path.isdir(direct+i) and not i.endswith('.db'):
                        content[i] = direct+i
            for i in contents:
                if os.path.isfile(direct+i):
                    if not os.path.isdir(direct+i):
                        original = [i, direct+i]
                        break
            text=''
            for it in EXTENSIONS[os.path.splitext(original[0])[1].split('.')[1]]:
                if it !='text':
                    text+=it+'/'
                    original.append(text.split('/')[0])

            print('original', original[2])
            types=  {}
            for i in contents:
                if os.path.isfile(direct+i):
                    if not os.path.isdir(direct+i):
                        name, ext = os.path.splitext(i)
                        if ext != '.db':
                            text=''
                            for it in EXTENSIONS[ext.split('.')[1]]:
                                if it !='text':
                                    text+=it+'/'
                                    types[text.split('/')[0]]= 0
            print('types', types)
            return render_template('filedit.html', document=document, content=content, cont=contents, original=original, types=types)
    except Exception as e:
        print(e)
    return redirect(url_for('home'))
@app.route('/filetype', methods=['POST'])
def get_file_type():
    data = request.get_json()
    name, ext = os.path.splitext(data['file'])
    if ext != '.db':
        text=''
        for it in EXTENSIONS[ext.split('.')[1]]:
            if it !='text':
                text+=it+'/'
    typ = text.split('/')[0]
    print('file type', typ)
    with open(data['content'], 'r') as file:
        contents = file.readlines()
        file.close()
    response = {'type': typ, 'content': contents}
    return response
@app.route('/savefile', methods=['POST'])
def save_file():
    data = request.get_json()  
    try:
        with open(data['file'], "w") as f:
            f.write(data['content'])
            return "OK", 200
    except Exception as e:
        print(e) 
        return e
@app.route('/logout', methods=['GET'])
def logout():
    try:
        if session['loggedin']:
            session.pop('loggedin',None)
            session.pop('id',None)
            session.pop('username',None)
    except Exception as e:
        print(e)
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)