"""
my name is Eden Katorza and this is my project
"""

from datetime import datetime
from DemoFormProject import app
from DemoFormProject.Models.LocalDatabaseRoutines import create_LocalDatabaseServiceRoutines

from flask import render_template, redirect, request

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import json 
import requests

import io
import base64

from os import path

from flask   import Flask, render_template, flash, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms import TextField, TextAreaField, SubmitField, SelectField, DateField
from wtforms import ValidationError


from DemoFormProject.Models.QueryFormStructure import QueryFormStructure 
from DemoFormProject.Models.QueryFormStructure import LoginFormStructure 
from DemoFormProject.Models.QueryFormStructure import UserRegistrationFormStructure 


import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

db_Functions = create_LocalDatabaseServiceRoutines() 


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


#יצירת דף הקוורי
@app.route('/Query', methods=['GET', 'POST'])
def Query(): # יצירת דף הקוורי והגרף

    form = QueryFormStructure(request.form)
    l= ['Comedy','Animation','Crime','Fantasy','Adventure','Family','Drama','Romance','Thriller','Action','Horror','History','Science Fiction','Mystery'] # כתיבת כל סוגי הג'אנרים שיוצגו

    form.genres.choices =list(zip(l,l)) # יצירת הרשימה המוצגת לבחירת הג'אנר
 
    chart = "static/Pics/pic2.jpg" # הוספת תמונה בדף הבחירה 
     
    if (request.method == 'POST' ):
        genres = form.genres.data
        year = form.year.data
        df = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\movies_metadata original.csv'),encoding='latin-1',low_memory=False) #לקיחת המידע מהדאטא סט שלי
        df=df[["title","budget","popularity","genres","release_date"]] # העמודות בהן אני משתמשת לקבלת הנתונים הנחוצים לי ליצירת הגרף
        df=df.dropna()
        df["budget"]=df["budget"].astype(int)#לקיחת התקציב והפיכתו למספר שלם
        df=df[df["budget"]>100000]#אני אשתמש רק בתקציבים מעל מאה אלף שקל בכדי להקטין את כמות הסרטים שיופיעו בגרף כדי שיהיה מסודר
        df=df[df["genres"].str.contains(genres)]#קבלת הז'אנר שבו בחר המשתמש והוצאת הסרטים שבהם ז'אנר זה נמצא 
        df=df[df["release_date"].str.contains(year)]#קבלת השנה שבה בחר המשתמש והוצאת הסרטים שבהם שנה זו נמצאת
        df=df.drop("genres",1)#בכדי שנוכל להמשיך הלאה יותר מסודר "זרקנו" בנתיים את הז'אנר כי כבר ניתחנו את הנתונים וסיימנו להשתמש בו
        df=df.drop("release_date",1)#בכדי שנוכל להמשיך הלאה יותר מסודר "זרקנו" בנתיים את השנה כי כבר ניתחנו את הנתונים וסיימנו להשתמש בה
        df=df.set_index("title")
        df["popularity"]=df["popularity"].astype(float)#לקיחת הפופולריות והפיכתו
        df["budget"]=df["budget"].apply(lambda x: x/1000000)# לקיחת עמודת התקציב ולחלקה למיליון בכדי שהגרף יהיה יותר מסודר ושהתקציב יינתן במיליונים
        fig = plt.figure()
        ax = fig.add_subplot(111)#הכנת הגרף
        ax.set_xlabel("budget",fontsize = 22)#הכנת שורת התקציב וגודל הכיתוב של "budget" 
        ax.set_ylabel("popularity",fontsize = 22)#הכנת שורת התקציב וגודל הכיתוב של "popularity"
        df.plot("budget","popularity",kind="scatter",ax=ax,figsize=(20,50),fontsize = 22) #הכנת שורות הגרפים
        for k, v in df.iterrows():
            ax.annotate(k, v,size = 22)
        chart = plot_to_img(fig)#מוציא את הגרף כתמונה

    return render_template('Query.html', 
            form = form,
            chart = chart,
            title='Query',
            year=datetime.now().year,
            message='This page will use the web forms to get user input'
        )

# -------------------------------------------------------
# Register new user page
# -------------------------------------------------------
#דף רישום המשתמש שבו המשתמש יוצר לעצמו משתמש וכאשר המשתמש תקין הוא נכנס ישירות לקוורי
@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = UserRegistrationFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (not db_Functions.IsUserExist(form.username.data)):
            db_Functions.AddNewUser(form)
            db_table = ""

            flash('Thanks for registering new user - '+ form.FirstName.data + " " + form.LastName.data )
            return redirect('Query')
        else:
            flash('Error: User with this Username already exist ! - '+ form.username.data)
            form = UserRegistrationFormStructure(request.form)

    return render_template(
        'register.html', 
        form=form, 
        title='Register New User',
        year=datetime.now().year,
        repository_name='Pandas',
        )

# -------------------------------------------------------
# Login page
# This page is the filter before the data analysis
# -------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (db_Functions.IsLoginGood(form.username.data, form.password.data)):
            flash('Login approved!')
            return redirect('Query')
        else:
            flash('Error in - Username and/or password')
   
    return render_template(
        'login.html', 
        form=form, 
        title='Login to data analysis',
        year=datetime.now().year,
        repository_name='Pandas',
        )


# בדאטא מודל שלי רואים הסבר על הדאטא ועל הנושא שלי זהו בעצם דף הפתיחה שכאשר אני לוחצת על כפתור הדאטא מעלה הוא מופיע
@app.route('/DataModel')
def DataModel():
    """Renders the contact page."""
    return render_template(
        'DataModel.html',
        title='This is my Data Model page about movies,budget and popoularity',
        year=datetime.now().year,
        message='In this page we will check if the amount of budget affects the popularity of the film'
    )

#הדאטא סט מהווה לי את המידע הרלוונטי לאתר
@app.route('/DataSet1')
def DataSet1():

    df = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\movies_metadata.csv'))
    raw_data_table = df.to_html(classes = 'table table-hover')


    """Renders the contact page."""
    return render_template(
        'DataSet1.html',
        title='This is Data Set page',
        raw_data_table = raw_data_table,
        year=datetime.now().year,
        message='In this page we will check if the amount of budget affects the popularity of the film '
    )
#פונקציה זו יוצרת את הגרף 
def plot_to_img(fig):
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    return pngImageB64String
