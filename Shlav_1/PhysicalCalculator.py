
MASS_WITHOUT_CARGO = 35,000
SPEED_OF_PLANE_TAKE_OFF = 140
F = 100,000
F_IN_KG = 10197.16213



"""
The function calculates the Acceleration.
input: cargoMass - the mass of the cargo that the user entered.
output: the Acceleration that was calculated.
"""
def calcAcceleration(cargoMass):
    return  (F/(MASS_WITHOUT_CARGO + cargoMass))


"""
The function calculates the needed time for takeOff.
input: acceleration - the acceleration that was calculated before.
output: the needed time for takeOff.
"""
def calcTimeTillTakeOff(acceleration):
    return (SPEED_OF_PLANE_TAKE_OFF/acceleration)


"""
The function calculated the takeoff distance of the plane.
input: acceleration: the acceleration that was calculated before, timeTillTakeOff - the needed time for the plane to take off.
output: the takeoff distance of the plane.
"""
def calcDistanceTillTakeOff(acceleration, timeTillTakeOff):
    return (0.5*acceleration*(timeTillTakeOff**2))




"""
The function gets by input the mass of the cargo from the user, then it calculated the acceleration, takeoff time and distance and prints it to the user.
then the function checks if there is a need in losing some cergo for the plane to takeoff.
"""
def main():
    cargoMass = input("Please enter the cargo mass in kg: ")
    acceleration = calcAcceleration(cargoMass)
    timeTillTakeOff = calcTimeTillTakeOff(acceleration)
    distanceTillTakeOff = calcDistanceTillTakeOff(acceleration, timeTillTakeOff)

    print("The distance it takes for the plane to take off is: ", distanceTillTakeOff)
    print("The time it takes for the plane to take off is: ", timeTillTakeOff)

    if(timeTillTakeOff > MAX_TIME_FOR_TAKEOFF):
        acceleration = SPEED_OF_PLANE_TAKE_OFF/ MAX_TIME_FOR_TAKEOFF
        planeMass = F/acceleration
        cargoMassToLose = (MASS_WITHOUT_CARGO + cargoMass) - planeMass
        print("The cargo is too heavy, please destroy " + cargoMassToLose + " kg worth of cargo.")




if __name__ == "__main__":
    main()
