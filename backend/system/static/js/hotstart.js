function initDeleteButtons() {
    $(".remove-button").on("click", function () {
        return confirm("Объект будет удален. Вы уверены?");
    });
}

function initClickableRows() {
    $(".clickable-row").on("click", function () {
        href = $(this).data("href");
        window.location = href;
    });
}


var BootstrapForm = {
    init: function () {
        BootstrapForm.addClassToInputs($(".bootstrap-form"));
    },

    addClassToInputs: function ($form) {
        $form.find("input").each(function () {
            if (this.type != 'submit' && this.type != 'checkbox')
                $(this).addClass("form-control");
        });
        $form.find("select").each(function () {
            $(this).addClass("form-control");
        });
    }
};


function addDatePicker(ids) {
    $(document).ready(function () {
        try {
            for (var i = 0; i < ids.length; i++) {
                var date_input = $("#" + ids[i]);
                date_input.datepicker({
                    'format': "dd.mm.yyyy"
                });
                date_input.css("max-width", "200px");
                date_input.css("line-height", "1em");
            }
        } catch (e) {
        }
    });
}

$(document).ready(function () {
    initDeleteButtons();
    initClickableRows();
    BootstrapForm.init();
});
