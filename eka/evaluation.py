'''
Created on 29 Sep 2021

@author: acmt2
'''
import pandas as pd
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from eka.auth import login_required
from eka.dt_mngmnt import DtMngmnt

bp = Blueprint('evaluation', __name__)


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    posts=""

    # setting a number of samples the user will evaluate
    res = DtMngmnt()
    sample = '1'
    res.setDirectory(sample)

    # returns a random list of IDs
    # sampleList = res.returnRandomSample()
    # sampleNumber=len(sampleList)
    # q1percentage=None
    # q2percentage=None

    # Verify if the user already has answered the question
    username = g.user['username']
    userFile = res.loadUserFile(username)
    # if userFile['q1']['total'] == 0:
    #     q1percentage = None
    #     labelq1 = "Click to start"
    # elif userFile['q1']['total'] == sampleNumber:
    #     q1percentage = 100
    #     labelq1 = "Completed"
    # else:
    #     q1percentage = round((userFile['q1']['total']*100)/sampleNumber)
    #     labelq1 = "Click to continue"

    # res.setDirectory('2')
    # sampleList = res.returnRandomSample()
    # sampleNumber=len(sampleList)
    # if userFile['q2']['total'] == 0:
    #     q2percentage = None
    #     labelq2 = "Click to start"
    # elif userFile['q2']['total'] == sampleNumber:
    #     q2percentage = 100
    #     labelq2 = "Completed"
    # else:
    #     q2percentage = round((userFile['q2']['total']*100)/sampleNumber)
    #     labelq2 = "Click to continue"

    # return render_template('webpages/index.html', totalsample=sampleNumber,q1number=q1percentage,
    #                        q2number=q2percentage,
    #                        labelq1=labelq1,labelq2=labelq2,posts=posts)

    return render_template('index.html', title='Part 1')


@bp.route('/part1', methods=('GET', 'POST'))
@bp.route('/webpages/part1', methods=('GET', 'POST'))
@login_required
def part1():
    res = DtMngmnt()
    res.setDirectory(0)
    username = g.user['username']

    userFile = res.loadUserFile(username)
    snmdIdentifier = userFile['p1']['current']
    totalAnswered = userFile['p1']['total']

    if request.method == 'POST':
        # check if errors happened during validation
        error = request.form['errorValue']
        print(error)
        if len(error) > 0:
            if error == "digitFromInvalid":
                error = "Enter a value different than zero for label FROM."
            elif error == "digitToInvalid":
                error = "Enter a value different than zero for label TO."
            elif error == "needANumberTo":
                error = "Enter a numeric value for label TO."
            elif error == "needANumberFrom":
                error = "Enter a numeric value for label FROM."
            else:
                error = "Evaluation incomplete. Please verify that you have given an answer for each item on the list of CES."

            flash(error, "error")
        else:
            error = None

        # If not error then save response
        if error is None:
            snmdIdentifier = request.form['snmdIdentifier']
            # 1. The answers to the list of CES
            # Get the list of answers
            answerList = []
            for i in range(0, int(request.form['totalCES'])):
                radioGroupName = "inlineRadioOptions"+str(i)
                answerList.append(request.form[radioGroupName])
            # get the condition
            condition_df = res.getOneCondition(snmdIdentifier, '2021-09-29_AllLinkedSnomed.csv')

            condition_df['evaluationAnswers'] = answerList
            print(condition_df)
            # save data
            res.appendDataFrameToCSV(str(userFile['id']), 'partOneAnswersA', condition_df)

            # 2. If provided the new CES
            improveAnswer = request.form['improveAnswer']
            print(improveAnswer)
            if improveAnswer == 'newCES':
                # ['username','snmdIdentifier','newCES']
                CESAnnotation = ""
                directionAnnotation = request.form['direction']
                if directionAnnotation == 'PERMANENT' or directionAnnotation == 'NONE':
                    CESAnnotation = directionAnnotation
                else:
                    paceAnnotation = request.form['pace']
                    durationFrom = request.form['value-from']
                    durationFromAnnotationUnits = request.form['from-lb']
                    durationTo = request.form['value-to']
                    durationToAnnotationUnits = request.form['to-ub']
                    CESAnnotation = "{} {} FROM {} {} TO {} {}".format(directionAnnotation, paceAnnotation,
                                                                       durationFrom, durationFromAnnotationUnits,
                                                                       durationTo, durationToAnnotationUnits)
                newCES_row = [userFile['id'], condition_df['snomedIdentifier'].iloc[0], CESAnnotation]
                # save data
                res.appendListToCSV(str(userFile['id']), 'partOneAnswersB', newCES_row)

            # 3. Update session values
            userFile['p1']['total'] = 1+userFile['p1']['total']
            totalAnswered = userFile['p1']['total']
            userFile['p1']['current'] = snmdIdentifier
            res.updateUserFile(username, userFile)
            print(totalAnswered)

    # snomedConceptAnnotations = {}
    # extract one by one the concepts to verify
    # if zero, then it is the beginning of the evaluation
    if totalAnswered == 0:
        # create the files to store the results
        # 1. Answers to the list of CES
        # 2. If given, the new CES value
        res.createCSVresultsFilesP1(userFile['id'])

        # 3. Extract the snomedIdentifier and CES to evaluate
        # Method returs a df but it is transformed to a dictionary
        snmdIdentifier = -1
        # snomedConceptAnnotations = res.getConceptsAnnotations(-1, '2021-09-29_AllLinkedSnomed.csv').to_dict('records')
    # else:
        # print(snmdIdentifier)
        # Method returs a df but it is transformed to a dictionary
        # snomedConceptAnnotations = res.getConceptsAnnotations(snmdIdentifier, '2021-09-29_AllLinkedSnomed.csv').to_dict('records')

    snomedConceptAnnotations,conditionName = res.getConceptsAnnotations(snmdIdentifier, '2021-09-29_AllLinkedSnomed.csv')
    sourcesLinks = res.getSourcesLinks(conditionName,'2021-05-31_TotalFilesConditions.csv')
    print(sourcesLinks)

    totalCesItems = len(snomedConceptAnnotations)
    print(len(snomedConceptAnnotations))
    return render_template('webpages/part1.html', title='First Part Study', answered=totalAnswered,
                           concepts=snomedConceptAnnotations.to_dict('records'), items=totalCesItems, sources=sourcesLinks.to_dict('records'))


@bp.route('/part2', methods=('GET', 'POST'))
@bp.route('/webpages/part2', methods=('GET', 'POST'))
@login_required
def part2():
    res = DtMngmnt()
    res.setDirectory(0)
    # Verify if the user already has answered the question
    username = g.user['username']
    userFile = res.loadUserFile(username)
    # current evaluation
    snmdIdentifier = userFile['p2']['current']
    totalAnswered = userFile['p2']['total']

    if request.method == 'POST':
        error = None
        answerValue = request.form.get('answer')
    #
        if error is None:
            #save the results
    #         patientID =request.form.get('patient')
    #         value = res.getButtonLabel(answerValue)
    #         rowValues = [username,'Q1',patientID,answerValue, value]
    #         res.appendRowsCSVresultsFile(username, rowValues)
            #update session values
            userFile['p2']['total'] = 1+userFile['p2']['total']
            totalAnswered = userFile['p2']['total']
            userFile['p2']['current'] = snmdIdentifier
            res.updateUserFile(username, userFile)
        else:
            flash(error)
    #
    # #returns a random list of IDs
    # sampleList = res.returnRandomSample()
    # sampleNumber=len(sampleList)
    #
    # #query the number
    # if userFile['q1']['total'] == 0:
    #     left = sampleNumber
    #     patientID = sampleList[0]
    # elif userFile['q1']['total'] == sampleNumber:
    #     #the user has reached the max sample number
    #     return redirect(url_for('index'))
    # else:
    #     left = sampleNumber - userFile['q1']['total']
    #     patientID=userFile['q1']['current']
    #     #find the index of the actual value and select the next ID
    #     j = 0
    #     for i in sampleList:
    #         i = i.replace(".json","")
    #         j+=1
    #         if i == patientID:
    #             break
    #     patientID=sampleList[j]
    #
    # patient = res.loadSampleFile(patientID)
    #
    # patientID = patientID.replace(".json","")
    # patientDetails = patient['patient']['details']
    #
    # patientRelevantInf = patient['patient']['completeData']
    # patientDistinctDatapoints = res.getDistinctDatapoints(patient['patient']['completeData'])
    ruleOneList = {}
    ruleFourList = {}
    if totalAnswered == 0:
        snmdIdentifier = -1

    ruleFourList = res.getPropagatedConcepts(snmdIdentifier, '2021-07-12_04PropAttributesRules.csv').to_dict('records')

    return render_template('webpages/part2.html', title='Part 2', rule1=ruleOneList, rule4=ruleFourList)
    # ,sample=sample, total=sampleNumber,
    # left=left, distinctDatapoints=patientDistinctDatapoints,
    # title='Question 1', details=patientDetails,relevant=patientRelevantInf)