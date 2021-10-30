var name=1;
$("body").on('click', '#radioAddQuestion', function () {

        var singleQuestionModule = "singleQuestionModule";

        var question = $(".module:first").clone();
        var question_label = $(".question-label:first").clone();

        $(question_label).insertBefore(".options-label:last");
        $(question).insertBefore(".options-label");

$(question).find(':radio').attr('name', "n" + name);

	name++;
    });