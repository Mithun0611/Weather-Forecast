from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from db import db, User, Search
from weather_api import get_forecast
import plotly.graph_objs as go
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db.init_app(app)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        uname = request.form['username']
        pwd = request.form['password']
        if User.query.filter_by(username=uname).first():
            return "User already exists"
        user = User(username=uname, password=pwd)
        db.session.add(user)
        db.session.commit()
        return redirect('/login.html')
    return render_template("register.html")

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session['user_id'] = user.id
            return redirect('/dashboard.html')
        return "Invalid credentials"
    return render_template("login.html")

@app.route('/dashboard.html', methods=['GET', 'POST'])
def dashboard():
    forecast_data = None
    plot_url = ""
    if 'user_id' not in session:
        return redirect('/login.html')

    if request.method == 'POST':
        city = request.form['city']
        forecast_data = get_forecast(city)
        if forecast_data:
            user = User.query.get(session['user_id'])
            result = json.dumps(forecast_data)
            search = Search(city=city, result=result, user=user)
            db.session.add(search)
            db.session.commit()

            # Plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_data['times'], y=forecast_data['temps'], mode='lines+markers', name='Temp'))
            fig.update_layout(title=f"5-Day Forecast for {city}", xaxis_title="Time", yaxis_title="Temp (°C)")
            plot_url = fig.to_html(full_html=False)

    return render_template('dashboard.html', plot_url=plot_url)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
