Bite
===========

Bite is an app for food lovers and compulsive organizers. It offers a convenient way to save, view, and recommend restaurants to friends. 

![Home Page](https://github.com/gabygandrade/FoodMapper/blob/master/static/img/home-srcshot.png)

##Technology Stack

Python, Flask, SQLAlchemy, SQLite, Javascript, jQuery, AJAX, Google Maps API, Foursquare API, HTML5 Geolocation API, HTML5, Jinja, CSS3

#Features
- Login
- Restaurant search by location and restaurant name or cuisine
- Bookmarks
- Bookmark deletion
- User-to-user recommendations
- Proximity-based restaurant mapping
- Detection of user location
- Client-side validation

![Welcome Page](https://github.com/gabygandrade/FoodMapper/blob/master/static/img/welcome-srcshot.png)

##Technologies

###Foursquare API
To get up-to-date and crowd sourced restaurant information, Bite uses the Foursquare venues API. When a user searches for a restaurant or cuisine in a given location, a function is called which dynamically creates an HTTP GET request to the Foursquare Venues API. This request includes the user’s query information as parameters, as well as a category id limiting the response to only include venues in the Foursquare “food” category. The response is then decoded from JSON to a python dictionary and sent to the search results page.

![Search Results Page](https://github.com/gabygandrade/FoodMapper/blob/master/static/img/search-results-srcshot.png)

###Google Maps API
On load of the map page, a SQLAlchemy query runs which queries the database for the user’s bookmarks and the associated restaurant information, including latitude and longitude. This information is sent over as JSON to the route, which loops through all the bookmarks, and places pins on the map using the Google Maps API. 
Many different features and combinations of features (ngrams, stopwords, stemming, different tokenization functions, etc.) were used to find the result with the most accuracy in predicting positive and negative tweets, and the highest precision and recalls scores across both labels. After training, the classifier was then serialized via the python module Pickle. The pickle file was then opened and the saved classifier used to determine the sentiment of incoming live tweets.

![Maps Page](https://github.com/gabygandrade/FoodMapper/blob/master/static/img/map-srcshot.png)

###HTML5 Geolocation API
Bite integrates the HTML5 Geolocation API with the Google Maps API, the browser asks the user whether it can access its current location. If so, the location information is sent over to the function that creates the Google Map, and the map is centered around the user’s current location. If geolocation fails or the user does not authorize it, the map defaults to San Francisco.

This functionality allows users visiting neighborhoods where they have bookmarked restaurants the flexibility of opening the app and seeing bookmarked restaurants in their proximity. 

###SQLAlchemy ORM
####Bookmarks 
After getting back a list of search results from the Foursquare API, users select the restaurant they would like to save as a “bookmark.” When a user saves a bookmark, there is a server side check with SQLAlchemy for whether it has already been bookmarked for that user and whether the restaurant is already in the database of restaurants. If the restaurant and bookmark are not already in database yet, their API information is cached in order to optimize load time. 

####Recommendations
From the search results page that users see when they submit a restaurant search, users also have the options to recommend restaurants to other users registered with Bite. Once a user selects the user to send the recommendation to, SQLAlchemy queries check whether the recipient already has that restaurant bookmarked and whether the recommender has already recommended that restaurant to the recipient. If both of those conditions are not true, a new recommendation is created in the database.

Upon login, users who have pending recommendations are prompted to view and respond to recommendations by accepting or passing on specific recommendations. When a user responds to a recommendation, the pending attribute of the recommendation is changed from True to False. If they accept a recommendation, new bookmark and bookmarkrecommendation records are created with the restaurant and user information from that recommendation. 

![Recommendations Page](https://github.com/gabygandrade/FoodMapper/blob/master/static/img/recommendations-scrshot.png)



