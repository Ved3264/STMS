$(document).ready(function() {
    $('#loginForm').submit(function(event) {
        event.preventDefault(); // Prevent the form from submitting

        var username = $('#email').val();
        var password = $('#password').val();
        var errorMessage = '';

        // Validate username and password
        if (email === '') {
            errorMessage += 'Username is required.<br>';
        }

        if (password === '') {
            errorMessage += 'Password is required.<br>';
        }

    });
});