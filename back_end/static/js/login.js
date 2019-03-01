/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File: ./login.js                                                          */
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Code to Execute on Page Load                                              */
/* ------------------------------------------------------------------------- */

window.onload = function update_footer_date()
{
    date = new Date().getFullYear();
    document.getElementById('footer-text').innerHTML = "&copy; TeamGreenThumb "
        + date + ": Andrew Kirfman, Aaron Ayrault, Cuong Do, Margaret Baxter, Sean McClain,"
        + " Ifra Traiq";
};

/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
var entered_name = "";
var entered_password = "";
host_parser.href = window.location.href;
var host_addr = host_parser.host;

/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_login";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{  };

ws.onmessage = function(received_message)
{
    if(received_message.data == "ValidationFailed")
    {
		var username_box = document.getElementById("username-input-box");
		var password_box = document.getElementById("password-input-box");
		
		var title = document.getElementById("login-title");
		
		if(username_box.className.indexOf("has-error") == -1)
		{
			username_box.className = username_box.className + " has-error";
		}
		
		if(password_box.className.indexOf("has-error") == -1)
		{
			password_box.className = password_box.className + " has-error";
		}
		
		if(document.getElementById("warning-text") == null)
		{
			var warning_title = document.createElement("h3");
			warning_title.className = "text-danger";
			warning_title.id = "warning-text";
			warning_title.innerHTML = "Login Failed!";
		
			title.appendChild(warning_title);
		}
		
		//return;
		
        document.getElementById("username-input-box").className =
            String(document.getElementById("username-input-box").className) + " has-error";

        document.getElementById("user-overtext").innerHTML = "Username:&nbsp;&nbsp;<p class='text-danger'"
            + " style='display:inline;'>Invalid username!</p>";
    }
    else if(received_message.data == "ValidationSucceeded")
    {
        var username_box = document.getElementById("usr");
        
		window.location.href = "/overview_screen" + "?" + String(username_box.value.trim());
    }
};

ws.onclose = function()
{  };

/* ------------------------------------------------------------------------- */
/* Miscellaneuous Functions                                                  */
/* ------------------------------------------------------------------------- */

function verifyLogin()
{
    // Gather data from the two text input boxes
    entered_name = document.getElementById("usr").value.trim();
    entered_password  = document.getElementById("pwd").value.trim();

    // Validate that input.  Each username and password must be subjected to some
    // consistency checks.  Specifically, only letters, numbers, dashes, and underscores
    // will be allowed for usernames and passwords

    // If either string is empty, don't worry about sending a message.
    // Set the element to indicate an error ane move on
    
    // This variable will store the results of consistency checks on the input.  If 
    // there are any failures, this variable will be set to true and no messages will be
    // sent to the backend server.  
    var test_failure = false;
    if(entered_name == "")
    {
        document.getElementById("username-input-box").className =
            String(document.getElementById("username-input-box").className) + " has-error";

        // Chagne the page HTML to report the failure
        document.getElementById("user-overtext").innerHTML = "Username:&nbsp;&nbsp;<p class='text-danger'"
            + " style='display:inline;'>Field cannot be blank!</p>";       

        test_failure = true;
    }

    if(entered_password == "")
    {
        document.getElementById("password-input-box").className = 
            String(document.getElementById("password-input-box").className) + " has-error";

        // Change the page HTML to report the failure
        document.getElementById("password-overtext").innerHTML = "Password:&nbsp;&nbsp;<p class='text-danger'"
            + " style='display:inline;'>Field cannot be blank!</p>";

        test_failure = true;
    }

    // If something went bad, return without interacting with the backend
    if(test_failure == true)
    {
        return;
    }

    ws.send("ValidateLogin:" + entered_name + ":" + entered_password);
};


