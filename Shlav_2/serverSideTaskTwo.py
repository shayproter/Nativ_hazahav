from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
db = SQLAlchemy(app)
load_dotenv('./.flaskenv')


#defining constant variables
MASS_WITHOUT_CARGO = 35000
SPEED_OF_PLANE_TAKE_OFF = 140
F = 100000
F_IN_KG = 10197.16213
MAX_TIME_FOR_TAKEOFF = 60

"""
The function calculates the Acceleration.
input: cargoMass - the mass of the cargo that the user entered.
output: the Acceleration that was calculated.
"""
def calcAcceleration(cargoMass):
    return (F / (MASS_WITHOUT_CARGO + cargoMass))

"""
The function calculates the needed time for takeOff.
input: acceleration - the acceleration that was calculated before.
output: the needed time for takeOff.
"""
def calcTimeTillTakeOff(acceleration):
    return (SPEED_OF_PLANE_TAKE_OFF / acceleration)

"""
The function calculated the takeoff distance of the plane.
input: acceleration: the acceleration that was calculated before, timeTillTakeOff - the needed time for the plane to take off.
output: the takeoff distance of the plane.
"""
def calcDistanceTillTakeOff(acceleration, timeTillTakeOff):
    return (0.5 * acceleration * (timeTillTakeOff ** 2))


"""
The function created the session that will be inserted to the database.
input: cargo_mass - the cargo mass that was entered by the user, distance_till_take_off - the takeoff ditance that was calculated,
cargo_mass_to_lose - the needed cargo mass to lose that was calculated, time_till_take_off - the takeoff time that was calculated.
"""
class calculationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cargo_mass = db.Column(db.String(100), unique=True, nullable=False)
    distance_till_take_off = db.Column(db.String(100), unique=True, nullable=False)
    cargo_mass_to_lose = db.Column(db.String(100), unique=True, nullable=False)
    time_till_take_off = db.Column(db.String(100), unique=True, nullable=False)




"""
The function gets input from the user(cargo mass), validating the user input, calculating the needed time till take off, the 
takeoff distance and creating a response, checking if theres any need to lose cargo and then inserting the calculated statistics to the database.
Input: none.
Output: the response containing all of the statistics.
"""
def calculate():
    cargo_mass  = request.json.get("cargo_mass")
    cargo_mass_to_lose = 0
    response = {}

    if cargo_mass is None: #validating the input
        return jsonify({"message": "100"}), 400
    if type(cargo_mass) != int or cargo_mass < 0 :
        return jsonify({"message": "200"}), 400
    acceleration = calcAcceleration(cargo_mass)

    #calculating the takeoff time and distance.
    time_till_take_off = calcTimeTillTakeOff(acceleration)
    distance_till_take_off = calcDistanceTillTakeOff(acceleration, time_till_take_off)

    #creating response
    flightStatsResponse = {"distance_till_take_off": distance_till_take_off, "time_till_take_off": time_till_take_off}

    if (time_till_take_off > MAX_TIME_FOR_TAKEOFF): #checking if there is any need in losing cargo.
        acceleration = SPEED_OF_PLANE_TAKE_OFF / MAX_TIME_FOR_TAKEOFF
        plane_mass = F / acceleration
        cargo_mass_to_lose = (MASS_WITHOUT_CARGO + cargo_mass) - plane_mass
        flightStatsResponse["cargo_mass_to_lose"] = cargo_mass_to_lose

    #inserting the statistics to the nySQL data base.
    flightStatsSession = calculationSession(cargo_mass=str(cargo_mass), distance_till_take_off=str(distance_till_take_off), cargo_mass_to_lose=str(cargo_mass_to_lose), time_till_take_off=str(time_till_take_off))
    db.session.add(flightStatsSession)
    db.session.commit()


    #creating the final response
    response['message'] = ''
    response['flight_statistics'] = flightStatsResponse
    return jsonify(response)


@app.route("/", methods=["POST"])
def index():
    return calculate()



app.run(debug=True)
