from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from dashboard import fetch_data, create_bar_chart, create_line_chart, create_pie_chart, create_heart_rate_scatter_plot
import pickle
from datetime import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'Calorie.db'
app.secret_key = 'TH15_1S_@_S3CR3T_K3Y'

def prediction(req):
    print(req)
    Gender=int(req['gender'])
    Age = float(req['age'])
    Height = float(req['height'])
    Duration=float(req['duration'])
    Heart_Rate = float(req['heart_rate'])
    Body_Temp = float(req['temperature'])

    model=pickle.load(open('final_model.pkl','rb'))

    data=[[Gender,Age,Height,Duration,Heart_Rate,Body_Temp]]
    print(data)
    result = model.predict(data)
    result = round(float(result),2)
    return result

@app.route('/',methods=("GET","POST"))
def main():
    if request.method=="POST":
        result=prediction(request.form)
        return render_template('index.html',calories = result)
        
    return render_template('index.html')

@app.route('/login.html',methods=("GET","POST"))
def login():
    if request.method=="POST":
        login_id=request.form['userid']
        passwd = request.form['password']
        login_conn = sqlite3.connect(app.config['DATABASE'])
        cur=login_conn.cursor()
        cur.execute('SELECT name,age,height,gender FROM users WHERE userid = ? AND password = ?', (login_id,passwd))
        result = cur.fetchone()
        login_conn.close()
        if result:
            print(result)
            session['userid'] = request.form['userid']
            session['name'] = result[0]
            session['age'] = result[1]
            session['height'] = result[2]
            session['gender'] = result[3]
            return redirect(url_for('home'))
        else:
            print("Wrong")
            flash("Wrong Id or Password")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register.html',methods=("GET","POST"))
def register():
    if request.method=="POST":
        user_id=request.form['userid']
        passwd = request.form['password']
        name = request.form['name']
        age = request.form['age']
        height = request.form['height']
        gender = request.form['gender']

        register_conn = sqlite3.connect(app.config['DATABASE'])
        register_cur=register_conn.cursor()
        register_cur.execute('SELECT userid FROM users WHERE userid = ?', (user_id,))
        result = register_cur.fetchone()
        if result:
            register_conn.close()
            flash("User already exists")
            return render_template('login.html')
        else:
            register_cur.execute('insert into users values(?,?,?,?,?,?)',(user_id,passwd,name,age,height,gender))
            register_conn.commit()
            register_conn.close()
            session['userid'] = request.form['userid']
            session['name'] = request.form['name']
            session['age'] = request.form['age']
            session['height'] = request.form['height']
            session['gender'] = request.form['gender']
            return redirect(url_for('home'))
    return render_template('login.html')
        
@app.route('/home.html',methods=("GET","POST"))
def home():
    if request.method=="POST":
        result = prediction(request.form)
        session['calories'] = result
        exercise_conn = sqlite3.connect(app.config['DATABASE'])
        exercise_cur=exercise_conn.cursor()
        exercise_cur.execute('insert into exercise(exercise_name,userid,duration,date,bpm,temperature,calories) values(?,?,?,?,?,?,?)',
                             (request.form['exercise_name'],
                              session['userid'],
                              float(request.form['duration']),
                              datetime.today().date(),
                              float(request.form['heart_rate']),
                              float(request.form['temperature']),
                              result))
        exercise_conn.commit()
        exercise_conn.close()
        return render_template('home.html',calories = result)
        

    return render_template('home.html',name = session['name'], age = session['age'], height = session['height'], gender = 0 if session['gender']=='Male' else 1)

@app.route('/dashboard.html',methods=("GET","POST"))
def dashboard():
    user_name = session.get('name')
    userid = session.get('userid')
    if user_name:
        exercise_data, time_data, calories_data, heart_data = fetch_data(userid)

        bar_chart = create_bar_chart(exercise_data)
        line_chart = create_line_chart(time_data)
        pie_chart = create_pie_chart(calories_data, title='Exercise Distribution and Calories Burned')
        scatter_plot = create_heart_rate_scatter_plot(heart_data)


        return render_template('user_dashboard.html',
                               username=user_name,
                               bar_chart=bar_chart,
                               line_chart=line_chart,
                               pie_chart=pie_chart,
                               scatter_plot=scatter_plot
                            )


# Afterwards can just redirect it to the login page directly, or can display a
# Homepage with dev info/project info and login button.

@app.route('/')
def method_name():
    return "HELLO WORLD!"

if __name__ == '__main__':
    app.run(debug=True)