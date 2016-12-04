from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50.sql import SQL
from flask_session import Session
from tempfile import gettempdir
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
            return render_template("apology.html")
        
        student_name = request.form['Name']
        
        # ensure table_id was submitted
        if not request.form.get('Table'):
            return render_template("apology.html")
        
        table_id = request.form['Table']
        
        # ensure problem was submitted
        if not request.form.get('Problem'):
            return render_template("apology.html")
            
        problem = request.form['Problem']
        
        # see if description was submitted
        if not request.form.get('Description'):
            description = None
            #idk what do I want to do if they don't submit a discription
        else:
            description = request.form['Description']
        
        db.execute('INSERT INTO current_requests (student_name, table_id, problem, description) VALUES(:student_name, :table_id, :problem, :description)', student_name=student_name, table_id=table_id, problem=problem, description=description)
        
        return redirect(url_for('viewrequests_s'))
        
    
    # if user reached route via GET (as by submitting a form via POST)
    else:
        return render_template("requesthelp_s.html")
        

@app.route("/viewrequests_t", methods=["GET", "POST"])
def viewrequests_t():
    if request.method == "POST":
        #VIEW MORE CODE GOES HERE
        #this doesn't work rn but who cares
        return render_template("requesthelp_s.html")
        
    else:
        rows = db.execute('SELECT * FROM current_requests')
        return render_template("viewrequests_t.html", result = rows)

@app.route("/viewrequests_s", methods=["GET"])
def viewrequests_s():
    rows = db.execute('SELECT * FROM current_requests')
    return render_template("viewrequests_s.html", result = rows)


@app.route("/sendData", methods=['POST', 'GET'])
def sendData():
    post = request.json
    student_name = post['student_name']
    table_id = post['table_id']
    problem = post['problem']
    description = post['description']
    db.execute('INSERT INTO current_requests (student_name, table_id, problem, description) VALUES(:student_name, :table_id, :problem, :description)', student_name=student_name, table_id=table_id, problem=problem, description=description)
    
@app.route("/getData")
def getData():
    if db.execute('SELECT * from current_requests'):
        return db.execute('SELECT * from current_requests')
    else:
        return json.dumps({"status": "success"})

    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8080)

