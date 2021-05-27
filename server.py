#!/usr/bin/python3

from flask import Flask, render_template, Response, url_for
from os import system as cmd
from irBlaster import blast

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/numbers')
def numbers():
	return render_template('numbers.html')

@app.route('/extra')
def extra():
	return render_template('extra.html')
	
@app.route('/light')
def light():
	return render_template('light.html')

@app.route('/disco')
def disco():
	return render_template('disco.html')

@app.route('/query/<keyName>')
def keyHandler(keyName):
	blast(keyName, "nec")
	print("Blasted " + keyName)
	return "nothing"

@app.route('/query/necx/<keyName>')
def necxKeyHandler(keyName):
	blast(keyName, "necx")
	print("Blasted " + keyName)
	return "nothing"
    
@app.route('/redirect/<keyName>')
def redirectHandler(keyName):
	blast(keyName, "nec")
	print("Blasted " + keyName)
	return index()
    
## Start webserver
if __name__ == '__main__':
	from waitress import serve
	serve(app, host='0.0.0.0', port=80)
