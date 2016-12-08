from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50.sql import SQL
from flask_session import Session
from tempfile import gettempdir
from time import gmtime, strftime
import time
import datetime
import csv
import json

app = Flask(__name__)
#app.config.from_pyfile('application.cfg')

# ensure responses aren't cached
if app.config['DEBUG']:
    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Expires'] = 0
        response.headers['Pragma'] = 'no-cache'
        return response

# configure session to use filesystem (instead of signed cookies)
app.config['SESSION_FILE_DIR'] = gettempdir()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

# configure CS50 Library to use SQLite database
db = SQL('sqlite:///requests.db')


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/requesthelp_s", methods=["GET", "POST"])
def requesthelp_s():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # ensure name was submitted
        if not request.form.get('Name'):
            return render_template("apology.html", message = "Please input name")
        
        student_name = request.form['Name']
        
        # ensure table_id was submitted
        if not request.form.get('Table'):
            return render_template("apology.html", message = "Please input table id #")
        
        table_id = request.form['Table']
        
        # ensure problem was submitted
        if not request.form.get('Problem'):
            return render_template("apology.html", message = "Please input problem")
        
        words = request.form.get('Problem').split()
        
        #ensure problem not more than 4 words long
        if len(words) > 4:
            return render_template("apology.html", message = "Problem cannot be longer than 3 words, feel free to elaborate in description")
            
        problem = request.form['Problem']
        
        # see if description was submitted, if not set to "None"
        if not request.form.get('Description'):
            description = "None"
        else:
            description = request.form['Description']
        
        #add request into the database
        db.execute('INSERT INTO current_requests (student_name, table_id, problem, description) VALUES(:student_name, :table_id, :problem, :description)', student_name=student_name, table_id=table_id, problem=problem, description=description)
        
        #redirect use to view requests page
        return redirect(url_for('viewrequests_s'))
        
    # if user reached route via GET (as by submitting a form via POST)
    else:
        return render_template("requesthelp_s.html")

@app.route("/viewrequests_s", methods=["GET"])
def viewrequests_s():
    
    #get all info from current_requests
    rows = db.execute('SELECT * FROM current_requests')
    
    #iterate through each stock instance
    for i in range(len(rows)):
        
        #get row's time submitted and current time and conver to date time
        time_submitted = rows[i]['time_submitted']
        ts = time.time()
        currentTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        d1 = datetime.datetime.strptime(time_submitted, '%Y-%m-%d %H:%M:%S')
        d2 = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M:%S')
        
        #calculate wait time
        difference = d2 - d1
        
        #add key"difference" to row[i] dict to save (time in minutes)
        rows[i]['difference'] = str(int(difference / datetime.timedelta(minutes=1))) + " min"
    
    #render page's html
    return render_template("viewrequests_s.html", result = rows)


#METHODS FOR ANDROID APP TO CONTACT SERVER BELOW#

#method for android to post new help request and send to server
@app.route("/sendData", methods=['POST', 'GET'])
def sendData():
    #if user trying to post info to server
    if request.method == 'POST':
        #get the varibles from the post request and save
        post = request.json
        student_name = post['student_name']
        table_id = post['table_id']
        problem = post['problem']
        description = post['description']
        
        #insert new request into database using variables from posted JSON
        db.execute('INSERT INTO current_requests (student_name, table_id, problem, description) VALUES(:student_name, :table_id, :problem, :description)', student_name=student_name, table_id=table_id, problem=problem, description=description)
        
        #return sucess
        return json.dumps({"status": "success"})
    else:
        #should not be attempting to get info from this page, return failure
        return json.dumps({"status": "failure"})


#method fo android to get all database information from server
@app.route("/getData")
def getData():
    #if there is data within current_requests, return entire database to android upon request 
    if db.execute('SELECT * from current_requests'):
        return json.dumps(db.execute('SELECT * from current_requests'))
    else:
        return json.dumps({"status": "no info in database"})


#method to move a help request from "current" database to the "filled" database upon android request
@app.route("/moveData", methods=['POST', 'GET'])
def moveData():
    #if user trying to "post" info to server
    if request.method == 'POST':
         #get the varibles from the post request and save
        post = request.json
        request_id = post['request_id']
        student_name = post['student_name']
        table_id = post['table_id']
        problem = post['problem']
        description = post['description']
        time_submitted = post['time_submitted']
        
        #insert posted request into filled database
        db.execute('INSERT INTO filled_requests (request_id, student_name, table_id, problem, description, time_submitted) VALUES(:request_id, :student_name, :table_id, :problem, :description, :time_submitted)', request_id = int(request_id), student_name=student_name, table_id=table_id, problem=problem, description=description, time_submitted=time_submitted)
        
        #delete request from current database
        db.execute('DELETE FROM current_requests WHERE request_id = :request_id', request_id = int(request_id))
        
        #return success
        return json.dumps({"status": "success"})
    else:
        #should not be attempting to get info from this page, return failure
        return json.dumps({"status": "failure"})

    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8080)

