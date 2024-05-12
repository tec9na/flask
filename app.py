#importere de nødvendige moduler og klasser fra Flask osv
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)                                                    # Oprettelse af Flask-instans
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"            # Konfirguration med database-URI (URI bruges til at identificere ressourcer dermed ved SQLALCH hvor den skal oprette forbindelse til)
app.config["SECRET_KEY"] = "abc"                                         # Hemmelig nøgle til sessionshåndtering - sikre kryptering af data - abc bruges til at kryptere og dekryptere
db = SQLAlchemy()                                                        # SQLAlchemy objekt som bruges til at kunne interagere med databasen

login_manager = LoginManager()                                      # Oprettelse af et LoginManager objekt
login_manager.init_app(app)                                         # Objekt intialiseres med Flask-app'en


class Users(UserMixin, db.Model):                                            # Definere klassen Users, som "repræsentere" vores brugertabel i databasen, Users arver fra 2 klasser; UserMixin(klasse fra Flask-Login, indebære brugerauthenificering og sessionshåndtering) og db.Model(klasse fra SQLAlchemy, definere modeller og oprettelse af databasetabeller)    
    id = db.Column(db.Integer, primary_key=True)                             # Variabel der definere en kolonne i Users med navnet "id", kolonnen er int og primary_key=True betyder at hver række i kolonnen er unik
    username = db.Column(db.String(250), unique=True, nullable=False)        # Variabel der definere en kolonne i Users med navnet "username", --#-- er en str og har en maks længde på 250 tegn, unique=True betyder at hvert username skal være unikt, nullable=False betyder at feltet skal have en værdi
    password = db.Column(db.String(250), nullable=False)                     # Variabel der er det samme som ovenstående bare ikke nødvendigt at den er unik


db.init_app(app)               # Initialisere vores SQLAlchemy objekt (db), ved at knytte det til vores Flask-app (app)


with app.app_context():        # Bruges til at skabe databasetabeller baseret på det vi har defineret vha SQLAlchemy, app.app_context() er mega svært - forstår det ikke - hverken with eller app.app_context
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):                # Definere load user funktion fra Flask-Login, bruges til at hente brugeren fra databasen baseret på brugerens id. 
    return Users.query.get(user_id)      # SQLAlchemy query bruges til at få adgang til databasen, Users.query refererer til Users-tabellen og .get(user_id) bruges til at hente den enkelte række fra tabellen baseret på brugerens id.


@app.route('/register', methods=["GET", "POST"])                     # Registreringsrute: Håndtere både "GET" og "POST" til registrering, app.route er en "rute" fra Flask
def register():                                                      # Definere funktionen register()
    if request.method == "POST":                                     # if-statement der kontrollere om anmodning er en POST - brugeren har sendt en registreringsformular
        username = request.form.get("username")                      # Henter username og password fra .form? idk
        password = request.form.get("password")                      # --#--
        hashed_password = generate_password_hash(password)           # Hasher adgangskoden vha "generate_password_hash()" fra Werkzeug-biblioteket
        user = Users(username=username, password=hashed_password)    # Oprettelse af en ny bruger i databasen ved at oprette en instans af "Users"
        db.session.add(user)                                         # Vi tilføjer den nye bruger til databasen og foretager ændringerne permanent ved at kalde commit() på sessionsobjektet
        db.session.commit()                                          # --#--
        return redirect(url_for("login"))                            # Efter vellykket oprettelse af brugeren omdirigeres brugeren til login-siden ved hjælp af redirect() og url_for().
    return render_template("sign_up.html")                           # Hvis anmodningen er en GET-anmodning, vises registreringssiden sign_up.html


@app.route("/login", methods=["GET", "POST"])                              # Loginrute: --#-- henter username og password fra 
def login():                                                               # Definere funktion login()
    if request.method == "POST":                                           # if-statement der kontrollere om anmodningen er en POST, brugeren har sendt login-formularen
        input_username = request.form.get("username")                      # Henter username og password fra .form som brugeren har sendt via POST-anmodningen  
        input_password = request.form.get("password")                      # --#--
        user = Users.query.filter_by(username=input_username).first()      # Vi henter brugeren fra databasen baseret på det indtastede brugernavn. filter_by() filtrerer brugere efter brugernavn, og first() returnerer den første bruger, der opfylder betingelsen
        if user and check_password_hash(user.password, input_password):    # Vi kontrollerer, om der er fundet en bruger med det angivne brugernavn, og om den indtastede adgangskode matcher den gemte hash-værdi i databasen. Dette gøres ved at bruge check_password_hash-funktionen fra Werkzeug-biblioteket til at sammenligne adgangskoderne
            login_user(user)                                               # Hvis brugernavn og adgangskode er gyldige, logger vi brugeren ind ved hjælp af login_user()-funktionen fra Flask-Login. Dette initialiserer brugersessionen og gør det muligt for brugeren at få adgang
            return redirect(url_for("home"))                               # Efter vellykket login omdirigeres brugeren til hjemmesiden ved hjælp af redirect() og url_for()
        else:                                                             
            return "Invalid username or password. Please try again."       # else-statement der returnere en fejlbesked til brugeren - hvis brugernavn eller adgangskode ikke er gyldig - og opfordres til at prøve igen.
    return render_template("login.html")                                   # Hvis anmodningen er en GET-anmodning, vises login-siden login.html


@app.route("/logout")                        # Dette er en logout rute
def logout():                                # Definere funktion logout()
    logout_user()                            # Funktionen bruges til at logge brugeren ud og omdirigere tilbage til "home"
    return redirect(url_for("home"))         # --#--


@app.route("/")                              # Startside/"home" rute
def home():                                  # Definere funktion home()
    return render_template("home.html")      # Her render vi en HTML skabelon, der repræsentere vores hjemmeside - under templates mappen ligger filen


if __name__ == "__main__":      # Ved ikke, men sikre at Flask-app'en kun køres når filen køres direkte
    app.run()