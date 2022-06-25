import requests
import json
from datetime import datetime #NORMALISE RACE/LAP DELTA
import statistics as stat
import functools

def getRaceDate(year,Race):
    inputs2 = requests.get("http://ergast.com/api/f1/"+year+"/"+Race+"/results.json")
    unparsed2 = inputs2.text
    parse2 = json.loads(unparsed2)
    EventInfo = parse2["MRData"]['RaceTable']["Races"][0]
    raceName = EventInfo['raceName']
    Circuit = EventInfo["Circuit"]["circuitName"]
    date = EventInfo["date"]
    Event = [raceName,Circuit,date]
    return Event

def getLaptimes(Driver,year,Race):
    inputs1 = requests.get("http://ergast.com/api/f1/"+year+"/"+Race+"/drivers/"+Driver+"/laps.json?limit=80")
    unparsed1 = inputs1.text
    parse1 = json.loads(unparsed1)
    i = 0
    DriverLaptimes = []
    try:
        len(parse1["MRData"]['RaceTable']['Races'][0]["Laps"])
    except:
        return 
    while i < len(parse1["MRData"]['RaceTable']['Races'][0]["Laps"]):
        input_time = parse1["MRData"]['RaceTable']['Races'][0]["Laps"][i]["Timings"][0]['time']
        try:
            x = datetime.strptime(input_time,'%M:%S.%f')
            outputTime = x.minute*60+x.second+x.microsecond/1000000
        except:
            outputTime = 0
        #Output = [i+1,outputTime]
        DriverLaptimes.append(outputTime)
        i +=1
    return DriverLaptimes

def checkTeam(Driver,race,year):
    inputsRace = requests.get("http://ergast.com/api/f1/"+year+"/"+str(race)+"/drivers/"+Driver+"/results.json")
    unparsedRace = inputsRace.text
    parseRace = json.loads(unparsedRace)
    Intermediate = parseRace["MRData"]['RaceTable']["Races"]
    if Intermediate:
        results = Intermediate[0]["Results"]
    for i in results:
        if i["Driver"]["driverId"] == Driver:
            team = i["Constructor"]["constructorId"]
    return team

def getQualiData(Driver,year,race):
    inputs1 = requests.get("http://ergast.com/api/f1/"+year+"/"+race+"/drivers/"+Driver+"/qualifying.json")
    unparsed1 = inputs1.text
    parse1 = json.loads(unparsed1)
    try:
        parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]
    except:
        return 
    QualiPosition = int(parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]["position"])
    if "Q2" in parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]:
        input_time = parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]["Q2"]
        QualiRound = 2
        if input_time == '':
            return QualiPosition, QualiRound, 0
        x = datetime.strptime(input_time,'%M:%S.%f')
        QualiTime = x.minute*60+x.second+x.microsecond/1000000
    if "Q1" in parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]:
        input_time = parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]["Q1"]
        QualiRound = 1
        if input_time == '':
            return QualiPosition, QualiRound, 0
        x = datetime.strptime(input_time,'%M:%S.%f')
        QualiTime = x.minute*60+x.second+x.microsecond/1000000
    if "Q3" in parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]:
        input_time = parse1["MRData"]['RaceTable']["Races"][0]["QualifyingResults"][0]["Q3"]
        QualiRound = 3
        if input_time == '':
            return QualiPosition, QualiRound, 0
        x = datetime.strptime(input_time,'%M:%S.%f')
        QualiTime = x.minute*60+x.second+x.microsecond/1000000
    return QualiPosition, QualiRound, QualiTime

def getPositionData(Driver,year,race):
    inputsRace = requests.get("http://ergast.com/api/f1/"+year+"/"+race+"/drivers/"+Driver+"/results.json")
    unparsedRace = inputsRace.text
    parseRace = json.loads(unparsedRace)
    try:
        RaceStartPosition = parseRace["MRData"]['RaceTable']["Races"][0]["Results"][0]["grid"]
        RaceFinishPosition = parseRace["MRData"]['RaceTable']["Races"][0]["Results"][0]["position"]
        RaceFinishText = parseRace["MRData"]['RaceTable']["Races"][0]["Results"][0]["positionText"]
        RaceFinishData = parseRace["MRData"]['RaceTable']["Races"][0]["Results"][0]["status"]
    except:
        return False
    return RaceStartPosition,RaceFinishPosition,RaceFinishText, RaceFinishData

def Racedata(Driver1Name,Driver2Name,year,Race):
    driver1data ={}
    driver2data = {}
    PositionDataD1 = getPositionData(Driver1Name,year,Race)
    PositionDataD2 = getPositionData(Driver2Name,year,Race)
    Driver1 = getLaptimes(Driver1Name,year,Race)
    Driver2 = getLaptimes(Driver2Name,year,Race)
    Valid = True
    if not Driver1 or not Driver2:
        Valid = False
    D1Faster = 0
    D2Faster = 0
    i=1
    Delta = [0]
    if PositionDataD1 and PositionDataD2:
        if int(PositionDataD1[0]) == 0:
            driver1data["grid"] = 20
        else:
            driver1data["grid"] = int(PositionDataD1[0])
        driver1data["finish"] = int(PositionDataD1[1])
        driver1data["status"] = PositionDataD1[3]
        driver1data["validRace"] = Valid
        if PositionDataD1[2] == "R":
            driver1data["retired"] = True
        else:
            driver1data["retired"] = False
        driver2data["validRace"] = Valid
        if int(PositionDataD2[0]) == 0:
            driver2data["grid"] = 20
        else:
            driver2data["grid"] = int(PositionDataD2[0])
        driver2data["finish"] = int(PositionDataD2[1])
        driver2data["status"] = PositionDataD2[3]
        if PositionDataD2[2] == "R":
            driver2data["retired"] = True
        else:
            driver2data["retired"] = False
    else:
        return False
    if Driver1 and Driver2:
        stddv1 = stat.pstdev(Driver1)
        stddv2 = stat.pstdev(Driver2)
        mean2 = stat.mean(Driver2) 
        mean1 = stat.mean(Driver1)
        laplist = [0]               
        noCount = 1
        while i<min(len(Driver1),len(Driver2)):
            if (Driver1[i]< mean1+stddv1*.75 and Driver1[i] > mean1-stddv1*.75) and (Driver2[i]< mean2+stddv2*.75 and Driver2[i] > mean2-stddv2*.75):
                Delta.append(60*(Driver1[i]-Driver2[i])/min(Driver1[i],Driver2[i]))
            else:
                Delta.append(0)
                noCount = noCount+1
            laplist.append(0)
            i+=1
        if len(Driver1) < 2*noCount or len(Driver2)< 2* noCount:
            Valid = False
        D1DeltaBit = 0
        D2DeltaBit = 0
        StrongLapD1 = 0
        StrongLapD2 = 0
        for i in Delta:
            if i<0:
                D1Faster +=1
                D1DeltaBit+=i

            elif i<-1:
                StrongLapD1 +=1
            elif i>0:
                D2Faster +=1
                D2DeltaBit+=i
                if i>1:
                    StrongLapD2 +=1

        totalRTD1 = sum(Driver1)
        totalRTD2 = sum(Driver2)
        carry = 0
        count = 0
        for i in Delta:
            carry +=i
            count +=1
        Average = carry/count

        driver1data["sub1sec"] = D1Faster-StrongLapD1
        driver1data["greater1sec"] = StrongLapD1
        driver1data["totalfast"] = D1Faster
        driver1data["notapplicable"] = noCount
        driver1data["lapnumber"] = len(Driver1)
        driver1data["delta"] = D1DeltaBit
        driver1data["totaltime"] = totalRTD1
        driver1data["average"] = Average
        if not driver1data["retired"]:
            driver1data["raceMovement"] = driver1data["grid"] - driver1data["finish"]
        else:
            driver1data["raceMovement"] = 0

        driver2data["sub1sec"] = D2Faster-StrongLapD2
        driver2data["greater1sec"] = StrongLapD2
        driver2data["totalfast"] = D2Faster
        driver2data["notapplicable"] = noCount
        driver2data['lapnumber'] = len(Driver2)
        driver2data["delta"] = D2DeltaBit
        driver2data["totaltime"] = totalRTD2
        driver2data["average"] = Average
        if not driver1data["retired"]:
            driver2data["raceMovement"] = driver2data["grid"] - driver2data["finish"]
        else:
            driver2data["raceMovement"] = 0
    else:
        return False
    
    dateandtime = [Race,year]
    return driver1data,driver2data,dateandtime
    #Printing Data

    print(driver1data)
    print(driver2data)

def singleRaceOutput(year, race, Drivers,FullGrid):
    EventInfo = getRaceDate(year,race)
    if not FullGrid:
        if race == "1":
            print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"st event of the "+year, "calender.\n")
        elif race == '2':
            print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"nd event of the "+year, "calender.\n")
        else:
            print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"th event of the "+year, "calender.\n")
    D1Qual = getQualiData(Drivers[0],year,race)
    D2Qual = getQualiData(Drivers[1],year,race)
    if not D1Qual:
        D1Qual = [20,0,0]
    if not D2Qual:
        D2Qual = [20,0,0]
    driver1quali = str(D1Qual[0])
    driver2quali = str(D2Qual[0])
    if D1Qual[1] == D2Qual[1] and not D1Qual[2] == 0 and not D2Qual[2] == 0:
        qualDelt = D1Qual[2]-D2Qual[2]
    elif D1Qual[1] == D2Qual[1]:
        qualDelt = 0
    data = Racedata(Drivers[0],Drivers[1],year,race)
    if not data:
        print(Drivers[0],"Qualified in p"+driver1quali)
        print(Drivers[1],"Qualified in p"+driver2quali)
        if D1Qual[1] == 0:
            print(Drivers[0], "did not take part in qualifying","while",Drivers[1],"was eliminated in Q"+str(D2Qual[1]))
        elif D2Qual[1] == 0:
            print(Drivers[0], "was eliminated in Q"+ str(D1Qual[1]),"while",Drivers[1],"did not take part in Qualifying")
        elif D1Qual[1] == D2Qual[1] and qualDelt<0:
            print(Drivers[0],"set a Q"+ str(D1Qual[1]), "laptime that was", round(abs(qualDelt),3),"seconds faster than",Drivers[1])
        elif D1Qual[1] == D2Qual[1] and qualDelt>0:
            print(Drivers[1],"set a Q"+str(D2Qual[1]), "laptime that was", round(abs(qualDelt),3),"seconds faster than",Drivers[0])
        else:
            print(Drivers[0], "was eliminated in Q"+ str(D1Qual[1]),"while",Drivers[1],"was eliminated in Q"+str(D2Qual[1]))
        
        print("Not enough race laps to analyse")
        return
    driver1data = data[0]
    driver2data = data[1]
    driver1finish = str(driver1data["finish"])
    driver2finish = str(driver2data["finish"])
    if driver1data["grid"] == 0:
        driver1grid = 20
    else:
        driver1grid = driver1data["grid"] 
    if driver2data["grid"] == 0:
        driver2grid = 20
    else:
        driver2grid = driver2data["grid"] 
    
    if int(driver1quali) == driver1data["grid"]:
        if driver1data["status"] == "Finished" or "Lap" in driver1data["status"]:
            print(Drivers[0], "Qualified in P"+driver1quali,"and finished in P"+driver1finish)
        elif not driver1data["retired"]:
            print(Drivers[0], "Qualified in P"+driver1quali,"and was classified in P"+driver1finish,"but did not finish due to", driver1data["status"])
        else:
            print(Drivers[0], "Qualified in P"+driver1quali,"and retired from the race due to", driver1data["status"])
    else:
        if driver1data["status"] == "Finished" or "Lap" in driver1data["status"]:
            print(Drivers[0], "Qualified in P"+driver1quali+", Took a grid penalty of", str(driver1grid-int(driver1quali))+ " positions and finished in P"+driver1finish)
        elif not driver1data["retired"]:
            print(Drivers[0], "Qualified in P"+driver1quali+", Took a grid penalty of", str(driver1grid-int(driver1quali))+ " positions and was classified in P"+driver1finish,"but did not finish due to", driver1data["status"])
        else:
            print(Drivers[0], "Qualified in P"+driver1quali+", Took a grid penalty of", str(driver1grid-int(driver1quali))+ " positions and retired from the race due to", driver1data["status"])
    if int(driver2quali) == driver2data["grid"]:
        if driver2data["status"] == "Finished" or "Lap" in driver2data["status"]:
            print(Drivers[1], "Qualified in P"+driver2quali,"and finished in P"+driver2finish)
        elif not driver2data["retired"]:
            print(Drivers[1], "Qualified in P"+driver2quali,"and was classified in P"+driver2finish,"but did not finish due to", driver2data["status"])
        else:
            print(Drivers[1], "Qualified in P"+driver2quali,"and retired from the race due to", driver2data["status"])
    else:
        if driver2data["status"] == "Finished" or "Lap" in driver2data["status"]:
            print(Drivers[1], "Qualified in P"+driver2quali+", Took a grid penalty of", str(driver2grid- int(driver2quali))+ " positions and finished in P"+driver2finish)
        elif not driver2data["retired"]:
            print(Drivers[1], "Qualified in P"+driver2quali+", Took a grid penalty of", str(driver2grid-  int(driver2quali))+ " positions and was classified in P"+driver2finish,"but did not finish due to", driver2data["status"])
        else:
            print(Drivers[1], "Qualified in P"+driver2quali+", Took a grid penalty of", str(driver2grid-  int(driver2quali))+ " positions and retired from the race due to", driver2data["status"])
    if D1Qual[1] == 0:
        print(Drivers[0], "did not take part in qualifying","while",Drivers[1],"was eliminated in Q"+str(D2Qual[1]))
    elif D2Qual[1] == 0:
        print(Drivers[0], "was eliminated in Q"+ str(D1Qual[1]),"while",Drivers[1],"did not take part in Qualifying")
    elif D1Qual[1] == D2Qual[1] and qualDelt<0:
        print(Drivers[0],"set a Q"+str(D1Qual[1]), "laptime that was", round(abs(qualDelt),3),"seconds faster than",Drivers[1])
    elif D1Qual[1] == D2Qual[1] and qualDelt>0:
        print(Drivers[1],"set a Q"+str(D2Qual[1]), "laptime that was", round(abs(qualDelt),3),"seconds faster than",Drivers[0])
    else:
        print(Drivers[0], "was eliminated in Q"+ str(D1Qual[1]),"while",Drivers[1],"was eliminated in Q"+str(D2Qual[1]))
    if driver1data["validRace"]:
        if not FullGrid:
            print("Number of laps", Drivers[0],"was faster by less than 1 second =", (driver1data["sub1sec"]))
            print("Number of laps", Drivers[1],"was faster by less than 1 second =", (driver2data["sub1sec"]))
            print("Number of laps", Drivers[0],"was more than 1 second faster =",driver1data["greater1sec"])
            print("Number of laps", Drivers[1],"was more than 1 second faster =",driver2data["greater1sec"])
            print("Total number of laps",Drivers[0],"was faster =" ,driver1data["totalfast"])
            print("Total number of laps",Drivers[1],"was faster =",driver2data["totalfast"])
            print("Number of laps with no pace difference or laps which must be neglected =", driver1data["notapplicable"])
            print("Total number of laps =",min(driver1data["lapnumber"],driver2data["lapnumber"]))
        if driver1data["average"] <0:
            print(Drivers[0],"was faster by",round(abs(driver1data["average"]),2),"seconds per lap")
        elif driver1data["average"] >0:
            print(Drivers[1],"was faster by",round(abs(driver1data["average"]),2),"seconds per lap")
        if driver1data["delta"]+driver2data["delta"] <0:
            print(Drivers[0],"Was faster on pace by",round(abs(driver1data["delta"]+driver2data["delta"]),3), "seconds overall")
        elif driver1data["delta"]+driver2data["delta"] >0:
            print(Drivers[1],"Was faster on pace by",round(abs(driver1data["delta"]+driver2data["delta"]),3), "seconds overall")
        if not FullGrid:
            if ((driver1data["delta"]+driver2data["delta"])/min(driver1data["totaltime"],driver2data["totaltime"])*100) <0:
                print("Percent difference in total cumulative pure pace =", Drivers[1],"was",round(abs((driver1data["delta"]+driver2data["delta"])/min(driver1data["totaltime"],driver2data["totaltime"])*100),2),"percent slower")
            elif ((driver1data["delta"]+driver2data["delta"])/min(driver1data["totaltime"],driver2data["totaltime"])*100) <0:
                print("Percent difference in total cumulative pure pace =", Drivers[0],"was",round(abs((driver1data["delta"]+driver2data["delta"])/min(driver1data["totaltime"],driver2data["totaltime"])*100),2),"percent slower")
            if driver1data["totaltime"]-driver2data["totaltime"] <0:
                print(Drivers[0], "finished the race ",round(abs(driver1data["totaltime"]-driver2data["totaltime"]),3), "Seconds ahead of", Drivers[1])
            if driver1data["totaltime"]-driver2data["totaltime"] >0:
                print(Drivers[1], "finished the race ",round(abs(driver1data["totaltime"]-driver2data["totaltime"]),3), "Seconds ahead of", Drivers[0])
    else:
        print("No valid laptimes for comparison were set.")
    #Charting
    '''pyplot.figure(1)
    pyplot.plot(Driver1)
    pyplot.plot(Driver2)
    pyplot.figure(2)
    pyplot.plot(Delta)
    pyplot.plot(laplist)
    pyplot.show()'''
    if not FullGrid:
        print("\n\n")

def DriversList(year):
    DriverDict = {}
    DriverInput = requests.get("http://ergast.com/api/f1/"+year+"/driverStandings.json")
    unparsedDriver = DriverInput.text
    parsedDrivers = json.loads(unparsedDriver)
    for i in parsedDrivers["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
        if len(i["Constructors"]) == 1:
            if i["Constructors"][0]["constructorId"] in DriverDict:
                working = DriverDict[i["Constructors"][0]["constructorId"]]
                if isinstance(working,list):
                    working.append(i["Driver"]["driverId"])
                    updated = working
                else:
                    updated = [working, i["Driver"]["driverId"]]
                DriverDict[i["Constructors"][0]["constructorId"]] = updated
            else:
                DriverDict[i["Constructors"][0]["constructorId"]] = i["Driver"]["driverId"]
        elif len(i["Constructors"]) == 2:
            for j in i["Constructors"]:
                if j["constructorId"] in DriverDict:
                    working = DriverDict[j["constructorId"]]
                    if isinstance(working,list):
                        working.append(i["Driver"]["driverId"])
                        updated = working
                    else:
                        updated = [working, i["Driver"]["driverId"]]
                    DriverDict[j["constructorId"]] = updated
                else:
                    DriverDict[j["constructorId"]] = i["Driver"]["driverId"]

    return DriverDict

def OverallSeasonResults():
    year = input("Select the year: ")
    DriverSet = DriversList(year)
    for i in DriverSet:
        print("\n"+i)
        seasonComparison(True,DriverSet[i],year,1,False,False)
    print()

def TeammateComparison():
    teams = []
    driver1 = input("driver to compare: ")
    inputDriver = requests.get("http://ergast.com/api/f1/drivers/"+driver1+"/seasons.json")
    unparsedDriver = inputDriver.text
    parsedDrivers = json.loads(unparsedDriver)
    SeasonsRan = int(parsedDrivers["MRData"]["total"])
    print(driver1,"Has run in",SeasonsRan,"Seasons of F1")
    Nocount = False
    for i in parsedDrivers["MRData"]["SeasonTable"]["Seasons"]:
        if not Nocount:
            year = i['season']
            teams = []
            DriverSet = DriversList(year)
            for j in DriverSet:
                if (driver1 in DriverSet[j]):
                    teams.append(j)
            if len(teams) == 1:
                print("In",year+";", driver1,"drove for",teams[0],"\n")
                seasonComparison(True,DriverSet[teams[0]],year,1,False,True)
            elif len(teams) == 2:
                print ("In", year+";",driver1,"drove for",teams[0], "and", teams[1],"\n")
                inputs2 = requests.get("http://ergast.com/api/f1/"+year+".json")
                unparsed2 = inputs2.text
                parse2 = json.loads(unparsed2)
                racelength = 0
                for i in parse2["MRData"]['RaceTable']["Races"]:
                    if datetime.strptime(i["date"],'%Y-%m-%d')< datetime.now():
                        racelength +=1
                j = 0
                while j < racelength:
                    team = checkTeam(driver1,j+1,year)
                    if team == teams[0]:
                        if j+1 == 1:
                            firstTeam = 1
                            secondTeam = (j+1)
                            j = racelength
                            print("At", teams[0])
                            seasonComparison(True,DriverSet[teams[0]],year,firstTeam,secondTeam,True)
                            print("At", teams[1])
                            seasonComparison(True,DriverSet[teams[1]],year,secondTeam,False,True)
                        else:
                            firstTeam = j+1
                            secondTeam = (1)
                            print("At", teams[1])
                            seasonComparison(True,DriverSet[teams[1]],year,secondTeam,firstTeam,True)
                            print("At", teams[0])
                            seasonComparison(True,DriverSet[teams[0]],year,firstTeam,False,True)
                            j = racelength
                    j+=1
                
            print("\n\n")
        
    print("\n\n")

def seasonComparison(OverallSeason,drivers,year,startrace,endrace,teammatecompMove):        
    driver1 = drivers[0]
    driver2 = drivers[1]
    if endrace:
        raceLengthCap = endrace-1
    else:
        raceLengthCap = 10000000000000
    ThirdDriver = False
    count = 0
    if not teammatecompMove:
        if len(drivers) == 3:
            driver3 = drivers[2] 
            ThirdDriver = True
            Driverlist = DriversList(year)
            i = 0
            while i < len(drivers):
                count = 0
                for j in Driverlist:
                    if drivers[i] in Driverlist[j]:
                        count +=1
                if count == 1:
                    driver1 = drivers[i]
                    if checkTeam(drivers[(i+1)%3],1,year) == checkTeam(driver1,1,year):
                        driver2 = drivers[(i+1)%3]
                        driver3 = drivers[(i+2)%3]
                    else:
                        driver3 = drivers[(i+1)%3]
                        driver2 = drivers[(i+2)%3]

                i+=1
    """elif teammatecomp:
        if len(drivers) == 3:
            driver1 = teammatecomp
            if checkTeam(drivers[1],1,year) == checkTeam(driver1,1,year):
                driver2 = drivers[1]
                driver3 = drivers[2]
            else:
                driver3 = drivers[1]
                driver2 = drivers[2]"""
    

    drivers = [driver1,driver2]
    racelength = 0
    RaceOut1 = []
    RaceOut2 = []
    QualiOut1 = []
    QualiOut2 = []
    CumulativeAvgPerLap = []
    CumulativeOverallDelta = []
    bestDeltaD1 = 100000000
    bestDeltaD2 = -1000000
    bestDeltaRaceD2 = "n/a"
    Driver1FastRaces = 0
    Driver2FastRaces = 0
    ValidRaces =[]
    ValidQuali = []
    InvalidRaces = []
    InvalidQuali = []
    driver1Quali = []
    driver2Quali = []
    QualiPosDelta = []
    driver1Race = []
    driver2Race = []
    driver1RaceNODNF = []
    driver2RaceNODNF = []
    driver1RaceMove = []
    driver2RaceMove = []
    QualiDelta = []
    inputs2 = requests.get("http://ergast.com/api/f1/"+year+".json")
    unparsed2 = inputs2.text
    parse2 = json.loads(unparsed2)
    for i in parse2["MRData"]['RaceTable']["Races"]:
        if datetime.strptime(i["date"],'%Y-%m-%d')< datetime.now():
            racelength +=1
    racelength = min(racelength,raceLengthCap)
    i = startrace
    team = checkTeam(driver1,1,year)
    while i <= racelength: #Collects all the race data from every race
        if ThirdDriver:
            if checkTeam(driver3,str(i+1),year) == team:
                crossover = i+1
                racelength = i
        data = Racedata(driver1,driver2,year,str(i))
        QualiData1 = getQualiData(driver1,year,str(i))
        QualiData2 = getQualiData(driver2,year,str(i))
        if data:
            RaceOut1.append(data[0])
            RaceOut2.append(data[1])
        else:
            RaceOut1.append(i)
            RaceOut2.append(i)
        if QualiData1 and QualiData2:
            QualiOut1.append(QualiData1)
            QualiOut2.append(QualiData2)
        else:
            QualiOut1.append(i)
            QualiOut2.append(i)
        i +=1
    i = 0
    while i < (racelength-(startrace-1)):
        if not isinstance(RaceOut1[i],int):
            if (not RaceOut1[i]['lapnumber'] == RaceOut1[i]['notapplicable'] and not RaceOut2[i]['lapnumber'] == RaceOut2[i]['notapplicable'] and not RaceOut1[i]["lapnumber"] == 1 and not RaceOut2[i]["lapnumber"] == 1):
                Driver1data = RaceOut1[i]
                Driver2data = RaceOut2[i]
                CumulativeAvgPerLap.append(Driver1data["average"])
                CumulativeOverallDelta.append(Driver1data["delta"]+Driver2data["delta"])
                if Driver1data["delta"]+Driver2data["delta"] >0:
                    Driver2FastRaces +=1
                elif Driver1data["delta"]+Driver2data["delta"] <0:
                    Driver1FastRaces +=1
                if Driver1data["delta"]+Driver2data["delta"]< bestDeltaD1:
                    bestDeltaD1 = Driver1data["delta"]+Driver2data["delta"]
                    bestDeltaRaceD1 = startrace+i
                if Driver1data["delta"]+Driver2data["delta"]> bestDeltaD2:
                    bestDeltaD2 = Driver1data["delta"]+Driver2data["delta"]
                    bestDeltaRaceD2 = startrace+i
                driver1RaceMove.append(Driver1data["raceMovement"])
                driver2RaceMove.append(Driver2data["raceMovement"])
                ValidRaces.append(startrace+i)
            else:
                InvalidRaces.append(str(startrace+i))
            if RaceOut1[i]["finish"] > RaceOut2[i]["finish"]:
                driver2Race.append(RaceOut2[i]["finish"]-RaceOut1[i]["finish"])
            else:
                driver1Race.append(RaceOut2[i]["finish"]-RaceOut1[i]["finish"])
            if (RaceOut2[i]["status"] == "Finished" or RaceOut2[i]["status"] == "+1 Lap" or RaceOut2[i]["status"] == "+2 Laps") and (RaceOut1[i]["status"] == "Finished" or RaceOut1[i]["status"] == "+1 Lap" or RaceOut1[i]["status"] == "+2 Laps"):
                if RaceOut1[i]["finish"] > RaceOut2[i]["finish"]:
                    driver2RaceNODNF.append(RaceOut2[i]["finish"]-RaceOut1[i]["finish"])
                else:
                    driver1RaceNODNF.append(RaceOut2[i]["finish"]-RaceOut1[i]["finish"])
        else:
            InvalidRaces.append(str(startrace+i))
        if not isinstance(QualiOut1[i],int) and not isinstance(QualiOut2[i],int):
            if QualiOut1[i][1] == QualiOut2[i][1]:
                ValidQuali.append(startrace+i)
                if QualiOut1[i][2]>QualiOut2[i][2]:
                    driver2Quali.append(startrace+i)
                    if abs(QualiOut2[i][2]-QualiOut1[i][2]) <7:
                        QualiDelta.append(QualiOut2[i][2]-QualiOut1[i][2])
                    QualiPosDelta.append(QualiOut2[i][0]-QualiOut1[i][0])
                elif QualiOut1[i][2]<QualiOut2[i][2]:
                    driver1Quali.append(startrace+i)
                    if abs(QualiOut2[i][2]-QualiOut1[i][2]) <7:
                        QualiDelta.append(QualiOut2[i][2]-QualiOut1[i][2])
                    QualiPosDelta.append(QualiOut2[i][0]-QualiOut1[i][0])
            else:
                if QualiOut1[i][1] > QualiOut2[i][1]:
                    driver1Quali.append(startrace+i)
                    QualiPosDelta.append(QualiOut2[i][0]-QualiOut1[i][0])
                elif QualiOut1[i][1] < QualiOut2[i][1]:
                    driver2Quali.append(startrace+i)
                    QualiPosDelta.append(QualiOut2[i][0]-QualiOut1[i][0])
        else:
            InvalidQuali.append(i+1)
            print(InvalidQuali)
        i +=1
    averagePerLap = sum(CumulativeAvgPerLap)/len(CumulativeAvgPerLap)
    averageOverall = sum(CumulativeOverallDelta)/len(CumulativeOverallDelta)
    qualiBattle = [len(driver1Quali),len(driver2Quali)]
    averageQualiGap = (sum(QualiPosDelta)/len(QualiPosDelta))
    averageRaceGap = (sum(driver1RaceNODNF)+sum(driver2RaceNODNF))/(len(driver1RaceNODNF)+len(driver2RaceNODNF))
    raceBattle = [len(driver1Race),len(driver2Race)]
    raceBattleNODNF = [len(driver1RaceNODNF),len(driver2RaceNODNF)]
    AvgQualiDelta = sum(QualiDelta)/len(QualiDelta)
    driver1avgMove = sum(driver1RaceMove)/len(driver1RaceMove)
    driver2avgMove = sum(driver2RaceMove)/len(driver2RaceMove)
    if not OverallSeason:
        if sum(CumulativeOverallDelta) <0:
            print(drivers[0], "was faster by", round(abs(sum(CumulativeOverallDelta)),3), "seconds over all races")
        else:
            print(drivers[1],"was faster by", round(abs(sum(CumulativeOverallDelta)),3), "seconds over all races")
        if sum(CumulativeAvgPerLap) <0:
            print(drivers[0], "had a cumulative per lap delta of ", round(abs(sum(CumulativeAvgPerLap)),3), "seconds over all races")
        else:
            print(drivers[1],"had a cumulative per lap delta of", round(abs(sum(CumulativeAvgPerLap)),3), "seconds over all races")
    print("The quali Head to Head is:",driver1, str(qualiBattle[0])+"-"+str(qualiBattle[1]),driver2)
    if AvgQualiDelta>0:
        print(driver1,"was faster in qualifying by",round(abs(AvgQualiDelta),3),"seconds on average")
    else:
        print(driver2,"was faster in qualifying by",round(abs(AvgQualiDelta),3),"seconds on average")
    print()
    print("The Race Head to Head is:",driver1, str(raceBattle[0])+"-"+str(raceBattle[1]),driver2)
    print("The DNF controlled race Head to Head is:",driver1, str(raceBattleNODNF[0])+"-"+str(raceBattleNODNF[1]),driver2)
    print()
    if averageQualiGap <0:
        print("On average", driver2, "Qualified", round(abs(averageQualiGap),2), "positions in front of", driver1)
    else:
        print("On average", driver1, "Qualified", round(abs(averageQualiGap),2), "positions in front of", driver2)
    if averageRaceGap <0:
        print("On average", driver2, "Finished", round(abs(averageRaceGap),2), "positions in front of", driver1)
    else:
        print("On average", driver1, "Finished", round(abs(averageRaceGap),2), "positions in front of", driver2)
    print()
    print(driver1, "Improved from his grid position by", round(driver1avgMove,2), "positions on average")
    print(driver2, "Improved from his grid position by", round(driver2avgMove,2), "positions on average")
    print()
    if averageOverall <0:
        print("On average",drivers[0], "was faster by", round(abs(averageOverall),3), "seconds over a race")
    else:
        print("On average",drivers[1],"was faster by", round(abs(averageOverall),3), "seconds over a race")
    if averagePerLap <0:
        print("On average", drivers[0],"was faster by", round(abs(averagePerLap),3), "seconds over a lap")
    else:
        print("On average",drivers[1],"was faster by", round(abs(averagePerLap),3), "seconds over a lap")
    print()
    print(driver1, "was faster in", str(Driver1FastRaces)+"/"+str(racelength-(startrace-1)),"races")
    print(driver2, "was faster in", str(Driver2FastRaces)+"/"+str(racelength-(startrace-1)),"races")
    print("Races excluded for lack of data = ",len(InvalidRaces))
    print()
    if not OverallSeason:
        print(drivers[0],"best race was round", bestDeltaRaceD1,"with a pace delta of", round(-1*bestDeltaD1,3), "seconds over", drivers[1])
        print(drivers[1],"best race was round", bestDeltaRaceD2,"with a pace delta of", round(bestDeltaD2,3), "seconds over",drivers[0])
        racenumber = 0
        for i in CumulativeOverallDelta:
            if i<0:
                print("at round", str(ValidRaces[racenumber])+":",driver1, "was", round(abs(i),3), "faster than",driver2, "with a per lap gap of:",round(abs(CumulativeAvgPerLap[racenumber]),3))
            if i>0:
                print("at round", str(ValidRaces[racenumber])+":",driver2, "was", round(abs(i),3), "faster than",driver1,"with a per lap gap of:",round(abs(CumulativeAvgPerLap[racenumber]),3) )
            racenumber+=1
        if InvalidRaces:
            DiscountedRaces = ", ".join(InvalidRaces)
            print("round(s):", DiscountedRaces ,"were neglected due to lack of data")
    if ThirdDriver:
        print("\nat round", str(crossover)+",", driver3, "was given the seat from", driver2)
        print()
        seasonComparison(OverallSeason,[driver1,driver3],year,crossover,False,False)
    else:
        print("\n\n")

def raceComparison(latestRace):
    if latestRace:
        year = str(datetime.now().year)
        inputs2 = requests.get("http://ergast.com/api/f1/"+year+".json")
        unparsed2 = inputs2.text
        parse2 = json.loads(unparsed2)
        for i in parse2["MRData"]['RaceTable']["Races"]:
            if datetime.strptime(i["date"],'%Y-%m-%d')< datetime.now():
                race = i['round']
    else:
        year = input("Select the year: ")
        race = input("Select the round: ")
    DriverSet = DriversList(year)
    EventInfo = getRaceDate(year,race)
    if race == "1":
        print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"st event of the "+year, "calender.")
    elif race == '2':
        print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"nd event of the "+year, "calender.")
    else:
        print("The", EventInfo[0]+",","Located at",EventInfo[1],"which took place on",EventInfo[2]+".","This was the",race+"th event of the "+year, "calender.")
    for i in DriverSet:
        print("\n"+i)
        singleRaceOutput(year,race,DriverSet[i],True)
    print("\n\n")

def main():
    print("*****F1 Comparison calculator*****")
    firstChoice = int(input("press 1 for single race comparison, press 2 for season long comparison, press 3 for driver career comparison, press 4 to quit \n"))
    if firstChoice == 1:
        secondChoice = int(input("Press 1 for teammate comparison, press 2 for non teammate driver comparison, press 3 for full grid race analysis: \n"))
        if secondChoice == 1:
            year = input("Select the year: ")
            Teams = DriversList(year)
            print("Select team from list: ",", ".join(Teams))
            ChosenTeam = input("Select team: ")
            Drivers = Teams[ChosenTeam]
            singleRaceOutput(year,input("Select the race (round number): "),Drivers,False)
        elif secondChoice == 2:
            Drivers = [input("First driver: "),input("Second driver: ")]
            singleRaceOutput(input("Select the year: "),input("Select the race (round number): "),Drivers,False)
        elif secondChoice ==3:
            ThirdChoice = int(input("For latest race press 1, otherwise press 2: "))
            if ThirdChoice == 1:
                raceComparison(True)
            elif ThirdChoice == 2:
                raceComparison(False)
    elif firstChoice == 2:
        secondChoice = int(input("Press 1 for teammate comparison, press 2 for non teammate driver comparison, press 3 for season overview: \n"))
        if secondChoice == 1:
            year = input("Select the year: ")
            Teams = DriversList(year)
            print("Select team from list: ",", ".join(Teams))
            ChosenTeam = input("Select team: ")
            Drivers = Teams[ChosenTeam]
            print(Drivers)
            seasonComparison(False,Drivers,year,1,False,False)
        elif secondChoice == 3:
            OverallSeasonResults()
        elif secondChoice == 2:
            year = input("Select the year: ")
            driver1 = input("First driver: ")
            driver2 = input("Second driver: ")
            drivers  =[driver1,driver2]
            print()
            seasonComparison(False,drivers,year,1,False,False)
    elif firstChoice == 4:
        return
    elif firstChoice == 3:
        TeammateComparison()
    main()

main()

