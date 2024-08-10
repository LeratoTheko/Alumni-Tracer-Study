// Alumni/static/js/admin_form.js

$(document).ready(function() {
    $('#id_question_type').change(function() {
        var questionType = $(this).val();
        if (questionType === 'radio' || questionType === 'checkbox' || questionType === 'dropdown') {
            $('#id_options').closest('.form-row').show();
            $('#id_scale_range').closest('.form-row').hide();
        } else if (questionType === 'rating') {
            $('#id_options').closest('.form-row').hide();
            $('#id_scale_range').closest('.form-row').show();
        } else {
            $('#id_options').closest('.form-row').hide();
            $('#id_scale_range').closest('.form-row').hide();
        }
    }).change();
});
