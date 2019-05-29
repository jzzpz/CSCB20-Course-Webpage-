document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("confirm_password").addEventListener("keyup", function() {
        
        if (document.getElementById("password").value == this.value) {
            document.getElementById('confirm_password').style.borderColor = null;
            document.getElementById('login-btn').removeAttribute("disabled");
            document.getElementById('login-btn').style.backgroundColor = null;

        } else {
            document.getElementById('login-btn').setAttribute("disabled", "disabled");
            document.getElementById('login-btn').style.backgroundColor = 'grey'
            document.getElementById('confirm_password').style.borderColor = 'red';


        }
    })

})
