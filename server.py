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
	"""Shows the page where user's can search for a restaurant """
	return render_template("index.html")

@app.route("/restaurant_results")
def show_rest_info():
	"""When the user submits their restaurant search, this gathers the user input to create the query request to 
	the Foursquare API. It then returns the response and sends it to the template"""
	
	# pull out parameters from request
	rest_name = request.args.get('rest-name')
	search_location = request.args.get('search-location')
	print (rest_name, search_location)

	fs_client_id = config.FS_CLIENT_ID 				# CAN I set these at the global level?
	fs_client_secret = config.FS_CLIENT_SECRET

	# create a python dict from the Foursquare API JSON response 
	fs_dict = foursquareapi.create_fs_dict(fs_client_id, fs_client_secret, rest_name, search_location) 	# Look in foursquareapi module and run the create_fs_dict function with the parameters here

	# parse that python dict to get just the part of the request w/needed info
	fs_venues_list = fs_dict['response']['venues']

	# print "FS Venues List: ", fs_venues_list

	return render_template("restaurant_results.html", 
		fs_venues_list=fs_venues_list)

# @app.route("/save_restaurant", methods=['POST'])		# FIXME: check to see if this this is the right route to use for the add_bookmark() controller function
# def save_restaurant():					# Do I need to make a call to the foursquare API again here to get the restaurant info to populate my tables? 
# 	"""Saves a restaurant to the database """
# 	return "add restaurant function started!" 
# 	saved_restaurant = 											# Do I need: json.dumps(session['restaurant'])??
# 	model.save_restaurant(session['email'], saved_restaurant) 	# pass in the saved restaurant 
# 	return "Added %s restaurant to the restaurants table" % (saved_restaurant)


# @app.route("/save_bookmark", methods=['POST'])		# FIXME: check to see if this this is the right route to use for the add_bookmark() controller function
# def save_bookmark():
# 	return "add bookmark function started!"


if __name__ == "__main__":
    app.run(debug = True)

# Work on login after map

# @app.route("/login")
# def display_login():
# 	# Displays login page
# 	return render_template("login.html")

# @app.route("/login", methods=['POST'])
# def login_user():
# 	# Makes POST request to get user input to log into account
# 	print "login function running"
# 	email = request.form['email']
# 	password = request.form['password']
# 	print (email, password)
# 	# login = model.login(email, password)	# need to create login function in model to tie this back to 
# 	return redirect("/login") 

# def save_object(obj_instance):
# 	try:
# 		session.add(obj_instance)
# 		session.commit()
# 		return 200
# 	except:
# 		return 500