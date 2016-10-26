# Startup Jobs (Project 5)

### Instructions

Copy the files to the provided Udacity vagrant virtual environment.

#### Database creation

The database should already be created but to rollback to its initial state, run the following command from the database directory:

```
python create_database.py
```

Then to populate with some sample data, run:

```
python populate_database.py
```

#### Running the server

In the app folder, run the following command to load the server:

```
python server.py
```

You can then access the website from `http://localhost:5000`. 

#### Using the API

You can retrieve json parsed results of individual startups or all the startups for each city.

To retrieve an individual startup, append json to the end of the url for the city you wish to retrieve information on:

```
http://localhost:5000/city/new-york/breather/json
```

To retrieve all the startups for an individual city, append json to the end of the city in the url:

```
http://localhost:5000/city/new-york/json
```

### Code

* server.py - Handlers and main server application
* client\_secret.json - oAuth json data that assists in creating the credentials object for oAuth
* /database/create\_datbase - Delete (if it exists) and create a new startup database
* /database/populate\_database.py - Populate database with some initial cities and startups
* /database/schema.py - The schema and instance methods
* /database/startup.db - The database
* /helpers/ - Different helpers to assist in database queries, template building, and validating
* /static/ - Javascript and css assets
* /templates/ - All the templates
