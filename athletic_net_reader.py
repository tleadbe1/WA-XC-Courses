import numpy as np
import csv
import os
import pandas as pd

def parse_time(t):
    s = t.split(":")
    if len(s) == 2:
        return 60*int(s[0]) + float(s[1])
    elif len(s) == 3:
        return 3600*int(s[0]) + int(s[1])*60 + float(s[2])
    else:
        return -1

def is_race_name(s):
    if not "\t" in s and not "Sweepstakes" in s:
        if "Meter" in s or "Mile" in s:
            return True
    return False

def is_random_line(s):
    if not "\t" in s:
        if not "Official Team Scores" in s:
            if not len(s.strip()) == 0:
                if not s[0] == "Q":
                    return True
    return False

def is_end_of_results(s):
    if "RUNNERSPACE" in s:
        return True
    return False


class Race_Result():
    """
    This Race Result class provides a standardized container for saving, loading, and processing race data saved on athletic.net. 
    It is designed to read a plain text file of the "All Results" athletic.net page for a given meet. Initial processing of race 
    data shoud be done through the supporting get_race_results() function. Previously saved race results can be loaded via the 
    Race_Result.load() method. Generally, the Race_Results.get_data() method is not intended to be run on its own. 

    Attributes

    file_name - string - name of the text file where the data was compiled from.
    meet_name - string - official name of the meet
    meet_location - string - official location of the meet
    race_name - official name of the race
    names - list of strings - names of participants
    times - list of floats - finishing times of participants in seconds
    schools - list of strings - school names for each participant
    grades - list of ints - grade of each participant
    qualified - list of bool - indicates if participant qualified for the next meet from this race
    teams - list of string - list of school team names officially competeing in the race
    team_scores - list of ints - scores for each competeing team
    varsity - bool - is the meet a varsity meet
    boys - bool - True indicates a boys race, False indicates a girls race
    distance - float - length of race in meters
    year - int - year this race took place

    Methods

    Race_Result.get_data(data,meet_name,year,meet_locations,race_name,boys,fname)

        data - list of str - lines of text from the athletic.net "all results" page. First line should be the race name and the last line should be 
                                the last entry of the race (usually followed by another race name).
        meet_name - str - Official name of the meet
        meet_location - str - Official location of the meet
        race_name - str - Official name of the race
        boys - bool - True indicates a boys race, False indicates a girls race
        fname - str - path and file name of where the original athletic.net page is stored as text

        Return - self - Race_Result object - Given Race_Result object containing all the information about the race 

    Race_Result.save()
        
        Saves the Race_Result as a zipped numpy object (.npz) with entries:

            ind_header - list of str - header for the individual result data
            team_header - list of str - header for the team result data
            meet_header - list of str - header for the meet data
            ind_data - numpy 2d array of mixed data - data for the individual results
            team_data - numpy 2d array of mixed data - data for the team results
            meet_data - numpy list of mixed data - meet information

        Data is saved as self.meet_name + "_" + self.race_name + "_" + str(self.year) + ".npz"
        
        Return - None

    Race_Result.load(meet_name,race_name,year)

        Loads race data into this Race_Result object using:

        meet_name - str - Official meet name
        race_name - str - Official race name
        year - int - year of the race

        Return - None
    
    """
    def __init__(self,):
        return 
    
    def get_data(self,data,meet_name,year,meet_location,race_name,boys,fname):
        """
        data - list of str - lines of text from the athletic.net "all results" page. First line should be the race name and the last line should be 
                                the last entry of the race (usually followed by another race name).
        meet_name - str - Official name of the meet
        meet_location - str - Official location of the meet
        race_name - str - Official name of the race
        boys - bool - True indicates a boys race, False indicates a girls race
        fname - str - path and file name of where the original athletic.net page is stored as text

        Return - self - Race_Result object - Given Race_Result object containing all the information about the race 
        """
        self.names = []
        self.times = []
        self.schools = []
        self.qualified = []
        self.grades = []
        self.varsity = False
        self.boys = boys
        self.distance = 0.
        self.file_name = fname
        self.race_name = race_name
        self.meet_name = meet_name
        self.meet_location = meet_location
        self.teams = []
        self.team_scores = []
        self.year = year
        dist = race_name.split()[0]
        if "," in dist:
            self.distance = 1000*int(dist.split(",")[0])
        else:
            self.distance = 1609.344*int(dist)
        if "varsity" in race_name.lower() or "elite" in race_name.lower():
            self.varsity = True
        if "Official Team Scores" in data[1]:
            j = 2
            while len(data[j].split("\t")) < 5:
                self.teams.append(data[j].split("\t")[1])
                self.team_scores.append(int(data[j].split("\t")[2]))
                j += 1
        else:
            j = 1
        while j < len(data):
            s_line = data[j].split("\t")
            self.names.append(s_line[2])
            self.grades.append(s_line[3])
            self.times.append(parse_time(s_line[4]))
            self.schools.append(s_line[6])
            if j < len(data) - 1:
                Q = data[j+1][0]
                if Q == "Q":
                    self.qualified.append(True)
                    j += 2
                else:
                    self.qualified.append(False)
            else:
                self.qualified.append(False)
            j += 1    
        self.names = np.array(self.names)
        self.times = np.array(self.times)
        self.schools = np.array(self.schools)
        self.qualified = np.array(self.qualified)
        self.grades = np.array(self.grades)
        self.teams = np.array(self.teams)
        self.team_scores = np.array(self.team_scores)
        return self

    def save(self):
        """
        Saves the Race_Result as a zipped numpy object (.npz) with entries:

            ind_header - list of str - header for the individual result data
            team_header - list of str - header for the team result data
            meet_header - list of str - header for the meet data
            ind_data - numpy 2d array of mixed data - data for the individual results
            team_data - numpy 2d array of mixed data - data for the team results
            meet_data - numpy list of mixed data - meet information

        Data is saved as self.meet_name + "_" + self.race_name + "_" + str(self.year) + ".npz"

        Return - None
        """
        ind_data = np.stack((self.names,self.times,self.schools,self.grades,self.qualified),axis = 1)
        team_data = np.stack((self.teams,self.team_scores),axis = 1)
        meet_data = np.array([self.file_name,self.meet_name,self.race_name,
                             self.meet_location,str(self.year),str(self.distance),
                              str(self.boys),str(self.varsity)])
        ind_header = np.array(["Name","Time","School","Grade","Qualified"])
        team_header = np.array(["Team","score"])
        meet_header = np.array(["File Name","Meet Name","Race Name",
                                "Meet Location","Year","Distance",
                                "Is Boys","Is Varsity"])
        fname = self.meet_name + "_" + self.race_name + "_" + str(self.year) 
        np.savez(fname.replace("/","")+ ".npz",ind_data = ind_data,team_data = team_data,meet_data = meet_data,
                                                                ind_header = ind_header,team_header = team_header,meet_header = meet_header)
        return 

    def save_csv(self):
        """
        Saves the Race_Result as multiple csv files:

            ind_data - numpy 2d array of mixed data - data for the individual results
            team_data - numpy 2d array of mixed data - data for the team results
            meet_data - numpy list of mixed data - meet information

        Data is saved as self.meet_name + "_" + self.race_name + "_" + str(self.year) + "_" + "*_data".csv"
            where * is either ind, team, or meet. 

        Note that currently one can only load data from npz files and not csv files.

        Return - None
        """
        ind_data = np.stack((self.names,self.times,self.schools,self.grades,self.qualified),axis = 1)
        team_data = np.stack((self.teams,self.team_scores),axis = 1)
        meet_data = np.array([self.file_name,self.meet_name,self.race_name,
                             self.meet_location,str(self.year),str(self.distance),
                              str(self.boys),str(self.varsity)])
        ind_header = np.array(["Name","Time","School","Grade","Qualified"])
        team_header = np.array(["Team","score"])
        meet_header = np.array(["File Name","Meet Name","Race Name",
                                "Meet Location","Year","Distance",
                                "Is Boys","Is Varsity"])
        fname = self.meet_name + "_" + self.race_name + "_" + str(self.year) 
        pre = ["ind","team","meet"]
        data = [ind_data,team_data,meet_data]
        header = [ind_header,team_header,meet_header]
        for p,d,h in zip(pre,data,header):
            with open(fname.replace("/","") + "_" + p + "_data.csv",mode = "w") as wfile:
                writer = csv.writer(wfile)
                writer.writerow(h)
                for line in d:
                    writer.writerow(line)
        return 

    def save_to_db(self): # TAG1
        """
        Saves the race data to base csv files for storage and SQL querying.
        """

        if os.path.isfile("schools.csv"):
            schools = pd.read_csv("schools.csv",dtype = {"school_id":np.int32,"name":str,"classification":str,"district":np.int32,"avg_enrollment":np.float32})
        else:
            print("No information on schools found. Quitting.")
            return
        
        if os.path.isfile("athletes.csv"):
            athletes = pd.read_csv("athletes.csv",dtype = {"athlete_id":np.int32,"first_name":str,"last_name":str,"school_id":np.int32,"grade":np.int32})

        else:
            athletes = pd.DataFrame(columns = ["athlete_id","first_name","last_name","school_id","grade"])
        
        if os.path.isfile("courses.csv"):
            courses = pd.read_csv("courses.csv",dtype = {"course_id":np.int32,"name":str})
        else:
            courses = pd.DataFrame(columns = ["course_id","name"])
        
        if os.path.isfile("meets.csv"):
            meets = pd.read_csv("meets.csv",dtype = {"meet_id":np.int32,"course_id":np.int32,"name":str})
        else:
            meets = pd.DataFrame(columns = ["meet_id","course_id","name"])

        if os.path.isfile("races.csv"):
            races = pd.read_csv("races.csv",dtype = {"race_id":np.int32,"meet_id":np.int32,"name":str,"distance_km":np.float32,"is_varsity":bool})
        else:
            races = pd.DataFrame(columns = ["race_id","meet_id","name","distance_km","is_varsity"])
        
        if os.path.isfile("race_results.csv"):
            race_results = pd.read_csv("race_results.csv",dtype = {"race_id":np.int32,"athlete_id":np.int32,"time_sec":np.float32,"qualified":bool})
        else:
            race_results = pd.DataFrame(columns = ["race_id","athlete_id","time_sec","qualified"])
        
        
        # Check if course has been added yet
        if (courses["name"] == self.meet_location).any(): 
            course_id = int(courses["course_id"][courses["name"] == self.meet_location].iloc[0])
        else:
            if len(courses["course_id"]) == 0:
                course_id = 1
            else:
                course_id = np.max(courses["course_id"]) + 1
            new_row = pd.DataFrame({"course_id":[course_id,],"name":[self.meet_location,]})
            courses = pd.concat([courses,new_row],ignore_index = True)

        # Check if meet has been added yet
        
        if (meets["name"] == self.meet_name).any(): 
            meet_id = int(meets["meet_id"][meets["name"] == self.meet_name].iloc[0])
        else:
            if len(meets["meet_id"]) == 0:
                meet_id = 1
            else:
                meet_id = np.max(meets["meet_id"]) + 1
            new_row = pd.DataFrame({"meet_id":[meet_id,],"course_id":[course_id,],"name":[self.meet_name,]})
            meets = pd.concat([meets,new_row],ignore_index = True)

        # Will always be a new race so just get new index

        if len(races["race_id"]) == 0:
            race_id = 1
        else:
            race_id = np.max(races["race_id"]) + 1

        new_row = pd.DataFrame({"race_id":[race_id,],"meet_id":[meet_id,],"name":[self.race_name,],"distance_km":[self.distance/1000,],"is_varsity":[self.varsity,]})
        races = pd.concat([races,new_row],ignore_index = True)
    
        # TAG2
        for name,time,school,grade,q in zip(self.names,self.times,self.schools,self.grades,self.qualified):
            if not (schools["name"].str.contains(school,regex = False)).any():
                continue
            school_id = int(schools[schools["name"].str.contains(school,regex = False)]["school_id"].iloc[0])

            first_name = name.split(" ")[0]   
            last_name = name[len(first_name)+1:]
            if ((athletes["first_name"] == first_name)*(athletes["last_name"] == last_name)*(athletes["school_id"] == school_id)).any():
                athlete_id = int(athletes["athlete_id"][((athletes["first_name"] == first_name)*(athletes["last_name"] == last_name)*(athletes["school_id"] == school_id))].iloc[0])
            else:
                if len(athletes["athlete_id"]) == 0:
                    athlete_id = 1
                else:
                    athlete_id = np.max(athletes["athlete_id"]) + 1
                try:
                    _ = int(grade)
                except:
                    grade = 0
                new_row = pd.DataFrame({"athlete_id":[athlete_id,],"first_name":[first_name,],"last_name":[last_name,],"school_id":[school_id,],"grade":[grade,]})
                athletes = pd.concat([athletes,new_row],ignore_index = True)

            new_row = pd.DataFrame({"race_id":[race_id,],"athlete_id":[athlete_id,],"time_sec":[time,],"qualified":[q,]})
            race_results = pd.concat([race_results,new_row],ignore_index = True)

        courses.to_csv("courses.csv",index = False)
        meets.to_csv("meets.csv",index = False)
        races.to_csv("races.csv",index=  False)
        race_results.to_csv("race_results.csv",index = False)
        athletes.to_csv("athletes.csv",index = False)
        return         


    def load(self,meet_name,race_name,year):
        """
        Loads race data into this Race_Result object using:

        meet_name - str - Official meet name
        race_name - str - Official race name
        year - int - year of the race

        Return - None
        """
        fname = meet_name + "_" + race_name + "_" + str(year)
        data = np.load(fname.replace("/","") + ".npz",allow_pickle = True)
        ind_data = data["ind_data"]
        team_data = data["team_data"]
        meet_data = data["meet_data"]
        self.names = ind_data[:,0]
        self.times = ind_data[:,1]
        self.schools = ind_data[:,2]
        self.qualified = ind_data[:,4]
        self.grades = ind_data[:,3]
        self.varisty = bool(meet_data[-1])
        self.boys = bool(meet_data[-2])
        self.distance = float(meet_data[-3])
        self.year = int(meet_data[-4])
        self.file_name = meet_data[0]
        self.race_name = meet_data[2]
        self.meet_name = meet_data[1]
        self.meet_location = meet_data[3]
        self.teams = team_data[:,0]
        self.team_scores = team_data[:,1]
        return 
            

def get_race_results(fname):
    """
    Read an athletic.net "all results" page of race results and return a list of Race_Result objects with all of the information.

    fname - str - path and name of the file containing the text of the athletic.net "all results" page. 

    Return - list of Race_Result objects - All the results from the input file.
    """
    with open(fname, mode = "r") as rfile:
        lines = rfile.read().split("\n")
    i = 0
    boys = True
    start_ind = -1
    race_results = []
    while i < len(lines):
        line = lines[i].strip()
        if "Followers" in line:
            meet_name = lines[i+1].strip()
            year = int(lines[i+3].strip()[-4:])
            meet_location = lines[i+4].strip()
            i += 5 
            continue
        if "boy" in line.lower() or "men" in line.lower():
            boys = True
        if "girl" in line.lower() or "women" in line.lower():
            boys = False
        if is_race_name(line):
            if start_ind > 0:
                res = Race_Result()
                race_results.append(res.get_data(lines[start_ind:i],meet_name,year,meet_location,lines[start_ind].strip(),boys,fname))
            start_ind = i
        elif is_random_line(line):
            if start_ind > 0:
                res = Race_Result()
                race_results.append(res.get_data(lines[start_ind:i],meet_name,year,meet_location,lines[start_ind].strip(),boys,fname))
            start_ind = -1
        if is_end_of_results(line):
            if start_ind > 0:
                res = Race_Result()
                race_results.append(res.get_data(lines[start_ind:i],meet_name,year,meet_location,lines[start_ind].strip(),boys,fname))
            break
        i += 1 
    return race_results



