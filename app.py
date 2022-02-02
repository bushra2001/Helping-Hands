# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:40:29 2021

@author: Bushra
"""

from flask import Flask, render_template, request, session, redirect, url_for
from datetime import date,time, datetime
import sqlite3 as sql
import math
import base64
import os
# Create Database if it doesnt exist
if not os.path.isfile('database.db'):
  conn = sql.connect('database.db')
  conn.execute('CREATE TABLE IF NOT EXISTS Donors (Name TEXT NOT NULL, Amount INTEGER NOT NULL, Email TEXT NOT NULL, [timestamp] TIMESTAMP)')
  conn.execute('CREATE TABLE IF NOT EXISTS Users (Name TEXT NOT NULL, Email TEXT NOT NULL, Password TEXT NOT NULL, Contact INTEGER NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Donations (Field TEXT NOT NULL, Amount INTEGER NOT NULL)')
  conn.close()

app = Flask(__name__,static_url_path='/assets',
            static_folder='assets', 
            template_folder='./')

@app.route('/')
def root():
   session['logged_out']= 1
   return render_template('index.html')

@app.route('/index.html')
def index():
   return render_template('index.html')

@app.route('/header_page.html')
def header_page():
   return render_template('header_page.html')

@app.route('/menu-bar-charity.html')
def menu_bar_charity():
   return render_template('menu-bar-charity.html')

@app.route('/footer.html')
def footer():
   return render_template('footer.html')

@app.route('/sidebar.html')
def sidebar():
   return render_template('sidebar.html')   

@app.route('/contact.html')
def contact():
   return render_template('contact.html')

@app.route('/our-causes.html')
def our_causes():
   with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Children Health Fund' ")
      CHF_VAL = (cur.fetchone())[0]
      CHF = math.ceil((CHF_VAL/112000)*100)
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Cancer Research Institute'")
      CRI_VAL = (cur.fetchone())[0]
      CRI = math.ceil((CRI_VAL/112000)*100)
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Education to Every Child'")
      EEC_VAL = (cur.fetchone())[0]
      EEC = math.ceil((EEC_VAL/112000)*100)
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Hostels and Old Age Homes'")
      HOH_VAL = (cur.fetchone())[0]
      HOH =math.ceil((HOH_VAL/112000)*100)
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Counselling Centers'")
      CC_VAL = (cur.fetchone())[0]
      CC =math.ceil((CC_VAL/112000)*100)
      cur.execute("SELECT AMOUNT FROM Donations WHERE Field = 'Food for the Hungry'")
      FH_VAL = (cur.fetchone())[0]
      FH = math.ceil((FH_VAL/112000)*100)
      con.commit()
   return render_template('our-causes.html',CHF=CHF, CHF_VAL=CHF_VAL, CRI=CRI, CRI_VAL=CRI_VAL,EEC=EEC, EEC_VAL=EEC_VAL,HOH=HOH, HOH_VAL=HOH_VAL,CC=CC, CC_VAL=CC_VAL,FH=FH, FH_VAL=FH_VAL)

@app.route('/about-us.html')
def about_us():
   return render_template('about-us.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    nm = request.form['nm']
    contact = request.form['contact']
    email = request.form['email']
    password = (request.form['password']).encode("utf-8")
         
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #check if User already present
      cur.execute("SELECT Email FROM Users WHERE Email=(?)",[(email)])
      data = cur.fetchall()
      if len(data)>0:
        print('User already exists')
        user_exists=1
      else:
        print("User not found, register new user")
        user_exists=0
        cur.execute("INSERT INTO Users (Name,Email,Password,Contact) VALUES (?,?,?,?)",(nm,email,base64.b64encode(password),contact) )
        
  return render_template('login.html',user_exists=user_exists, invalid = None, logged_out=None)


@app.route('/login.html',  methods=['GET', 'POST'])
def login():
  invalid = None
  if request.method == 'POST':
    email = request.form['email']
    password = (request.form['password']).encode("utf-8")     
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #Validate user credentails from database
      cur.execute("SELECT Email FROM Users WHERE Email=(?) AND Password=(?)",[(email),(base64.b64encode(password))])
      data = cur.fetchall()
      if len(data)>0:
        print('Login Success')
        # Fetch name of user
        cur.execute("SELECT Name FROM Users WHERE Email=(?) AND Password=(?)",[(email),(base64.b64encode(password))])
        nm = cur.fetchall()
        nm=nm[0][0]
        # Store User details in Session and log in user
        session['nm'] = nm
        session['email'] = email
        session['logged_out'] = None
        return redirect(url_for('donate'))
      else:
        print("Invalid Login")
        invalid=1  
  return render_template('login.html',user_exists=None, invalid = invalid, logged_out=None)

@app.route('/logout')
def logout():
  session.clear()
  session['logged_out']=1
  print('Session Cleared and Logged Out')
  return render_template('index.html')  

@app.route('/donate')
def donate():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   nm = session['nm']
   email = session['email']
   return render_template('donate.html',nm=nm,email=email)         

#insert values into table
@app.route('/donation',methods = ['POST', 'GET'])
def donation():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   if request.method == 'POST':
         nm = session['nm']
         email = session['email']
         amt = request.form['amt']
         fields =request.form['fields']
         today = datetime.now()
         today = today.strftime("%d-%m-%Y"+","+"%H:%M")
         
         with sql.connect("database.db") as con:
            cur = con.cursor()
            #check if already donated. If already donated, add donation. Else create new donation
            cur.execute("SELECT Email FROM Donors WHERE Email=(?)",[(email)])
            data = cur.fetchall()
            if len(data)>0:
              cur.execute("UPDATE Donors SET Amount=Amount+(?), timestamp =(?)  WHERE Email=(?)",[(amt),(today),(email)])
            else:
              cur.execute("INSERT INTO Donors (Name,Amount,Email,timestamp) VALUES (?,?,?,?)",(nm,amt,email,today) )                
            con.commit()
            
            #check if already donated in field. If already donated, add donation. Else create new donation
            cur.execute("SELECT Field FROM Donations where Field =(?)",[(fields)])
            data = cur.fetchall()
            if len(data)>0:
              cur.execute("UPDATE Donations SET Amount=Amount+(?) WHERE Field=(?)",[(amt),(fields)])
            else:
              cur.execute("INSERT INTO Donations (Field,Amount) VALUES (?,?)",(fields,amt) )                
            con.commit()



            # Greeting
            msg = "Thank You for Donating"
            for row in cur.execute("SELECT Amount FROM Donors WHERE Email=(?)",[(email)]):
                Amount=row
            

         return render_template("greeting.html",msg = msg,nm=nm,Amount=Amount,today=today, email=email)
         con.close()

#Display List of Donations
@app.route('/list1')
def list1():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("SELECT * FROM Donors")
   
   rows = cur.fetchall();
   return render_template("list1.html",rows = rows)

#Display Profile
@app.route('/profile')
def profile():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   nm = session['nm']
   email = session['email']
   with sql.connect("database.db") as con:
    cur = con.cursor()
    # Fetch details of user
    cur.execute("SELECT Contact FROM Users WHERE Email=(?)",[(email)])
    contact = cur.fetchall()
    contact=contact[0][0]

    cur.execute("SELECT Password FROM Users WHERE Email=(?)",[(email)])
    password = cur.fetchall()
    password=password[0][0]
   return render_template("profile.html",nm=nm,email=email,contact=contact,password=password)

if __name__ == '__main__':
   app.secret_key = ".."
   app.run()