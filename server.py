from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response 
from flask import session as fsess
# import model
import jinja2
import os
import foursquareapi
import config

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
app.jinja_env.undefined = jinja2.StrictUndefined 

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/restaurant_results")
def show_rest_info():
	"""When someone submits their restaurant search, this gathers that query info to create the request to the Foursquare API"""
	
	# pull out parameters from request
	rest_name = request.args.get('rest-name')
	search_location = request.args.get('search-location')
	print (rest_name, search_location)

	fs_client_id = config.FS_CLIENT_ID
	fs_client_secret = config.FS_CLIENT_SECRET

	# create a python dict from the Foursquare API JSON response 
	fs_dict = foursquareapi.create_fs_dict(fs_client_id, fs_client_secret, rest_name, search_location) 	# Look in foursquareapi module and run the create_fs_dict function with the parameters here
	
	# parse that python dict to get just the part of the request w/needed info
	fs_venues_list = fs_dict['response']['venues']

	return render_template("restaurant_results.html", fs_venues_list=fs_venues_list)

if __name__ == "__main__":
    app.run(debug = True)

""""Work on login after get map working:

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    # print "login function running"
    # email = request.form['email']
    # password = request.form['password']
    # print (email, password)
    return redirect("/")
"""