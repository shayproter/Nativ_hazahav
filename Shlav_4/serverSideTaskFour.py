from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
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
MIN_TEMP_FOR_TAKEOFF = 15
MAX_TEMP_FOR_TAKEOFF = 30
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
The function gets a certain date, enters a weather API with the following data: lat, lon, date. The function that gets a response from the API,
checks  if the response was not an error, and then checks in which hour the temperature is between 15 and 30, then the function returns those hours
along with the average temperature in this day and a boolean variable to say if the plane can takeoff in this date or not.
"""
def get_weather_data():
    lat = "30"
    lon = "35"
    canThePlaneTakeoff = False
    date = "2023-01-01"
    hour_range = []
    TakeoffTemp = 0

    #creating the url for the weather API
    url = f"https://api.open-meteo.com/v1/forecast?latitude=" + lat + "&longitude=" + lon + "&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto&start_date=" + date +"&end_date="+ date
    #getting a response from the API
    response = requests.get(url)
    weather_data = json.loads(response.content.decode())
    print(weather_data)

    if response.status_code == 200: #validating the response
        tempByHour = weather_data['hourly']
        dailyStats = weather_data['daily']
        #getting the response needed fields

        hours = list(tempByHour['time'])
        temps = list(tempByHour['temperature_2m'])
        TakeoffTemp = sum(temps) / len(temps) #calculating the average temperature

        if len(dailyStats['temperature_2m_max']) == 1: #checking if the response should be further checked by validating that the minimum and maximum are in the right range of temperature.
            maxTemp = int(dailyStats['temperature_2m_max'][0])
            minTemp = int(dailyStats['temperature_2m_min'][0])
            if maxTemp < MIN_TEMP_FOR_TAKEOFF or minTemp > MAX_TEMP_FOR_TAKEOFF:
                return hour_range, canThePlaneTakeoff, TakeoffTemp

        #checking in which hours the temperature is in the wanted range (15-30)
        if len(hours) == len(temps):
            for hour, temp in zip(hours, temps):
                try:
                    if int(temp) >= MIN_TEMP_FOR_TAKEOFF and int(temp) <= MAX_TEMP_FOR_TAKEOFF:
                        hour_range.append(hour[-5:])
                        canThePlaneTakeoff = True

                except TypeError:
                    pass

    return hour_range, canThePlaneTakeoff, TakeoffTemp
    #returning the hours that in which the temperature is in the wanted range, a boolean that says if the plane can take off and the average temperature.



"""
The function gets input from the user(cargo mass, date), validating the user input, calculating the needed time till take off, the 
takeoff distance and creating a response, checking if theres any need to lose cargo, then inserting the calculated statistics to the database, getting the weather statistics and creating a response for the user. 
Input: none.
Output: the response containing all of the statistics.
"""
def calculate():
    cargo_mass  = request.json.get("cargo_mass")
    cargo_mass_to_lose = 0
    response = {}

    if cargo_mass is None: #validating the input
        return jsonify({"message": False}), 400
    if type(cargo_mass) != int or cargo_mass < 0 :
        return jsonify({"message": False}), 400
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


    #creating the final response and getting the weather stats by the date.
    weatherStats, canPlaneTakeoff, tempInTakeoff = get_weather_data()
    response['message'] = True
    response['flight_statistics'] = flightStatsResponse
    response['hours_for_takeoff'] = weatherStats
    response['can_plane_takeoff'] = canPlaneTakeoff
    response['temp'] = tempInTakeoff
    return jsonify(response)


@app.route("/", methods=["POST"])
def index():
    return calculate()



app.run(debug=True)
