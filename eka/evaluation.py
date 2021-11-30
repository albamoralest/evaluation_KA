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
    # setting a number of samples the user will evaluate
    res = DtMngmnt()
    sample = '1'
    res.set_directory(sample)

    # Annotations objective
    objective = 50

    # Verify if the user already has answered the question
    username = g.user['username']
    userFile = res.load_user_file(username)
    if userFile['p1']['total'] == 0:
        p1percentage = None
        labelp1 = "Click to start Part 1"
    elif userFile['p1']['total'] == objective:
        p1percentage = 100
        labelp1 = "Completed"
    else:
        p1percentage = round((userFile['p1']['total']*100)/objective)
        labelp1 = "Click to continue Part 1"

    # res.setDirectory('2')
    # sampleList = res.returnRandomSample()
    # sampleNumber=len(sampleList)
    if userFile['p2']['total'] == 0:
        p2percentage = None
        labelp2 = "Click to start Part 2"
    elif userFile['p2']['total'] == objective:
        p2percentage = 100
        labelp2 = "Completed"
    else:
        p2percentage = round((userFile['p2']['total']*100)/objective)
        labelp2 = "Click to continue Part 2"

    # return render_template('webpages/index.html', totalsample=sampleNumber,q1number=q1percentage,
    #                        q2number=q2percentage,
    #                        labelq1=labelq1,labelq2=labelq2,posts=posts)

    return render_template('index.html', title='User study', p1number=p1percentage, labelp1=labelp1,
                           p2number=p2percentage, labelp2=labelp2)


@bp.route('/part1', methods=('GET', 'POST'))
@bp.route('/webpages/part1', methods=('GET', 'POST'))
@login_required
def part1():
    res = DtMngmnt()
    res.set_directory(0)
    username = g.user['username']

    user_file = res.load_user_file(username)
    snmd_identifier = user_file['p1']['current']
    total_answered = user_file['p1']['total']

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
            snmd_identifier = request.form['snmdIdentifier']
            # 1. The answers to the list of CES
            # Get the list of answers
            answer_list = []
            for i in range(0, int(request.form['totalCES'])):
                radio_group_name = "inlineRadioOptions"+str(i)
                answer_list.append(request.form[radio_group_name])
            # get the condition
            condition_df = res.get_one_condition(snmd_identifier, '2021-09-29_AllLinkedSnomed.csv')

            condition_df['evaluationAnswers'] = answer_list
            print(condition_df)
            # save data
            res.append_data_frame_to_csv(str(user_file['id']), 'partOneAnswersA', condition_df)

            # 2. If provided the new CES
            improve_answer = request.form['improveAnswer']
            print(improve_answer)
            if improve_answer == 'newCES':
                # ['username','snmdIdentifier','newCES']
                ces_annotation = ""
                direction_annotation = request.form['direction']
                if direction_annotation == 'PERMANENT' or direction_annotation == 'NONE':
                    ces_annotation = direction_annotation
                else:
                    pace_annotation = request.form['pace']
                    duration_from = request.form['value-from']
                    duration_from_annotation_units = request.form['from-lb']
                    duration_to = request.form['value-to']
                    duration_to_annotation_units = request.form['to-ub']
                    ces_annotation = "{} {} FROM {} {} TO {} {}".format(direction_annotation, pace_annotation,
                                                                       duration_from, duration_from_annotation_units,
                                                                       duration_to, duration_to_annotation_units)
                new_ces_row = [user_file['id'], condition_df['snomedIdentifier'].iloc[0], request.form['snmdConcept'], ces_annotation]
                # save data
                res.append_list_to_csv(str(user_file['id']), 'partOneAnswersB', new_ces_row)

            # 3. Update session values
            user_file['p1']['total'] = 1+user_file['p1']['total']
            total_answered = user_file['p1']['total']
            user_file['p1']['current'] = snmd_identifier
            res.update_user_file(username, user_file)
            print(total_answered)

    # snomedConceptAnnotations = {}
    # extract one by one the concepts to verify
    # if zero, then it is the beginning of the evaluation
    if total_answered == 0:
        # create the files to store the results
        # 1. Answers to the list of CES
        # 2. If given, the new CES value
        res.create_csv_results_files_p1(user_file['id'])

        # 3. Extract the snomedIdentifier and CES to evaluate
        # Method returs a df but it is transformed to a dictionary
        snmd_identifier = -1
        # snomedConceptAnnotations = res.getConceptsAnnotations(-1, '2021-09-29_AllLinkedSnomed.csv').to_dict('records')
    # else:
        # print(snmdIdentifier)
        # Method returs a df but it is transformed to a dictionary
        # snomedConceptAnnotations = res.getConceptsAnnotations(snmdIdentifier, '2021-09-29_AllLinkedSnomed.csv').to_dict('records')

    # TODO:
    # cluster samples for participants
    snomed_concept_annotations, condition_name = res.get_concepts_annotations(snmd_identifier, '2021-09-29_AllLinkedSnomed.csv')
    sourcesLinks = res.get_sources_links(condition_name, '2021-05-31_TotalFilesConditions.csv')
    print(sourcesLinks)

    totalCesItems = len(snomed_concept_annotations)
    print(len(snomed_concept_annotations))
    return render_template('webpages/part1.html', title='First Part Study', answered=total_answered,
                           concepts=snomed_concept_annotations.to_dict('records'), items=totalCesItems, sources=sourcesLinks.to_dict('records'))


@bp.route('/part2', methods=('GET', 'POST'))
@bp.route('/webpages/part2', methods=('GET', 'POST'))
@login_required
def part2():
    res = DtMngmnt()
    res.set_directory(0)
    # user information
    username = g.user['username']
    user_file = res.load_user_file(username)
    # current evaluation
    snmd_identifier = user_file['p2']['current']
    total_p1 = user_file['p1']['total']
    total_answers_p2 = user_file['p2']['total']

    if request.method == 'POST':
        error = None
        snmd_identifier = request.form['snmdIdentifier']
    #
        # If no answers in Part 1, cannot start Part 2
        if total_p1 == 0:
            error = "Please complete Part 1 of the study."

        if error is None:
            # save the results
    #         patientID =request.form.get('patient')
    #         value = res.getButtonLabel(answerValue)
    #         rowValues = [username,'Q1',patientID,answerValue, value]
    #         res.appendRowsCSVresultsFile(username, rowValues)
            #update session values
            user_file['p2']['total'] = 1+user_file['p2']['total']
            total_answers_p2 = user_file['p2']['total']
            user_file['p2']['current'] = snmd_identifier
            res.update_user_file(username, user_file)
        else:
            flash(error)

    if total_answers_p2 == 0:
        # TODO: read answers from Part 1
        #  use these answers for study 2 and
        #  extract the snmdIdentifiers from Part 1
        #  save the list
        snmd_identifier = -1
        # total_list_answers = res.extract_answers(user_file['id'])
        res.extract_answers(user_file['id'])

    # find next item on the list
    next_item_row = res.next_item_sample_p2(user_file['id'], snmd_identifier)

    # print(nextItemRow)
    if next_item_row is not None:
        list_ces = res.next_item_all_ces_p2(user_file['id'], next_item_row['snomedIdentifier']).to_dict('records')
        next_snmd_identifier = next_item_row['snomedIdentifier']
        # print(nextSnmdIdentifier)
        list_rules = res.return_list_rules_item(next_snmd_identifier)
        print(list_rules)
        rule_one_list = {}
        rule_two_list = {}
        rule_three_list = {}
        rule_four_list = {}
        rule_five_list = {}
        rule_six_list = {}
        for rule in list_rules:
            file_name = ""
            if rule == 1:
                file_name = '2021-07-12_01DescendantsNoEffectConcepts.csv'
                rule_one_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')
            elif rule == 2:
                file_name = '2021-07-01_02DirectChildrenConcepts.csv'
                rule_two_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')
            elif rule == 3:
                file_name = '2021-11-19_03RulesMoreOneAtt.csv'
                rule_three_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')
            elif rule == 4:
                file_name = '2021-11-19_04RulesOneAtt.csv'
                rule_four_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')
            elif rule == 5:
                file_name = '2021-11-25_05NoAttributes.csv'
                rule_five_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')
            elif rule == 6:
                file_name = '2021-11-22_06ParentsOnly.csv'
                rule_six_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule).to_dict('records')

        # TODO
        # show all the correct CES
        return render_template('webpages/part2.html', title='Part 2', parent=next_item_row, cess=list_ces,
                               rule1=rule_one_list, rule2=rule_two_list, rule3=rule_three_list, rule4=rule_four_list,
                               rule5=rule_five_list, rule6=rule_six_list)
    else:
        return redirect(url_for('index'))
    # ,sample=sample, total=sampleNumber,
    # left=left, distinctDatapoints=patientDistinctDatapoints,
    # title='Question 1', details=patientDetails,relevant=patientRelevantInf)
