$(document).ready(function () {

    // list to store 0 or 1 representing availability for each time block on timetable
    let availability = new Array(182).fill(0);

    // Exit message
    $('#message').on('click', function () {
       $('#error').addClass('hide-message');
    });

    // Check register input
    $('#register-form').submit(function () {
        let submit = true;
        $('#register-form input').each(function () {
            if (!$(this).val()) {
                submit = false;
            }
        });
        if (!submit) {
            alert("Please fill in all fields");
            return false;
        }
        return true;
    });

    // Check login input
    $('#login-form').submit(function () {
        let submit = true;
        $('#login-form input').each(function () {
            if (!$(this).val()) {
                submit = false;
            }
        });
        if (!submit) {
            alert("Please fill in all fields");
            return false;
        }
        return true;
    });

    // Check join group input
    $('#join-group-form').submit(function () {
        if (!$('#join-group-form input.input-text').val()) {
            alert("Please fill in all fields");
            return false;
        }
        else {
            let code = prompt("Enter groop code", "");
            if (code === "") {
                alert("Please enter join code");
                return false;
            }
            else if (code === null) {
                return false;
            }
            else {
                $('input[name=group-code-join]').val(code);
                return true;
            }
        }
    });

    // Check create group input
    $('#create-group-form').submit(function () {
        if (!$('#create-group-form input.input-text').val()) {
            alert("Please fill in all fields");
            return false;
        }
        else {
            let code = prompt("Enter groop code", "");
            if (code === "") {
                alert("Please enter a join code. This allows your friends to join the group.");
                return false;
            }
            else {
                $('input[name=group-code-create]').val(code);
                return true;
            }
        }
    });


    // Check add member input
    $('#add-member-form').submit(function () {
        if (!$('#add-member-form input.add-member-text').val()) {
            alert("Please enter members username");
            return false;
        }
        else {
            return true;
        }
    });

    // Confirm leaving group
    $('#leave-group-form').submit(function () {
        if (confirm("Are you sure you want to leave this group?")) {
            return true;
        }
        else {
            return false;
        }
    });

    // Check settings input
    $('#username-form').submit(function () {
        if (!$('#username-form input').val()) {
            alert("Please enter username");
            return false;
        }
        else {
            if (confirm("Are you sure you want to change username?")) {
                return true;
            }
            else {
                return false;
            }
        }
    });
    $('#displayname-form').submit(function () {
        if (!$('#displayname-form input').val()) {
            alert("Please enter displayname");
            return false;
        }
        else {
            if (confirm("Are you sure you want to change displayname?")) {
                return true;
            }
            else {
                return false;
            }
        }
    });

    // Toggle settings tab
    $('#settings-btn').on('click', function () {
        $('.settings-tab').toggleClass('open');
    });

    // Toggle sidebar
    $('#sidebar-open').on('click', function () {
        sidebar();
    });
    $('#sidebar-collapse').on('click', function () {
        sidebar();
        if ($('.settings-tab.open')[0]) {
            $('.settings-tab').toggleClass('open');
        }
    });

    // Open notifications
    $('#notifications').on('click', function () {
        $('.notifications').toggleClass('open');
    });

    // Mark Available / Hover animation / Show available members on collab table
    $('td').hover(function () {
        let check = $(this).attr('id');
        if (check == "grey" || check == "red" || check == "yellow" ||
            check == "green" || check == "blue") {
            let members = $(this).attr('class').split(' ')[0];
            $('#available-members').html("AVAILABLE: " + members);
            let hour = $(this).attr('class').split(' ')[1];
            $('.row'+hour).toggleClass('table-row');
        }
        else {
            let hour = $(this).attr('class').split(' ')[1];
            $('.row'+hour).toggleClass('table-row');
        }
    });
    $('td').on('click', function () {
        let check = $(this).attr('id');
        if (check == "grey" || check == "red" ||
            check == "orange" || check == "yellow" ||
            check == "green" || check == "blue") {
                let members = $(this).attr('class').split(' ')[0];
                $('#available-members').html("AVAILABLE: " + members);
        }
        else {
            $(this).toggleClass('available');
        }
    });


    // Mark entire day as available
    $('th').on('click', function () {
        let check = $(this).attr('id');
        $(this).toggleClass('on');
        if ($(this).attr('class').split(' ')[1]) {
            $('.' + check).addClass('available');
        }
        else {
            $('.' + check).removeClass('available');
        }
    });

    // Save Timetable
    $('#timetable-form, #collab-form').submit(function () {
        $('td').each(function () {
            if ($(this).attr('class').split(' ')[2]) {
                let num = $(this).attr('id');
                availability[num] = "1";
            }
        });
        let data = availability.join("");
        $("input[name=timetable-data]").val(data);
    });

    // Reset timetable
    $('#reset').on('click', function () {
        if (confirm('Your timetable will be reset')) {
            $('td').removeClass('available');
        }
    });

    // Collab timetable
    $('#collab-form').submit(function () {
        let name = $('.select-group').val();
        if (name === null) {
            alert("Please select group");
            return false;
        }
        else {
            let data = availability.join("");
            $("input[name=timetable-data-collab]").val(data);
            return true;
        }
        return false;
    });

    // Sidebar toggle function
    function sidebar() {
        $('.sidebar').toggleClass('open');
        $('.sidebar-header').toggleClass('open');
        $('.overlay').toggleClass('open');
        $('.settings-tab').toggleClass('active');
    }
});