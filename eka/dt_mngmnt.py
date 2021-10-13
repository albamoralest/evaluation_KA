'''
Created on 29 Sep 2021

@author: acmt2
'''

import os
import os.path
import json
import pandas as pd

# import random
from fileinput import filename
# import csv, shutil, time
from csv import writer
class DtMngmnt():
    resultsDirectory = 0
    resourcesDirectory = 0
    '''
    classdocs
    '''


    def __repr__(self):
        # self.totalResult = self.getTotalExamples()
        return '<Results {}>'.format(self.body)
    
    def setDirectory(self, sample):
        self.resultsDirectory = os.getcwd()+ '/eka/users/'
        self.resourcesDirectory = os.getcwd()+'/eka/resources/'
        
    def verifyUser(self, username):
        usersList = [f for f in os.listdir(self.resultsDirectory) if not f.startswith('.')] 
        username = username + ".json"
        file =False
        for user in usersList:
            if user == username:
                file = True
                pass
        
        return file
    
    def generateUserID(self, flag, username):
        idcode = 1
        
        if flag:
            #the username already has an IDCODE
            userfile = self.loadUserFile(username)
            idcode = userfile[id]
        else:
            usersList = [f for f in os.listdir(self.resultsDirectory) if not f.startswith('.')] 
            usersCount = len(usersList)
        
            if usersCount > 0:
                idcode = usersCount+1
            
        return idcode
    
    def createUserFile(self, username):
        userid = self.generateUserID(False, username)
        content = {}
        content['id'] = userid
        content['username'] = username
        content['p1'] = {}
        content['p1']['total'] = 0
        content['p1']['current'] = 0
        content['p2'] = {}
        content['p2']['total'] = 0
        content['p2']['current'] = 0
        with open(self.resultsDirectory+username +".json", 'w') as outfile:
            json.dump(content,outfile)

    def updateUserFile(self, username, content):
        with open(self.resultsDirectory+username +".json", 'w') as outfile:
            json.dump(content,outfile)

    def loadUserFile (self, fileName):
        obj = None
        if os.path.isfile(self.resultsDirectory+fileName + ".json"):
            with open(self.resultsDirectory+fileName + ".json") as json_file:
                obj = json.load(json_file)
        return obj

    def verifyAdmin(self, userFile):
        try:
            if userFile['admin'] == 'YES':
                return True
            else:
                return False
        except:
            return False

    def getNumberConcepts(self, fileName):
        return self.readCSVFile(fileName).snomedIdentifier.value_counts()

    def readCSVFile(self, fileName):
        localPath = self.resourcesDirectory + fileName
        try:
            # with open(localPath, newline='') as f:
            #     reader = csv.reader(f)
            #     samplelist = list(reader)
            dfConcepts = pd.read_csv(localPath)
            return dfConcepts
        except Exception as e:
            print("EX: " + str(e))

    def getConceptsAnnotations(self, snmdId, fileName):
        # read doc
        dfConcepts = self.readCSVFile(fileName)
        dfConcepts['snomedIdentifier'] = dfConcepts['snomedIdentifier'].map(str)
        # order by id
        dfConcepts.sort_values(by=['snomedIdentifier'], inplace=True, ascending=[True])
        # delete duplicates
        dfNew = dfConcepts.drop_duplicates(subset=['snomedIdentifier'], keep="first", inplace=False)

        # if id == -1 then obtain the first id in the list
        if snmdId == -1:
            selectedId = dfNew.iloc[0]['snomedIdentifier']
            # print(selectedId)
        else:
        # if id = XXX concept id, then obtain the next id in the list
            index_list = dfNew.index[dfNew['snomedIdentifier']==snmdId].tolist()
            selectedId = dfNew.iloc[index_list[0]]['snomedIdentifier']

        querySentence = "snomedIdentifier=='{}'".format(selectedId)
        # print(querySentence)
        annotationsList = dfConcepts.query(querySentence)
        # print(len(annotationsList))

        return annotationsList

