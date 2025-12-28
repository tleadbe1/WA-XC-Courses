import numpy as np
import csv

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
    def __init__(self,):
        return 
    
    def get_data(self,data,meet_name,year,meet_location,race_name,boys,fname):
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

    def load(self,meet_name,race_name,year):
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

out = get_race_results("../StatePredictions/WescoConf2025.txt")
for o in out:
    o.save()

