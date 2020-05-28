(function($) {
    let form = $("#survey-form");

    form.children("div").steps({
        headerTag: "h3",
        bodyTag: "fieldset",
        transitionEffect: "fade",
        stepsOrientation: "vertical",
        startIndex: 0,
        enableAllSteps: true,
        titleTemplate: '<div class="title"><span class="step-number d-sm-none d-xl-block text-center">#index#</span><span class="step-text">#title#</span></div>',
        labels: {
            previous: 'Previous',
            next: 'Next',
            finish: 'Submit',
            current: '',
            loading: "Loading ..."
        },
        onStepChanging: function(event, currentIndex, newIndex) {
            // change next to finish at the second last step
            if (newIndex == totalSteps - 2) {
                $(".actions a[href='#next'] span").text("Finish")
            } else {
                $(".actions a[href='#next'] span").text("Next")
            }
            highlightCompletedSection();
            save();
            return true;
        },
        onFinishing: function(event, currentIndex) {
            let isComplete = true;
            // check all choice
            let choice_set = new Set();
            let section_set = new Set();

            // single-choice
            $('input:radio, input:checkbox').each(function() {
                let name = $(this).attr("name");
                if (!$("input[name=" + name + "]").is(':checked')) {
                    let question = $(this).closest('.question').children('.question-title').children('p').text()
                    let section = $(this).closest('fieldset').children('h2').text()
                    choice_set.add("<span class='highlight'>" + section + "</span> " + question);
                    section_set.add($(this).closest("fieldset").attr("id").replace("-p-", "-t-"));
                    isComplete = false;
                }
            });

            // check all open questions
            let textarea_set = new Set();
            $("textarea").each(function() {
                if(!$(this).val()) {
                    isComplete = false;
                    textarea_set.add("<span class='highlight'>" + $(this).parent().siblings("h2").text() + "</span> " +
                                    $(this).prev().first().text());
                }
            });

            if (!isComplete) {
                let incomplete_count = choice_set.size + textarea_set.size;
                let modal_message = "<p>There are <span class='highlight'>"+ incomplete_count +"</span> questions you didn't answer:</p>";
                modal_message += "<p>[Choice]</p>";
                choice_set.forEach(function(value){
                    modal_message += "<p>" + value + "</p>";
                });
                modal_message += "<p>[Open-ended]</p>";
                textarea_set.forEach(function(value){
                    modal_message += "<p>" + value + "</p>";
                });
                modal_message += "<p>Do you still want to submit the survey?</p>";
                dialog(modal_message,
                function() {
                    save(form)
                },
                function() {
                });
                return;
            }
            return true;
        },
        onFinished: function(event, currentIndex) {
            save(form)
        },
        onStepChanged: function(event, currentIndex, priorIndex) {
            return true;
        }
    });
    // mark green when section complete
    highlightCompletedSection();

    // style button group
    $("#save a").prepend("<i class='fas fa-save mr-2'></i>");
    $("a[href='#next']").wrapInner("<span></span>");
    $("a[href='#next']").append("<i class='fas fa-chevron-right ml-2'></i>");
    $("a[href='#previous']").wrapInner("<span></span>");
    $("a[href='#previous']").prepend("<i class='fas fa-chevron-left mr-2'></i>");
    $("a[href='#finish']").wrapInner("<span></span>");
    $("a[href='#finish']").append("<i class='fas fa-cloud-upload-alt ml-2'></i>\n");
    // add save listener
    $( "#save" ).click(function() { save(); });
    // add class
    $(".wizard").addClass("row").addClass("justify-content-end");
    $(".wizard .steps").addClass("col-md-3").addClass("d-none d-md-flex");
    $(".wizard .content").addClass("col-md-9");
    $(".wizard .actions").addClass("fixed-bottom mr-5");
    $(".wizard .actions ul").addClass("float-right");
    $(".wizard .actions ul li a").addClass("px-4 py-2 px-sm-5 py-sm-3");

    let totalSteps = $(".steps").find('li').length;

})(jQuery);

function dialog(message, yesCallback, noCallback) {
    $('.modal-body').html(message);
    let dialog = $('#submit_modal').modal();

    $('#btnYes').click(function() {
        yesCallback();
    });
    $('#btnNo').click(function() {
        noCallback();
    });
}

function composeData(data, key, value) {
    // split for matrix
    key = key.split('_')[0]
    // filter
    value = value.split(";;;").join(',')
    // compose data dict
    if (data[key]) {
        data[key] = data[key] + ";;;" + value
    } else {
        data[key] = value
    }
}

function save(form) {
    let data = {}
    // auth
    composeData(data, 'csrfmiddlewaretoken', $("input[name='csrfmiddlewaretoken']").val())
    composeData(data, 'uid', $("input[name='uid']").val())
    composeData(data, 'token', $("input[name='token']").val())

    // choice, choice-text, choice-multi-text, degree
    $("#survey-form input:checked").each(function() {
        composeData(data, $(this).attr('name'), $(this).val())
    })

    // textarea
    $("#survey-form textarea").each(function() {
        if ($.trim($(this).val())) {
            let value = $(this).data('prefix') ? $(this).data('prefix') + $(this).val() : $(this).val()
            composeData(data, $(this).attr('name'), value)
        }
    })

    $.ajax({
        url: '/survey/save/',
        type: 'post',
        dataType: 'json',
        data: data,
        success: function(res) {
            success("survey saved");
            if(form) form.submit();
        },
        error: function(res) {
            error("error");
        },
    });
}

function highlightCompletedSection() {
    // check all choice
    let section_set_complete = new Set();
    let section_set_incomplete = new Set();

    $('input:radio, input:checkbox').each(function() {
        let name = $(this).attr("name");
        if (!$("input[name=" + name + "]").is(':checked')) {
            section_set_incomplete.add($(this).closest("fieldset").attr("id").replace("-p-", "-t-"));
        } else {
            section_set_complete.add($(this).closest("fieldset").attr("id").replace("-p-", "-t-"));
        }
    });

    $("textarea").each(function() {
        if($(this).parents('.matrix-text').length != 0) return;
        if(!$(this).val()) {
            section_set_incomplete.add($(this).closest("fieldset").attr("id").replace("-p-", "-t-"));
        } else {
            section_set_complete.add($(this).closest("fieldset").attr("id").replace("-p-", "-t-"));
        }
    });

    section_set_complete.forEach(function(value){
        if (section_set_incomplete.has(value)) {
            section_set_complete.delete(value);
        }
    });

    // add class complete
    section_set_complete.forEach(function(value){
        // add
        $("#" + value + " .step-number").addClass("complete");
        $("#" + value + " .step-text").addClass("complete");
        // remove listener
        $("#" + value).one( "click", function() {
            $("#" + value + " .step-number").removeClass("complete");
            $("#" + value + " .step-text").removeClass("complete");
        } );
    })
}

$('.other-text').change(function(){
    $(this).prev().prev().val($(this).data('choice') + $(this).val());
})

$('.choice-text input').change(function(){
    if ($(this).hasClass("other-radio")) {
        $(this).siblings("input").show().focus()
    } else if ($(this).hasClass("radio")) {
        $(this).parent().parent().find(".other-text").hide()
    }
})

$('.choice-multi-text input.other-radio').change(function(){
    if ($(this).is(':checked')){
        $(this).siblings("input").show().focus()
    } else {
        $(this).siblings("input").hide()
    }
})

$('input.matrix-radio').change(function(){
    $(this).parent().parent().find(('input:radio')).each(function() {
        if($(this).is(':checked')){
            $(this).siblings('label').html('&#10003;')
        } else {
            $(this).siblings('label').text('_')
        }
    })
})