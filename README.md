Uber Coding Challenge: San Francisco Movie Locator

- The project is hosted on heroku:

[[Project live demo](http://uber-sf-movie.herokuapp.com)]


Project Scope: This is a simple service that allows user to search the movies within San Francisco with the autocomplete search functions. The movie data is providedby DataSF.


Author: Jason Qiu

Brief Summary of the design

Web Framework: Flask 

Reason: 1. Light weighted 2. Python based. 3. Support Restful service

Storage Service: Redis Cloud

Reasons: 1. Fast. 2. Simple. 3. Support various data structures for optimizing auto complete

Front End:
jQuery plugins(gmap, autocomplete) + Bootstrap 

Reasons: 1. Save time. 
