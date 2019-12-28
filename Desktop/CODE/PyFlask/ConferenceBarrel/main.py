''' To run the application: 

-> Set the environment variable that contains the aplication
    The flask will look for this appication in the variable named «FLASK_APP»
-> use this command: 
                    $Env:FLASK_APP="main.py"

($Env:FLASK_APP="Any_Other_Name.py")


By default we need lways to restart server to see the changes,
but by setting «debug» variable we can change that: 
                    $Env:FLASK_DEBUG=1

After that all the chages will be seen after refreshing html page

-----------------------------------------
Flask Quick Guide:

=> To create new html page /OR/ «view»:
(«view» includes wraper «@app.route('pages')» + function «def page():»)
1. Create new html in the template
2. Create new route: @app.route('/new_page')
3. Create a function name same to wrap: def new_page():

=> To pass variable into html page
1. Pass first into: @app.roure('/newpage/<var_type:Variable')
2. Pass variable into function: def new_page(Variable):
3. Pass into html: render_template('new_page.html', variable_html=Variable)

=> To pass variable from the funtion into other html page if «redirect» is used:
1. Pass varriable into «redirect»: redirect(url_for('new page', Variable=var_name))
2. Than use "To pass variable into html page" instrutions

=> To create sub-pages wrap sub-page into main page
1. Wrap into main page: @app.route('/main_page')
2. Wrap into sub-page: @app.route('/main_page/sub_page')
3. Create a function with same name as sub-page: def sub_page():

=> To protect html page with login seccion
(Only can be accessed if login seccion id opened)
1. Wrap into html page: @app.route('/html_page')
2. Wrap into login wrap: @login_required
3. Create the function of thml page: def html_apges(): 


'''


# Import Flask application object
# reneder_template() -> to render html page inside the «basetemplatepage.html»
# abrot() -> to display «404» error if page does not exists
# reuest to 'POST' and 'GET' data from data base (used in search form)
from flask import Flask, render_template, abort, request, redirect, url_for, flash


# Library for user login control
# To import it you need to install it -> pip install flask_login
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user


# Import SQLAlchemy to manage DB
from flask_sqlalchemy import SQLAlchemy


# Importing Flask API and Resource
from flask_restful import Api, Resource 


# Date time for db use
from datetime import datetime


# New instance of a Flask bject to handle http trafic
# Value passed into initializer is the default module for assets to be found
# For large application it is better to have assets in a several modules for usability
# For small application it is not necessary
app = Flask(__name__)


# Flask Restful API initializer
# assotiate url rules with resources
# the resource will handle the http request ad send back response in Json
api = Api(app)

####### Setting up the data base
# We will use Flask-SQLAlchemy to write code and test on SQLite
# As this code can be used on others data bases we will then use PotrageSQL to implement app on Heroku

# Path to the sql db
# To use another data base (PostregeSQL) we will need just to use another path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conferencebarrel.sqlite'

# Dissable a Flask warning - no reason why it is appear
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Pass SQLAlchemy with initilizer into new variable for future use
db = SQLAlchemy(app)


# Storing secret key for flask seccionas in the configuration manager
# You need a strong key, but can be used simple one for testing
app.config['SECRET_KEY'] = 'flaskproject'

# Setting up a flask login manager object which setup flask application for falsk login
login_manager = LoginManager()
login_manager.init_app(app)
# To redirect page to login when user is logout
login_manager.login_view = 'login'

#################################
#           DB MODELS           #


# DB for Conferences
# Create a class to manage Conference DB:
class Conference(db.Model):
    #### this vars: «id», «title»,«date»,«ticket_cost» => will be used in the html page inside the « block » : <h3> Conference name: {{conference_details.title}} </h3>
    # field name = database.Column(value/field type, constrains «primary_key=True», «nullable=False» (NOT NULL), «default=datetime.utcnow»(if an object is not assigned by defaut it will assume todays date)) 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ticket_cost = db.Column(db.Float, nullable=False)
    # Establish Manay to Many relationship to «ConferenceBarrelUser» through «ConferenceBarrelTickets» table
    attendees = db.relationship('ConferenceBarrelUser', secondary='conference_barrel_tickets')

    # Function for string representation of the method
    def __repr__(self):
        return f'Conference {self.title}'


# DB for users
# Setting up the class for used data
# User Class will inherit UserMixin class
# For thsi case use defualt configurations
class ConferenceBarrelUser(db.Model, UserMixin):
    # add «id», «username» and «password» to a data base
    # «id» will be automatically generated
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Establish Manay to Many relationship to «Conference» through «ConferenceBarrelTickets» table
    conferences = db.relationship('Conference', secondary='conference_barrel_tickets')

    def __init__(self, username, password):
        self.username = username
        self.password = password


# To prepare data base to store the username and password use «ipython»
# type «ipython» -> from main import db, ConferenceBarrelUser
# create data base by «db.create_all()»


# DB for relating two columns «Conference» and «ConferenceBarrelUsers»
# This is intermedia table in Many to Many relation
# Create a class to manage Conference DB:
class ConferenceBarrelTickets(db.Model):
    #### this vars: «id», «title»,«date»,«ticket_cost» => will be used in the html page inside the « block » : <h3> Conference name: {{conference_details.title}} </h3>
    # field name = database.Column(value/field type, constrains «primary_key=True», «nullable=False» (NOT NULL), «default=datetime.utcnow»(if an object is not assigned by defaut it will assume todays date)) 
    id = db.Column(db.Integer, primary_key=True)
    # To reference this collumn to other use «name_of_the_table.id»
    # Every name of the tabe is converted «TableName» -> into -> «table_name»
    user_id = db.Column(db.Integer, db.ForeignKey('conference_barrel_user.id'))
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'))
    # We would use to generate code to access related into in other tables by «user» and «conference» «id» 
    # Hoever with SQLAlchemy we can reference class models directly to acess particular info fro the table without referencing «id»
    # var related to db «ConferenceBarrelUser» with back reference to filed «ticket», and with «lazy='dynamic'» not load untiil data is accessed
    # for thsi relationship work we need to add same relations into Model classess related here: «ConferenceBarreslUser» and «Conference»
    user = db.relationship(ConferenceBarrelUser, backref=db.backref('tickets', lazy='dynamic'))
    conference = db.relationship(Conference, backref=db.backref('tickets', lazy='dynamic'))

# After creatign intermedia table «ConferenceBarrelTickets» between «Conference» and «ConferenceBarrelUser» table
# Update the the intermedia table «ConferenceBarrelTickets» through the ipython or in thr way

#### All 3 tabes are contained inside «conferencebarrel.sqlite» db file -> was created manualy



'''
# Inserting data into DBs: 
After creation of class MODEL «Conference» or any other class MODEL
 -> VIEW FILE CALLED «manage_db_in_terminal_info»
 for How to insert data into data base

'''

#           DB MODELS           #
#################################



# Function for http requests
# We need to use wrapper to wrapp this function in a https response -> To wich request should be handled by this function
## -> Every wrapper need to have same name that function: @app.route('/Nome1') -> def Nome1()
# We wrapp httpm request to a «index» function wich can return text into html page or html page, or other contentn into html page
## -> To readdress the main page «http://127.0.0.1:5000/» to «/index» use @app.route('/')
@app.route('/')
@app.route('/index')
def index():
    #To pass plain text into html just type: «return "Conference Barrel"»
    #To return html page use templates function «return render_template('name.tml')»
    return render_template('index.html')



### html for «about» page
# Add another wrapper to add new function that will create html content
@app.route('/static/about')
def about():
    return 'About this Conference Barrel'


### html for «conferences» page
### html for «/conferences/<conference_id>» page
# -> To pass any numeric value into html page = define variable in wrapper: <conference_id>
# and pass it into function 
# -> To specify var type add «int» : <int:conference_id>
# -> To create a page for "conferences" only just create another wrapper above existant function 
## -> You can have multiple route to decorate (wrap) a single function
#####  Explanation: if there is «number» after «/conference/» display «details.html»
#####               Else (if there is NO «number» after «/conference/») display «conferences.html»

Conf_num = 0

@app.route('/conferences')
@app.route('/conferences/<int:conference_id>')
## -> Add the default of "None" so the if would function properly
def conferences(conference_id=None):
    if conference_id is not None:
        # declare global variable to pass into it any «conference_id» to pass into «404» error page
        global Conf_num
        Conf_num = conference_id
        # return text with variable passed into function and wrapped into html request wrapper previously
        # return f'Detailes about conference {conference_id}'
        ### Import all values from table by field ID
        conference_details = Conference.query.get(conference_id)
        # If «conference_details» object is None display «404» page error
        if conference_details is None:
            abort(404)
        # «conference_details» - is var to pass all conference info
        return render_template('details.html', conference_details=conference_details)
    else:
        # To view data base just use variable to pass data base values: conferences = Conference.query.all()
        return render_template('conferences.html', conferences=Conference.query.all())


# Function for 404 error for non-existing web page
@app.errorhandler(404)
def handle_404(e):
    # «return» function is a tuple so you can add another argument after comma «,»
    return render_template('404.html', Conf_num=Conf_num),404


# Function for 401 error for user login
@app.errorhandler
def handle_401(e):
    return redirect(url_for('login'))


# to search data base with «request» method from Flask
# To use other method than 'GET' (wich is defined by default) add into «@app.route» oher methods: methods=['GET', 'POST']
@app.route('/search', methods=['GET', 'POST'])
def search():
    # get the form method from search form with «request» method
    if request.method == 'POST':
        # var that passes value into search query
        # name of html form input filed 'needle'
        needle = request.form['needle']
        # Pass result into «result» 
        ### => «filter» «Conference» data base by «title» «like» in «needle» varibale + search for «all()»
        # «%» meanins anything after and aything before the value in the «needle»
        results = Conference.query.filter(Conference.title.like(f'%{needle}%')).all()
        # «return» «results.html» page with «results» from querying data base
        return render_template('results.html', results=results)
    else:
        return render_template('search.html')



# Routing function to login users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Name of html form input filed 'username'
        username = request.form['username']
        # Name of html form input filed 'password'
        password = request.form['password']
        # to filter query/filter username and password in db
        usrnm_frm_db = ConferenceBarrelUser.query.filter(ConferenceBarrelUser.username == username).filter(ConferenceBarrelUser.password == password).first()
        # To check if there is much on username and password
        if usrnm_frm_db is None:
            flash('Invalid username and/or password!')
            return redirect(url_for('login'))
        login_user(usrnm_frm_db)
        # «usrname» -> passes username into the «@app.route('/secret_data/<username>')» wraper  AND  «def secret_data(username)» function 
        return redirect(url_for('secret_data', username=username))
    else:
        return render_template('login.html')

# Creating protected resource
# Passing «<username>» variable into the wraper to pass it into the function
@app.route('/secret_data')
@login_required # To protect this page from unauthorized access
def secret_data():
    # Formating varible appearence: username=str(username).capitalize()+' ('+username+')'
    return render_template('secret_data.html')

# create a logout function
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Create a funtion that will take the user id and return the content with that id
# this function is called after user is authenticated
@login_manager.user_loader
def load_user(id):
    return ConferenceBarrelUser.query.get(id)
    # If you don't put «(id)» in the end the error is: AttributeError: 'function' object has no attribute 'is_authenticated'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # Check if username does already exist in the data base
        usrname = ConferenceBarrelUser.query.filter(ConferenceBarrelUser.username == username).first()


        # Verify if username was typed into form field
        if username == '':
            # Show flash message explainig what happend
            flash("Username can't empty!")
            # return back to register page
            return redirect(url_for('register'))


        # if username is NOT NONE return register page again
        if usrname is not None:
            # Show flash message explainig what happend
            flash('Username already exists')
            # return back to register page
            return redirect(url_for('register'))


        # Verify if passwords match
        passwords_match = password1 == password2

        # if passwords does NOT match return register page again
        if passwords_match is False:
            flash("Passwords doesn't match!")
            return redirect(url_for('register'))
        
        # Pass user credentials into var «usr_data_nm_pss» 
        usr_data_nm_pss = ConferenceBarrelUser(username, password1)

        # Add user credentials into data base session
        db.session.add(usr_data_nm_pss)

        # Write user credentials into «ConferenceBarrelUser» data base
        db.session.commit()

        # If everythong is good redirect to login page
        return redirect(url_for('login'))
    else:
        # If method used is not 'POST' redirect to «register.html»
        return render_template('register.html')


# To create a new ticket
# - and than redirect user to a «prefile» view/html page
@app.route('/new_ticket/<int:conference_id>')
@login_required
def new_ticket(conference_id):
    # Before querying the «conference_id» it should be add ErrorHandling
    # - but it will be omited in here
    conference = Conference.query.get(conference_id)
    ticket = ConferenceBarrelTickets(user=current_user, conference=conference)
    # Insert inserted data into data base
    # we need to check for a duplicates, but not in this demo
    db.session.add(ticket) # add to the session
    db.session.commit() # write into db -> make the changes
    return redirect(url_for('profile'))


# Personal user profile:
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')



# Resource to retrive the list of conferences
# The resource class has a methods for each http methods: «GET», «PUT», «POST»
class ConferenceResource(Resource):
    # to retrive a list of conferences
    # «def get(self)» will handle http get request
    # Passed variable («conference_id») has to have value
    def get(self, conference_id=None):
        # Return value is a list of dictionaries: one dictionary for each «Conference Model» in the data base
        # Flask-RESTful wil strigify the content and return pure Json
        # To re-use the resource to give the details of the single conference
        ## If «conference_id» is None retrieve all conferences «id» and «title»
        if conference_id is None:
            return [ 
                {
                    'id': conference.id,
                    'title': conference.title
                }
                # loop through the conferences
                for conference in Conference.query.all()
            ]
        # «Else» (if there are conference id), query all caonferences in data base
        # - and retrieve conference details 
        else:
            conference = Conference.query.get(conference_id)
            return {
                'id': conference.id,
                'title': conference.title,
                'date': conference.date.strftime('%m/%d/%Y'),
                'ticket_cost': conference.ticket_cost,
                'attendee_count': len(Conference.query.all())
            }


# To associate «Resource» with «url rule» the API instace provides the «Add resource» method
api.add_resource(ConferenceResource, '/api/conferences', '/api/conferences/<int:conference_id>')