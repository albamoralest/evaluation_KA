'''
Created on 29 Sep 2021

@author: acmt2
'''
import pandas as pd
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
# from werkzeug.exceptions import abort
from eka.auth import login_required
from eka.dt_mngmnt import DtMngmnt
# from eka import create_app
# application = create_app()

bp = Blueprint('evaluation', __name__)


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # setting a number of samples the user will evaluate
    res = DtMngmnt()
    res.set_directory(0)

    # TODO: change accordingly
    #  Annotations objective
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

    if userFile['p2']['total'] == 0:
        p2percentage = None
        labelp2 = "Click to start Part 2"
    elif userFile['p2']['total'] == objective:
        p2percentage = 100
        labelp2 = "Completed"
    else:
        p2percentage = round((userFile['p2']['total']*100)/objective)
        labelp2 = "Click to continue Part 2"

    return render_template('index.html', title='User study', p1number=p1percentage, labelp1=labelp1,
                           p2number=p2percentage, labelp2=labelp2)


@bp.route('/info', methods=('GET', 'POST'))
@bp.route('/webpages/info', methods=('GET', 'POST'))
@login_required
def info():
    res = DtMngmnt()
    res.set_directory(0)
    username = g.user['username']

    user_file = res.load_user_file(username)
    if request.method == 'POST':
        user_file['info']['role'] = request.form['role']
        user_file['info']['specialization'] = request.form['specialization']
        res.update_user_file(username, user_file)
        print("Update additional participant's additional information")

        return render_template('index.html', title='Registration')
    return render_template('webpages/info.html', title='Registration')


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
    # sample = user_file['sample']

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
            elif error == "incompleteCheckBox":
                error = "Please verify that you selected a response for each row"
            else:
                error = "Evaluation incomplete. Please verify that you have given an answer for each item on the list of CES."

            flash(error, "error")
        else:
            error = None

        # If not error then save response
        if error is None:
            snmd_identifier_main = request.form['snmdIdentifier']
            # 1. The answers to the list of CES
            # Get the list of answers
            answer_list = []
            for i in range(0, int(request.form['totalCES'])):
                radio_group_name = "inlineRadioOptions"+str(i)
                answer_list.append(request.form[radio_group_name])
            # get the condition
            condition_df = res.get_one_condition(snmd_identifier_main, '2021-09-29_AllLinkedSnomed.csv')
            condition_df['evaluationAnswers'] = answer_list

            # 2. Save the confidence value
            condition_df['userConfidence'] = request.form['confidenceResult']

            # save data
            # print(condition_df)
            res.append_dataframe_to_csv(str(user_file['id']), 'partOneAnswersA', condition_df)

            # 3. If provided the new CES
            improve_answer = request.form['improveAnswer']
            # print(improve_answer)
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
                new_ces_row = [user_file['id'], condition_df['snomedIdentifier'].iloc[0], request.form['snmdConcept'],
                               ces_annotation, request.form['confidenceResult']]
                # save data
                res.append_list_to_csv(str(user_file['id']), 'partOneAnswersB', new_ces_row)

            # 4. Update session values
            user_file['p1']['total'] = 1+user_file['p1']['total']
            total_answered = user_file['p1']['total']
            user_file['p1']['current'] = snmd_identifier_main
            res.update_user_file(username, user_file)
            snmd_identifier = user_file['p1']['current']
            # print(total_answered)

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

    print(snmd_identifier)
    # cluster samples for participants
    snomed_concept_annotations, condition_name = \
        res.get_concepts_annotations(snmd_identifier, '2021-12-07_AllLinkedSnomed.csv')
    sourcesLinks = res.get_sources_links(condition_name, 'conditions_links.csv')

    totalCesItems = len(snomed_concept_annotations)
    print(len(snomed_concept_annotations))
    return render_template('webpages/part1.html', title='First Part Study', answered=total_answered,
                           concepts=snomed_concept_annotations.to_dict('records'), items=totalCesItems,
                           sources=sourcesLinks.to_dict('records'))


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

    # total rules
    rules_list = {}

    # for the POST value
    if request.method == 'POST':
        print("POST method")
        error = None
        snmd_identifier = request.form['snmdIdentifier']
        # If no answers in Part 1, cannot start Part 2
        if total_p1 == 0:
            error = "Please complete Part 1 of the study."

        if error is None:
            # 1. The answers to the list of CES
            # Get the list of answers
            answer_list = []
            for i in range(0, int(request.form['total_rows'])):
                radio_group_name = "cb" + str(i)
                answer_list.append(request.form[radio_group_name])

            # print(answer_list)
            df_results = pd.DataFrame(columns=['answer', 'rule', 'snomedIdentifierPropagated', 'snomedIdentifier'])
            for row in answer_list:
                new_row = row.split(',')
                new_row.append(snmd_identifier)
                series_obj = pd.Series(new_row, index=df_results.columns)
                df_results = df_results.append(series_obj, ignore_index=True)

            # save results
            res.append_dataframe_to_csv(str(user_file['id']), 'partTwoAnswers', df_results)
            print("Results")
            # Update results
            user_file['p2']['total'] = 1+user_file['p2']['total']
            total_answers_p2 = user_file['p2']['total']
            user_file['p2']['current'] = snmd_identifier
            res.update_user_file(username, user_file)
        else:
            flash(error)

    if total_answers_p2 == 0:
        snmd_identifier = -1
        # read answers from Part 1, extract the snmdIdentifiers and use these answers for study 2. Do this only once
        res.extract_answers(user_file['id'])
        # create answer file
        res.create_csv_results_files_p2(user_file['id'])

    # find next item on the list
    print("Find next identifier")

    next_item_row = pd.DataFrame()
    list_rules = []
    next_item_row = res.next_item_sample_p2(user_file['id'], snmd_identifier)

    if next_item_row is not None:
        next_item = True
        while next_item:
            rule_one_list = pd.DataFrame()
            items_rules = {}
            rule_two_list = {}
            rule_three_list = {}
            rule_four_list = {}
            rule_five_list = {}
            rule_six_list = {}
            next_snmd_identifier = next_item_row['snomedIdentifier']
            print("Get list rules that apply to the given concept")
            list_rules = res.return_list_rules_item(next_item_row['snomedIdentifier'])
            # print(list_rules)
            for rule in list_rules:
                file_name = ""
                if rule == 1:
                    file_name = '2021-07-12_01DescendantsNoEffectConcepts.csv'
                    rule_one_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_one_list['rule'] = '1'
                    if len(rule_one_list) > 0:
                        rules_list['1'] = 'This condition is a descendant of the main health condition'
                elif rule == 2:
                    file_name = '2021-07-01_02DirectChildrenConcepts.csv'
                    rule_two_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_two_list['rule'] = '2'
                    rule_one_list = rule_one_list.append(rule_two_list)
                    if len(rule_two_list) > 0:
                        rules_list['2'] = 'This condition is a direct descendant of the main health condition'
                elif rule == 3:
                    file_name = '2021-11-19_03RulesMoreOneAtt.csv'
                    rule_three_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_three_list['rule'] = '3'
                    rule_one_list = rule_one_list.append(rule_three_list)
                    if len(rule_three_list) > 0:
                        rules_list['3'] = 'This condition shares similar attribute(s) as the main health condition'
                elif rule == 4:
                    file_name = '2021-11-19_04RulesOneAtt.csv'
                    rule_four_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_four_list['rule'] = '4'
                    rule_one_list = rule_one_list.append(rule_four_list)
                    if len(rule_four_list) > 0:
                        rules_list['4'] = 'This condition is a descendant of the main health condition and shares similar attribute(s)'
                elif rule == 5:
                    file_name = '2021-11-25_05NoAttributes.csv'
                    rule_five_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_five_list['rule'] = '5'
                    rule_one_list = rule_one_list.append(rule_five_list)
                    if len(rule_five_list) > 0:
                        rules_list['5'] = 'This condition shares same parent(s) and/or similar attribute(s) as the main health condition'
                elif rule == 6:
                    file_name = '2021-11-22_06ParentsOnly.csv'
                    rule_six_list = res.get_propagated_concepts(next_snmd_identifier, file_name, rule)
                    rule_six_list['rule'] = '6'
                    rule_one_list = rule_one_list.append(rule_six_list)
                    if len(rule_six_list) > 0:
                        rules_list['6'] = 'This condition shares the same direct parents as the main health condition'
            if len(rule_one_list) > 1:
                print("Propagation " + next_item_row['snomedIdentifier'])
                next_item = False
            else:
                print("No propagation " + next_item_row['snomedIdentifier'] + ". Searching next concept...")
                next_item_row = res.next_item_sample_p2(user_file['id'], next_snmd_identifier)

        print("List of CES from study Part 1")
        rule_one_list.sort_values(by=['rule'], inplace=True, ascending=[True])
        list_ces = res.next_item_all_ces_p2(user_file['id'], next_item_row['snomedIdentifier']).to_dict('records')

        # obtain information about the attributes of the SNOMED concept
        print("Get list of attributes")
        list_attributes_main = res.get_main_concept_attributes(next_snmd_identifier).to_dict('records')
        print("Get list of direct parents")
        list_parents_main = res.get_main_concept_parents(next_snmd_identifier).to_dict('records')
        # list of rules where the concept appears
        # print("Get list rules that apply to the given concept")
        # list_rules = res.return_list_rules_item(next_snmd_identifier)
        # print(list_rules)

        rule_one_list['index'] = list(range(len(rule_one_list)))
        items_rules = rule_one_list.to_dict('records')
        total_rows = len(items_rules)

        # show all the correct CES
        return render_template('webpages/part2.html', title='Part 2', parent=next_item_row, cess=list_ces,
                               attributes=list_attributes_main, parents=list_parents_main,
                               rule1=items_rules, total_rows=total_rows, list_rules=rules_list)
    else:
        return redirect(url_for('evaluation.index'))