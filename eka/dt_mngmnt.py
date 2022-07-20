'''
Created on 29 Sep 2021

@author: acmt2
'''

import os
import os.path
import json
import re

import pandas as pd

# import random
from fileinput import filename
import csv, shutil, time
from csv import writer


class DtMngmnt():
    usersDirectory = 0
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
        self.usersDirectory = os.getcwd() + '/eka/users/'
        self.resultsDirectory = os.getcwd() + '/eka/results/'
        # Resources for part 1
        self.resourcesDirectory = os.getcwd()+'/eka/resources/'
        # Resources for part 2, propagation
        self.propagationDirectory = os.getcwd()+'/eka/propagation/'
        
    def verify_user(self, username):
        usersList = [f for f in os.listdir(self.usersDirectory) if not f.startswith('.')]
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
            usersList = [f for f in os.listdir(self.usersDirectory) if not f.startswith('.')]
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
        content['info'] = {}
        content['info']['role'] = 0
        content['info']['specialization'] = 0
        # indicate sample
        # if (userid % 2) == 0:
        #     content['sample'] = 2
        # else:
        #     content['sample'] = 1

        with open(self.usersDirectory + username + ".json", 'w') as outfile:
            json.dump(content, outfile)

    def update_user_file(self, username, content):
        with open(self.usersDirectory + username + ".json", 'w') as outfile:
            json.dump(content, outfile)

    def load_user_file (self, fileName):
        obj = None
        if os.path.isfile(self.usersDirectory + fileName + ".json"):
            with open(self.usersDirectory + fileName + ".json") as json_file:
                obj = json.load(json_file)
        return obj

    def verify_admin(self, user_file):
        try:
            if user_file['admin'] == 'YES':
                return True
            else:
                return False
        except:
            return False

    def get_number_concepts(self, file_name):
        return self.read_csv_file(file_name).snomedIdentifier.value_counts()

    def read_csv_file(self, file_name):
        localPath = self.resourcesDirectory + file_name
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

        # delete duplicates
        df_new = df_concepts.drop_duplicates(subset=['snomedIdentifier'], keep="first", inplace=False,ignore_index=True)

        # if id == -1 then obtain the first id in the list
        if snmdId == -1:
            selected_id = df_concepts.iloc[0]['snomedIdentifier']
            condition_name = df_concepts.iloc[0]['conditionName']
            # print(selectedId)
        else:
            # if id = XXX concept id, then obtain the next id in the list
            # index_list = df_new.index[df_new['snomedIdentifier']==snmdId].tolist()
            index_list = df_new[df_new['snomedIdentifier'] == snmdId].index[0]
            # print("index[0]")
            # print(index_list)
            # index_list = df_new[df_new['snomedIdentifier'] == snmdId].index[0]

            # print(index_list)
            selected_id = df_concepts['snomedIdentifier'].iloc[index_list+1]
            condition_name = df_concepts['conditionName'].iloc[index_list + 1]

        df_concepts = self.read_csv_file('2021-09-29_AllLinkedSnomed.csv')
        df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)
        # # order by id
        # df_concepts.sort_values(by=['snomedIdentifier'], inplace=True, ascending=[True])
        query_sentence = 'snomedIdentifier=="{}"'.format(selected_id)
        annotations_list = df_concepts.query(query_sentence)
        # order by confidence
        annotations_list.sort_values(by=['confidence'], inplace=True, ascending=[False])
        # add a new index column
        annotations_list['index'] = list(range(len(annotations_list)))
        print('print list')
        # print(annotations_list)
        return annotations_list, condition_name

    def create_csv_results_files_p1(self, userID):
        # 1. File one: Answers to all the CES annotations
        fileNameOne = str(userID)+"partOneAnswersA"
        fieldNamePartOne = ['snomedConcept', 'snomedIdentifier', 'conditionName', 'predictedTag', 'confidence',
                            'sentence', 'source', 'support CNL1L2L3', 'support L1L2L3', 'L1', 'L2', 'L3',
                            'evaluationAnswers', 'userConfidence']
        with open(self.resultsDirectory + fileNameOne + '.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartOne)
            writer.writeheader()

        # 2. File two: If given the new CES
        fileNAmeTwo = str(userID)+"partOneAnswersB"
        fieldNamePartTwo = ['username', 'snomedIdentifier', 'snomedConcept', 'CES', 'userConfidence']

        with open(self.resultsDirectory + fileNAmeTwo + '.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNamePartTwo)
            writer.writeheader()

    def append_list_to_csv(self, userID, fileName, newRow):
        # open file in append mode
        with open(self.resultsDirectory + userID + fileName + '.csv', '+a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(newRow)
            # writer = csv.DictWriter(csv_file, newline=dfObject)
            # writer.writerow(newRow)

    def append_dataframe_to_csv(self, userID, file_name, new_data_frame):
        new_data_frame.to_csv(self.resultsDirectory + str(userID) + file_name + '.csv', mode='a', index=False, header=False)

    # def append_dataframe(self, userID, fileName, newDataFrame):
    #     newDataFrame.to_csv(self.resultsDirectory +userID+fileName+".csv", mode='a', index=False, header=False)

    def get_sources_links(self, conditionName, fileName):
        dfConcepts = self.read_csv_file(fileName)

        # condition name without special characters
        conditionName = re.sub(r"[^a-zA-Z0-9 ]", " ", conditionName)
        conditionName = re.sub(' +', ' ', conditionName)
        conditionName = conditionName.replace("syndromes", "syndrome")

        # remove special characters in dataframe
        dfConcepts['conditionName'].replace(regex=True, inplace=True, to_replace=r"[^a-zA-Z0-9 ]", value=' ')
        dfConcepts['conditionName'].replace(regex=True, inplace=True, to_replace=' +', value=' ')
        dfConcepts['conditionName'].replace(regex=True, inplace=True, to_replace="syndromes", value= "syndrome" )

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
        df_concepts['snomedIdentifier'] = df_concepts['snomedIdentifier'].map(str)

        if rule == 1:
            # rename column name
            df_concepts.rename(columns={'snomedDesIdentifier': 'descendantId',
                                        'snomedDesConcept':'descendantConcept'}, inplace=True)
        elif rule == 2:
            # rename column name
            df_concepts.rename(columns={'snomedChlIdentifier': 'descendantId',
                                        'snomedChlConcept': 'descendantConcept'}, inplace=True)

        query = 'snomedIdentifier=="{}"'.format(snmd_id)
        df_concepts = df_concepts.query(query)
        # print(df_concepts)
        df_results = df_concepts[['descendantId', 'descendantConcept']]

        # To verify that if the result is only one row, it should be different than the main snmd identifier
        if len(df_results) > 3:
            df_results = df_results.sample(n=3)
        elif len(df_results) == 1 and str(df_results['descendantId'].values[0]) == snmd_id:
            df_results = pd.DataFrame()

        return df_results

    def extract_answers(self, userId):
        # 1. Read file with new CES
        df_new_ces = pd.read_csv(self.resultsDirectory + "{}partOneAnswersB.csv".format(userId),
                                 usecols=['snomedIdentifier', 'snomedConcept', 'CES', 'userConfidence'])
        df_new_ces['snomedIdentifier'] = df_new_ces['snomedIdentifier'].map(str)
        df_new_ces['userConfidence'] = df_new_ces['userConfidence'].map(int)
        df_new_ces = df_new_ces.query("userConfidence>1")
        df_new_ces['evaluationAnswers'] = 0

        # 2. Read file with evaluation of each annotation
        df_evaluation_ces = pd.read_csv(self.resultsDirectory + "{}partOneAnswersA.csv".format(userId),
                                        usecols=['snomedConcept', 'snomedIdentifier', 'predictedTag',
                                                 'evaluationAnswers', 'confidence', 'userConfidence'])
        df_evaluation_ces['snomedIdentifier'] = df_evaluation_ces['snomedIdentifier'].map(str)
        # filter only the concept with which the participant is familiar or somehow familiar
        df_evaluation_ces['userConfidence'] = df_evaluation_ces['userConfidence'].map(int)
        df_evaluation_ces = df_evaluation_ces.query("userConfidence>1")
        df_evaluation_ces = df_evaluation_ces.rename(columns={'predictedTag': 'CES'})

        # 3. read NO EFFECT list of concepts
        df_ne = pd.read_csv(self.resourcesDirectory + "2021-12-08_NoEffect_shuffled.csv",
                                 usecols=['snomedConcept', 'snomedIdentifier', 'CES', 'evaluationAnswers'])
        df_ne['snomedIdentifier'] = df_ne['snomedIdentifier'].map(str)
        # From df_ne select 25% of the total of familiar answers from the participant
        sample = len(df_evaluation_ces) + len(df_new_ces)
        sample = int(len(df_ne)*0.25)//1
        # 4. For final results, append file #2 and #3
        df_results = df_evaluation_ces.append(df_ne.sample(n=sample))
        # 5. Shuffle results of #2 and #3
        # df_results = df_results.sample(frac=1)
        # 6. Append results file #1 first
        df_results = df_new_ces.append(df_results)

        df_results.sort_values(by=['snomedIdentifier', 'evaluationAnswers'],
                               inplace=True, ascending=[True, True])
        df_results.to_csv(self.resultsDirectory + '{}SampleP2.csv'.format(userId), index=False)
        # return dfResults

    def next_item_sample_p2(self, userId, snmdId):
        # read doc
        dfsample_p2 = pd.read_csv(self.resultsDirectory + "{}SampleP2.csv".format(userId))
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
        dfsample_p2 = pd.read_csv(self.resultsDirectory + "{}SampleP2.csv".format(user_id))
        # dfsample_p2['evaluationAnswers'] = dfsample_p2['evaluationAnswers'].map(int)
        dfsample_p2['snomedIdentifier'] = dfsample_p2['snomedIdentifier'].map(str)
        # dfsample_p2.info()
        query = 'snomedIdentifier=="{}" and evaluationAnswers < 2'.format(snmd_id)
        # print(query)
        list_ces = dfsample_p2.query(query)
        if len(list_ces) < 1:
            list_ces = dfsample_p2.query('snomedIdentifier=="{}"'.format(snmd_id)).head(1)
        # print(list_ces)

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
            # print(dfResult)
            if len(dfResult) >= 1:
                list_rules.append(i)
        return list_rules

    def get_main_concept_attributes(self, snmd_id):
        list_attributes = pd.DataFrame()
        # read doc
        df_attributes = pd.read_csv(self.propagationDirectory+"attributes/2021-07-01_ForecastedAttributesDetails.csv")
        # dfsample_p2['evaluationAnswers'] = dfsample_p2['evaluationAnswers'].map(int)
        df_attributes['snomedIdentifier'] = df_attributes['snomedIdentifier'].map(str)
        # dfsample_p2.info()
        query = 'snomedIdentifier=="{}"'.format(snmd_id)
        df_attributes.sort_values(by=['group'], inplace=True, ascending=[True])
        # print(query)
        list_attributes = df_attributes.query(query)
        # if len(list_attributes) < 1:
        #     list_ces = df_attributes.query('snomedIdentifier=="{}"'.format(snmd_id)).head(1)
        # print(list_attributes)

        return list_attributes

    def get_main_concept_parents(self, snmd_id):
        list_attributes = pd.DataFrame()
        # read doc
        df_parents = pd.read_csv(self.propagationDirectory+"attributes/2021-07-01_ForecastedDatasetParentsDetails.csv")
        # dfsample_p2['evaluationAnswers'] = dfsample_p2['evaluationAnswers'].map(int)
        df_parents['snomedIdentifier'] = df_parents['snomedIdentifier'].map(str)
        # dfsample_p2.info()
        query = 'snomedIdentifier=="{}"'.format(snmd_id)
        df_parents.sort_values(by=['conceptId'], inplace=True, ascending=[True])
        # print(query)
        list_parents = df_parents.query(query)
        # print(list_parents)
        return list_parents

    def create_csv_results_files_p2(self, userID):
        # 1. File one: Answers to all the CES annotations
        file_name = str(userID)+"partTwoAnswers"
        field_name_part_two = ['answer', 'rule', 'snomedIdentifierPropagated', 'snomedIdentifier']
        with open(self.resultsDirectory + file_name + '.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_name_part_two)
            writer.writeheader()