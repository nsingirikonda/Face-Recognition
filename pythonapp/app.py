from flask import Flask, render_template, json, request, g, Response, jsonify
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import json, simplejson
import MySQLdb

from selenium import webdriver
import time
import urllib
#import urllib2

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.before_request
def db_connect():
  print("In before request getting conn")
  g.conn = MySQLdb.connect(host='localhost',
                              user='root',
                              passwd='password',
                              db='BucketList')
  print("Got connection")
  g.cursor = g.conn.cursor() 
  print("Got cursor")



@app.after_request
def db_disconnect(response):
  #g.cursor.close()
  #g.conn.close()
  return response

@app.route('/', methods=['POST','GET'])
def main():
    result = query_db("SELECT user_name,user_location, user_time FROM log_user")   
    data = json.dumps(result)
    #driver = webdriver.Firefox()
    #driver.get('http://ec2-50-112-136-119.us-west-2.compute.amazonaws.com:9090/')
    #driver.refresh()
    return render_template('index.html',your_list=data)
    
def your_view():
   result = query_db("SELECT user_name,user_location, user_time FROM log_user")   
   data = json.dumps(result)
   return render_template('index.html',your_list=result)  

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

#sends data as Json
# called in facecog file to log users into database
@app.route('/signUpJson',methods=['POST','GET'])
def signUpJson():
    #g.cursor = conn.cursor()
    print('hey cursor')
    try:
        print('start trying')
        data = request.data
        data = data.decode('utf-8')
        print(data)
        dataJson = json.loads(data)
        print('got dataJson')
        _name = dataJson['inputName']
        _location = dataJson['inputLocation']
        _time = dataJson['inputTime']
        
        print(_name)
        print(_location)
        print(_time)

        # validate the received values
        if _name and _location and _time:
            print('heyo')
            
            # All Good, let's call MySQL
            print('hey conn')
            g.cursor.callproc('sp_createLog',(_name,_location,_time))
            print('hey callproc')
            data = g.cursor.fetchall()
            print('hey data')
            if len(data) is 0:
                g.conn.commit()
                print('User Logged')
                return json.dumps({'message':'User logged successfully !'})
            else:
                return json.dumps({'message':'NOPE !'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        g.cursor.close() 
        g.conn.close()
        
    return jsonify(request.form)    
  

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    #g.cursor = conn.cursor()
    print('hey cursor')
    try:
        _name = request.form['inputName']
        _location = request.form['inputLocation']
        _time = request.form['inputTime']

        print(_name)
        print(_location)
        print(_time)

        # validate the received values
        if _name and _location and _time:
            print('heyo')
            
            # All Good, let's call MySQL
            print('hey conn')
            g.cursor.callproc('sp_createLog',(_name,_location,_time))
            print('hey callproc')
            data = g.cursor.fetchall()
            print('hey data')
            if len(data) is 0:
                g.conn.commit()
                print('User Logged')
                return json.dumps({'message':'User logged successfully !'})
            else:
                return json.dumps({'message':'NOPE !'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        g.cursor.close() 
        g.conn.close()
        
    return jsonify(request.form)    
        
def query_db(query, args=(), one=False):
  g.cursor.execute(query, args)
  rv = [dict((g.cursor.description[idx][0], value)
  for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
  return (rv[0] if rv else None) if one else rv        
        
@app.route("/loglist",methods=[ 'GET' ] )   
def loglist():
   result = query_db("SELECT user_name,user_location, user_time FROM log_user")   
   data = json.dumps(result)
   resp = Response(data, status=200, mimetype='application/json')
   return resp
   
@app.route("/userList",methods=[ 'GET' ] )
def userList():
   result = query_db("SELECT user_id,user_name, user_pic_name FROM user_list")   
   data = json.dumps(result)
   resp = Response(data, status=200, mimetype='application/json')
   return resp

@app.route("/tableoutput",methods=['POST','GET'] )
def your_view():
   result = query_db("SELECT user_name,user_location, user_time FROM log_user")   
   data = json.dumps(result)
   return render_template('loglist.html',your_list=result)   
   
@app.route("/createUser",methods=['POST','GET'] )
def create_user():
    try:
        _id = request.form['inputID']
        _name = request.form['inputName']
        _picName = request.form['inputPicName']

        print(_id)
        print(_name)
        print(_picName)   
        
        if _id and _name and _picName:
            print('heyo')
            
            # All Good, let's call MySQL
            print('hey conn')
            g.cursor.callproc('sp_createUser',(_id,_name,_picName))
            print('hey callproc')
            data = g.cursor.fetchall()
            print('hey data')
            if len(data) is 0:
                g.conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'message':'NOPE !'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        g.cursor.close() 
        g.conn.close()
        
    return jsonify(request.form)    
            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090)#9090
