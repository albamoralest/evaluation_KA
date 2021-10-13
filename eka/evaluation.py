'''
Created on 29 Sep 2021

@author: acmt2
'''

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
    sample='1'
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
    # sample='1'
    # setting a number of samples the user will evaluate
    res = DtMngmnt()

    # res.setDirectory(sample)
    res.setDirectory(0)
    # Verify if the user already has answered the question
    username = g.user['username']
    userFile = res.loadUserFile(username)

    if request.method == 'POST':
        error = None
        answerValue = request.form.get('next')

        if error is None:
            # save the results
            snmdIdentifier = request.form.get('snmdIdentifier')
            value = res.getButtonLabel(next)
    #         rowValues = [username,'Q1',patientID,answerValue, value]
    #         res.appendRowsCSVresultsFile(username, rowValues)
    #         #update session values
    #         userFile['q1']['total'] = 1+userFile['q1']['total']
    #         userFile['q1']['current'] = patientID
    #         res.updateUserFile(username, userFile)
        else:
            flash(error)

    # extract one by one the concepts to verify
    if userFile['p1']['total'] == 0:
        # take the first in the list
        sampleNumber = res.getNumberConcepts('2021-08-19_completeDatasetLinkedSnomedN1.csv')
        left = sampleNumber

        snomedConceptAnnotations = res.getConceptsAnnotations(-1, '2021-08-19_completeDatasetLinkedSnomedN1.csv').to_dict()

        print(snomedConceptAnnotations)
        for item in snomedConceptAnnotations:
            for item2 in snomedConceptAnnotations[item]:
                print(snomedConceptAnnotations[item][item2])
    else:
        print(userFile)
    return render_template('webpages/part1.html', title='Part 1', concepts=snomedConceptAnnotations)


@bp.route('/part2', methods=('GET', 'POST'))
@bp.route('/webpages/part2', methods=('GET', 'POST'))
@login_required
def part2():
    # sample='1'
    # setting a number of samples the user will evaluate
    res = DtMngmnt()

    # res.setDirectory(sample)
    res.setDirectory(0)
    # Verify if the user already has answered the question
    username = g.user['username']
    userFile = res.loadUserFile(username)

    # if request.method == 'POST':
    #
    #     error=None
    #     answerValue = request.form.get('answer')
    #
    #     if error is None:
    #         #save the results
    #         patientID =request.form.get('patient')
    #         value = res.getButtonLabel(answerValue)
    #         rowValues = [username,'Q1',patientID,answerValue, value]
    #         res.appendRowsCSVresultsFile(username, rowValues)
    #         #update session values
    #         userFile['q1']['total'] = 1+userFile['q1']['total']
    #         userFile['q1']['current'] = patientID
    #         res.updateUserFile(username, userFile)
    #     else:
    #         flash(error)
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

    return render_template('webpages/question2.html', title='Part 3')  # ,sample=sample, total=sampleNumber,
    # left=left, distinctDatapoints=patientDistinctDatapoints,
    # title='Question 1', details=patientDetails,relevant=patientRelevantInf)