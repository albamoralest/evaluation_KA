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
import csv, shutil, time
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
            # returns a dataframe object
            return dfConcepts
        except Exception as e:
            print("EX: " + str(e))

    def getOneCondition(self, snmdId, fileName):
        # read doc
        dfConcepts = self.readCSVFile(fileName)
        dfConcepts['snomedIdentifier'] = dfConcepts['snomedIdentifier'].map(str)
        querySentence = "snomedIdentifier=='{}'".format(snmdId)
        # print(querySentence)
        annotationRows = dfConcepts.query(querySentence)
        annotationRows.sort_values(by=['confidence'], inplace=True, ascending=[False])
        return annotationRows

    def getConceptsAnnotations(self, snmdId, fileName):
        # read doc
        dfConcepts = self.readCSVFile(fileName)
        dfConcepts['snomedIdentifier'] = dfConcepts['snomedIdentifier'].map(str)
        # order by id
        dfConcepts.sort_values(by=['snomedIdentifier'], inplace=True, ascending=[True])
        # delete duplicates
        dfNew = dfConcepts.drop_duplicates(subset=['snomedIdentifier'], keep="first", inplace=False,ignore_index=True)

        # if id == -1 then obtain the first id in the list
        if snmdId == -1:
            selectedId = dfNew.iloc[0]['snomedIdentifier']
            # print(selectedId)
        else:
            # if id = XXX concept id, then obtain the next id in the list
            # index_list = dfNew.index[dfNew['snomedIdentifier']==snmdId].tolist()
            index_list = dfNew[dfNew['snomedIdentifier'] == snmdId].index[0]
            print(index_list)
            selectedId = dfNew['snomedIdentifier'].iloc[index_list+1]

        querySentence = "snomedIdentifier=='{}'".format(selectedId)
        annotationsList = dfConcepts.query(querySentence)
        # order by confidence
        annotationsList.sort_values(by=['confidence'], inplace=True, ascending=[False])
        # print(len(annotationsList))
        annotationsList['index'] = list(range(len(annotationsList)))

        return annotationsList

    def createCSVresultsFilesP1(self,userID):
        # 1. File one: Answers to all the CES annotations
        fileNameOne = str(userID)+"partOneAnswersA"
        fieldNamePartOne = ['snomedConcept', 'snomedIdentifier', 'conditionName', 'predictedTag', 'confidence',
                            'sentence', 'source', 'support CNL1L2L3', 'support L1L2L3', 'L1', 'L2', 'L3']
        with open(self.resultsDirectory + fileNameOne + '.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartOne)
            writer.writeheader()

        # 2. File two: If given the new CES
        fileNAmeTwo = str(userID)+"partOneAnswersB"
        fieldNamePartTwo = ['username', 'snmdIdentifier', 'newCES']

        with open(self.resultsDirectory+fileNAmeTwo+'.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartTwo)
            writer.writeheader()

    def appendListToCSV(self, userID, fileName, newRow):
        # open file in append mode
        with open(self.resultsDirectory+userID+fileName+'.csv', '+a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(newRow)
            # writer = csv.DictWriter(csv_file, newline=dfObject)
            # writer.writerow(newRow)

    def appendDataFrameToCSV(self, userID, fileName, newDataFrame):
        newDataFrame.to_csv(self.resultsDirectory+str(userID)+fileName+'.csv',mode='a',index=False, header=False)

