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
    propagationDirectory = 0
    listFiles = ['rule0.csv', 'rule1.csv', 'rule2.csv', 'rule3.csv', 'rule4.csv', 'rule5.csv', 'rule6.csv', 'rule7.csv']
    '''
    classdocs
    '''

    def __repr__(self):
        # self.totalResult = self.getTotalExamples()
        return '<Results {}>'.format(self.body)
    
    def set_directory(self, sample):
        self.resultsDirectory = os.getcwd() + '/eka/users/'
        # Resources for part 1
        self.resourcesDirectory = os.getcwd()+'/eka/resources/'
        # Resources for part 2, propagation
        self.propagationDirectory = os.getcwd()+'/eka/propagation/'
        
    def verify_user(self, username):
        usersList = [f for f in os.listdir(self.resultsDirectory) if not f.startswith('.')] 
        username = username + ".json"
        file =False
        for user in usersList:
            if user == username:
                file = True
                pass
        
        return file
    
    def generate_user_id(self, flag, username):
        idcode = 1
        
        if flag:
            #the username already has an IDCODE
            userfile = self.load_user_file(username)
            idcode = userfile[id]
        else:
            usersList = [f for f in os.listdir(self.resultsDirectory) if not f.startswith('.')] 
            usersCount = len(usersList)
        
            if usersCount > 0:
                idcode = usersCount+1
            
        return idcode
    
    def create_user_file(self, username):
        userid = self.generate_user_id(False, username)
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

    def update_user_file(self, username, content):
        with open(self.resultsDirectory+username +".json", 'w') as outfile:
            json.dump(content,outfile)

    def load_user_file (self, fileName):
        obj = None
        if os.path.isfile(self.resultsDirectory+fileName + ".json"):
            with open(self.resultsDirectory+fileName + ".json") as json_file:
                obj = json.load(json_file)
        return obj

    def verify_admin(self, userFile):
        try:
            if userFile['admin'] == 'YES':
                return True
            else:
                return False
        except:
            return False

    def get_number_concepts(self, fileName):
        return self.read_csv_file(fileName).snomedIdentifier.value_counts()

    def read_csv_file(self, fileName):
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

    def get_one_condition(self, snmdId, fileName):
        # read doc
        dfConcepts = self.read_csv_file(fileName)
        dfConcepts['snomedIdentifier'] = dfConcepts['snomedIdentifier'].map(str)
        querySentence = 'snomedIdentifier=="{}"'.format(snmdId)
        # print(querySentence)
        annotationRows = dfConcepts.query(querySentence)
        annotationRows.sort_values(by=['confidence'], inplace=True, ascending=[False])
        return annotationRows

    def get_concepts_annotations(self, snmdId, fileName):
        # read doc
        df_concepts = self.read_csv_file(fileName)
        df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
        # order by id
        df_concepts.sort_values(by=['snomedIdentifier'], inplace=True, ascending=[True])
        # delete duplicates
        df_new = df_concepts.drop_duplicates(subset=['snomedIdentifier'], keep="first", inplace=False,ignore_index=True)

        # if id == -1 then obtain the first id in the list
        if snmdId == -1:
            selected_id = df_new.iloc[0]['snomedIdentifier']
            condition_name = df_new.iloc[0]['conditionName']
            # print(selectedId)
        else:
            # if id = XXX concept id, then obtain the next id in the list
            # index_list = dfNew.index[dfNew['snomedIdentifier']==snmdId].tolist()
            index_list = df_new[df_new['snomedIdentifier'] == snmdId].index[0]
            print(index_list)
            selected_id = df_new['snomedIdentifier'].iloc[index_list+1]
            condition_name = df_new['conditionName'].iloc[index_list + 1]

        querySentence = 'snomedIdentifier=="{}"'.format(selected_id)
        annotationsList = df_concepts.query(querySentence)
        # order by confidence
        annotationsList.sort_values(by=['confidence'], inplace=True, ascending=[False])
        # print(len(annotationsList))
        # add a new index
        annotationsList['index'] = list(range(len(annotationsList)))
        print(condition_name)
        return annotationsList, condition_name

    def create_csv_results_files_p1(self,userID):
        # 1. File one: Answers to all the CES annotations
        fileNameOne = str(userID)+"partOneAnswersA"
        fieldNamePartOne = ['snomedConcept', 'snomedIdentifier', 'conditionName', 'predictedTag', 'confidence',
                            'sentence', 'source', 'support CNL1L2L3', 'support L1L2L3', 'L1', 'L2', 'L3', 'evaluationAnswers']
        with open(self.resultsDirectory + fileNameOne + '.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartOne)
            writer.writeheader()

        # 2. File two: If given the new CES
        fileNAmeTwo = str(userID)+"partOneAnswersB"
        fieldNamePartTwo = ['username', 'snomedIdentifier', 'snomedConcept', 'CES']

        with open(self.resultsDirectory+fileNAmeTwo+'.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartTwo)
            writer.writeheader()

    def append_list_to_csv(self, userID, fileName, newRow):
        # open file in append mode
        with open(self.resultsDirectory+userID+fileName+'.csv', '+a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(newRow)
            # writer = csv.DictWriter(csv_file, newline=dfObject)
            # writer.writerow(newRow)

    def append_data_frame_to_csv(self, userID, fileName, newDataFrame):
        newDataFrame.to_csv(self.resultsDirectory+str(userID)+fileName+'.csv',mode='a',index=False, header=False)

    def get_sources_links(self, conditionName, fileName):
        dfConcepts = self.read_csv_file(fileName)

        querySentence = 'conditionName=="{}"'.format(conditionName)
        sourcesList_df = dfConcepts.query(querySentence)
        sourcesList_df['type'] = sourcesList_df['type'].str.replace('.json', '')

        return sourcesList_df

    def read_csv_file_directory(self, fileName, typeDirectory):
        if typeDirectory == 'propagation':
            localPath = self.propagationDirectory + fileName
        else:
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

    def get_propagated_concepts(self, snmd_id, file_name, rule):
        # read doc
        query = ""
        df_results = pd.DataFrame()
        df_concepts = pd.read_csv(self.propagationDirectory + file_name)
        if rule == 1:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['snomedDesIdentifier', 'snomedDesConcept']]
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['snomedDesIdentifier'].values[0]) == snmd_id:
                df_results = pd.DataFrame()
        elif rule == 2:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['snomedChlIdentifier', 'snomedChlConcept']]
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['snomedChlIdentifier'].values[0]) == snmd_id:
                df_results = pd.DataFrame()
        elif rule == 3:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            # print(query)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['descendantId', 'descendantConcept', 'query']]
            # print(df_results)
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['descendantId'].values[0]) == snmd_id:
                df_results = pd.DataFrame()
        elif rule == 4:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            # print(query)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['descendantId', 'descendantConcept']]
            # print(df_results)
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['descendantId'].values[0]) == snmd_id:
                df_results = pd.DataFrame()
        elif rule == 5:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            # print(query)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['descendantId', 'descendantConcept']]
            print(df_results['descendantId'].values[0])
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['descendantId'].values[0]) == snmd_id:
                df_results = pd.DataFrame()
        elif rule == 6:
            df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snmd_id)
            # print(query)
            df_concepts = df_concepts.query(query)
            df_results = df_concepts[['descendantId', 'descendantConcept']]
            # print(df_results)
            # control that items list does not have only one concept and it is the same ID
            if len(df_results) == 1 and str(df_results['descendantId'].values[0]) == snmd_id:
                df_results = pd.DataFrame()

        return df_results

    def extract_answers(self, userId):
        # read file with new CES
        df_new_ces = pd.read_csv(self.resultsDirectory+"{}partOneAnswersB.csv".format(userId),
                               usecols=['snomedIdentifier','snomedConcept','CES'])
        df_new_ces['snomedIdentifier'] = df_new_ces['snomedIdentifier'].map(str)

        df_new_ces['evaluationAnswers'] = 0
        # read file with evaluation of each annotation
        df_evaluation_ces = pd.read_csv(self.resultsDirectory+"{}partOneAnswersA.csv".format( userId),
                                      usecols=['snomedConcept', 'snomedIdentifier', 'predictedTag', 'evaluationAnswers','confidence'])
        df_evaluation_ces['snomedIdentifier'] = df_evaluation_ces['snomedIdentifier'].map(str)
        df_evaluation_ces = df_evaluation_ces.rename(columns={'predictedTag': 'CES'})

        df_results = df_new_ces.append(df_evaluation_ces)
        # dfResults.info()
        # order by id, answer
        df_results.sort_values(by=['snomedIdentifier', 'evaluationAnswers', 'confidence'], inplace=True, ascending=[True, True, False])
        df_results.to_csv(self.resultsDirectory+'{}SampleP2.csv'.format(userId), index=False)
        # return dfResults

    def next_item_sample_p2(self, userId, snmdId):
        # read doc
        dfsample_p2 = pd.read_csv(self.resultsDirectory+"{}SampleP2.csv".format(userId))
        dfsample_p2['snomedIdentifier'] = dfsample_p2['snomedIdentifier'].map(str)
        dfsample_p2 = dfsample_p2.drop_duplicates(subset=['snomedIdentifier'], keep="first", inplace=False, ignore_index=True)

        if snmdId == -1:
            # selectedId = dfsampleP2.iloc[0]['snomedIdentifier']
            selected_row = dfsample_p2.loc[0]
            # print(selectedId)
        else:
            index_list = dfsample_p2[dfsample_p2['snomedIdentifier'] == snmdId].index[0]
            if (index_list+1) == len(dfsample_p2):
                selected_row = None
            else:
                # selectedRow = dfsampleP2['snomedIdentifier'].loc[index_list + 1]
                selected_row = dfsample_p2.loc[index_list + 1]

        return selected_row

    def next_item_all_ces_p2(self, user_id, snmd_id):
        # read doc
        dfsample_p2 = pd.read_csv(self.resultsDirectory+"{}SampleP2.csv".format(user_id))
        # dfsample_p2['evaluationAnswers'] = dfsample_p2['evaluationAnswers'].map(int)
        dfsample_p2['snomedIdentifier'] = dfsample_p2['snomedIdentifier'].map(str)
        dfsample_p2.info()
        query = 'snomedIdentifier=="{}" and evaluationAnswers < 2'.format(snmd_id)
        print(query)
        list_ces = dfsample_p2.query(query)
        if len(list_ces) < 1:
            list_ces = dfsample_p2.query('snomedIdentifier=="{}"'.format(snmd_id)).head(1)
        print(list_ces)

        return list_ces

    def return_list_rules_item(self, snomed_identifier):
        list_rules = []

        for i in range(1, 7):
            # print(i)
            file_name = "summaryRule"+str(i)+".csv"
            df_rule = pd.read_csv(self.propagationDirectory + file_name)
            df_rule['snomedIdentifier'] = df_rule['snomedIdentifier'].map(str)
            query = 'snomedIdentifier=="{}"'.format(snomed_identifier)
            # print(query)
            dfResult = df_rule.query(query)
            if len(dfResult) >= 1:
                list_rules.append(i)
        return list_rules
