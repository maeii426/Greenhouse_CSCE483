/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File: ./static/js/create_new_account.js                                   */
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Global Variables                                                          */
/* ------------------------------------------------------------------------- */

var num_phone_boxes = 1;
var num_address_fields = 1;

/* ------------------------------------------------------------------------- */
/* Code to Execute on Page Load                                              */
/* ------------------------------------------------------------------------- */

function addLoadEvent(func) {
    var oldonload = window.onload;

    if(typeof window.onload != 'function')
    {
        window.onload = func;
    }
    else
    {
        window.onload = function()
        {
            if(oldonload)
            {
                oldonload();
            }

            func();
        };
    }
}

function updateFooterDate()
{
    document.getElementById('footer-text').innerHTML = "&copy; TeamGreenThumb "
        + new Date().getFullYear() + ": Andrew Kirfman, Aaron Ayrault, Cuong Do, "
        + "Margaret Baxter, Sean McClain, Ifra Traiq";
};

function disableRemovePhoneButton()
{
    var remove_phone = document.getElementById("remove-phone");

    if(remove_phone.className.indexOf("disabled") == -1)
    {
        remove_phone.className = remove_phone.className + " disabled";
    }
};

function disableRemoveAddressButton()
{
    var remove_address = document.getElementById("remove-address");

    if(remove_address.className.indexOf("disabled") == -1)
    {
        remove_address.className = remove_address.className + " disabled";
    }
};

// Schedule functions to run when the page loads
addLoadEvent(updateFooterDate);
addLoadEvent(disableRemovePhoneButton);
addLoadEvent(disableRemoveAddressButton);

/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
host_parser.href = window.location.href;
var host_addr = host_parser.host;

/* ------------------------------------------------------------------------- */
/* Input Form Setting Functions                                              */
/* ------------------------------------------------------------------------- */

function InputFormSetError(elem, elem_box)
{
	var element = document.getElementById(elem);
	var element_box = document.getElementById(elem_box);
	
	if(element.value.trim() == "")
	{
		if(element_box.className.indexOf("has-error") == -1)
		{
			element_box.className = element_box.className + " has-error";
		}

		return false;
	}
	else
	{
		element_box.className = element_box.className.replace("has-error", 
			"").replace("has-warning", "").replace("has-success", "");
		
		return true;
	}	
};

function InputFormSetWarning(elem, elem_box)
{
	var element = document.getElementById(elem);
	var element_box = document.getElementById(elem_box);
	
	if(element.value.trim() == "")
	{
		if(element_box.className.indexOf("has-error") == -1)
		{
			element_box.className = element_box.className + " has-warning";
		}

		return false;
	}
	else
	{
		element_box.className = element_box.className.replace("has-error", 
			"").replace("has-warning", "").replace("has-success", "");
		
		return true;
	}		
};

function InputFormSetSuccess(elem_box)
{
	var element_box = document.getElementById(elem_box);
	
	element_box.className = element_box.className.replace("has-error",
		"").replace("has-warning", "");
	
	element_box.className = element_box.className + " has-success";
};

function InputFormClearAll(elem_box)
{
	var element_box = document.getElementById(elem_box);
	
	element_box.className = element_box.className.replace("has-error", 
		"").replace("has-warning", "").replace("has-success", "");
};

function InputFormDisable(elem_box)
{
	var element_box = document.getElementById(elem_box);
	
	element_box.disabled = true;
};

function InputFormEnable(elem_box)
{
	var element_box = document.getElementById(elem_box);
	
	element_box.disabled = false;
};

function ClearTitle()
{
	var title = document.getElementById("message-title");

	while (title.firstChild) 
	{
		title.removeChild(title.firstChild);
	}
};

function ClearAllInputForms()
{
	// Clear all of the non-repeated boxes
	InputFormClearAll("username-input-box");
	InputFormClearAll("fname-input-box");
	InputFormClearAll("lname-input-box");
	InputFormClearAll("email-input-box");
	InputFormClearAll("password-input-box");
	InputFormClearAll("password-confirm-input-box");

	// Clear phone boxes
	var i = 0;
	for(i = 1; i<=num_phone_boxes; i++)
	{
		InputFormClearAll("phone-input-box-" + String(i));
	} 
	
	// Clear address boxes
	for(i = 1; i<=num_address_fields; i++)
	{
		InputFormClearAll("number-input-box-" + String(i));
		InputFormClearAll("street-input-box-" + String(i));
		InputFormClearAll("city-input-box-" + String(i));
		InputFormClearAll("zip-input-box-" + String(i));
		InputFormClearAll("state-input-box-" + String(i));
		InputFormClearAll("isGreenhouse-input-box-" + String(i));
		InputFormClearAll("isResidence-input-box-" + String(i));
	}
}



/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_create_account";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{  };

ws.onmessage = function(received_message)
{
    if(received_message.data.indexOf("ValidationSucceeded") >= 0)
    {
        var username = document.getElementById("usr").value.trim();
        
        // Send off the rest of the phone numbers and other data
        var phone_i = null;

        var i = 0;
        for(i=1; i<=num_phone_boxes; i++)
        {   
            phone_i = document.getElementById("phone-" + String(i));
            phone_i = phone_i.value.trim().replace(/\D/g, '');
            

            ws.send("InsertPhone:" + String(username) + ":" + String(phone_i));
        }
        
        // Send off the rest of the addresses
        var number_i = null;
        var street_i = null;
        var city_i = null;
        var zip_i = null;
        var state_i = null;
        var isGreenhouse_i = null;
        var isResidencce_i = null;
        
        for(i = 1; i<=num_address_fields; i++)
        {
			// Get the HTML elements from the web page. Retrieve all values from the 
			// HTML elements and strip off any leading and trailing spaces.  
			number_i = document.getElementById("number-" + String(i)).value.trim();
			street_i = document.getElementById("street-" + String(i)).value.trim();
			city_i = document.getElementById("city-" + String(i)).value.trim();
			zip_i = document.getElementById("zip-" + String(i)).value.trim();
			state_i = document.getElementById("state-" + String(i)).value.trim();
			isGreenhouse_i = document.getElementById("isGreenhouse-" + String(i)).value.trim();
			isResidence_i = document.getElementById("isResidence-" + String(i)).value.trim();
			
			// Pack the address up into a message to send 
			ws.send("InsertAddress:" + String(username) + "|" + String(number_i)
				+ "|" + String(street_i) + "|" + String(city_i) + "|" + String(zip_i)
				+ "|" + String(state_i) + "|" + String(isGreenhouse_i) + "|"
				+ String(isResidence_i));
		}
	
		// All non-repeated boxes
		InputFormSetSuccess("username-input-box");
		InputFormSetSuccess("fname-input-box");
		InputFormSetSuccess("lname-input-box");
		InputFormSetSuccess("email-input-box");
		InputFormSetSuccess("password-input-box");
		InputFormSetSuccess("password-confirm-input-box");
		
		// Set phone boxes
		for(i = 1; i<=num_phone_boxes; i++)
		{
			InputFormSetSuccess("phone-input-box-" + String(i));
		}
		
		// Set the address boxes
		for(i = 1; i<=num_address_fields; i++)
		{
			InputFormSetSuccess("number-input-box-" + String(i));
			InputFormSetSuccess("street-input-box-" + String(i));
			InputFormSetSuccess("city-input-box-" + String(i));
			InputFormSetSuccess("zip-input-box-" + String(i));
			InputFormSetSuccess("state-input-box-" + String(i));
			InputFormSetSuccess("isGreenhouse-input-box-" + String(i));
			InputFormSetSuccess("isResidence-input-box-" + String(i));
		} 
		
		// Indicate that the submisison succeeded
		var title = document.getElementById("message-title");
		var success_message = document.createElement("h3");
		success_message.className = "text-success";
		success_message.innerHTML = "Account Submitted Successfully!";
		title.append(success_message);
		
		// Disable all input buttons since we've already added an address
		InputFormDisable("usr");
		InputFormDisable("fname");
		InputFormDisable("lname");
		InputFormDisable("email");
		InputFormDisable("pwd");
		InputFormDisable("pwd-confirm");
		
		for(i = 1; i<=num_phone_boxes; i++)
		{
			InputFormDisable("phone-" + String(i));
		}
		
		for(i = 1; i<=num_address_fields; i++)
		{
			InputFormDisable("number-" + String(i));
			InputFormDisable("street-" + String(i));
			InputFormDisable("city-" + String(i));
			InputFormDisable("zip-" + String(i));
			InputFormDisable("state-" + String(i));
			InputFormDisable("isGreenhouse-" + String(i));
			InputFormDisable("isResidence-" + String(i));
		}
		
		// Disable all extraneous boxes
		
		// Add/remove phone
		var add_phone_button = document.getElementById("add-phone");
		var remove_phone_button = document.getElementById("remove-phone");
		if(add_phone_button.className.indexOf("disabled") == -1)
		{
			add_phone_button.className = add_phone_button.className +  " disabled";
		}
		
		if(remove_phone_button.className.indexOf("disabled") == -1)
		{
			remove_phone_button.className = remove_phone_button.className + " disabled";
		}
		
		// Add/remove Address
		var add_address_button = document.getElementById("add-address");
		var remove_address_button = document.getElementById("remove-address");
		if(add_address_button.className.indexOf("disabled") == -1)
		{
			add_address_button.className = add_address_button.className + " disabled";
		}
		
		if(remove_address_button.className.indexOf("disabled") == -1)
		{
			remove_address_button.className = remove_address_button.className + " disabled";
		}
		
		// Submit account/cancel
		var submit_account_button = document.getElementById("submit-account");
		var cancel_button = document.getElementById("cancel");
		if(submit_account_button.className.indexOf("disabled") == -1)
		{
			submit_account_button.className = submit_account_button.className + " disabled"
		}
		
		if(cancel_button.className.indexOf("disabled") == -1)
		{
			cancel_button.className = cancel_button.className + " disabled";
		}
		
		// Add a large button to have the user return to the main login screen.  
		var login_div = document.getElementById("return-to-login");
		
		var new_button = document.createElement("button");
		
		new_button.className = "btn btn-success btn-block";
		new_button.id = "return-to-login";
		new_button.innerHTML = "Return To Login Screen!"
		new_button.onclick = function(){ window.location.href = '/'; };
		
		login_div.appendChild(new_button);
    }
    else if(received_message.data.indexOf("ValidationFailed") >= 0)
    {
		// Set the message title to indicate failure
		ClearTitle();
		ClearAllInputForms();
		
		// Add a new title that says that the validation failed
		var message = received_message.data.trim();
		message = message.split(":");
		
		var warning_element = document.createElement("h3");
		warning_element.className = "text-danger";
		
		if(message[1] == "Username")
		{
			warning_element.innerHTML = "Username Exists";
		}
		else
		{
			warning_element.innerHTML = "Unknown Error";
		}
		
		var title = document.getElementById("message-title");
		title.appendChild(warning_element);
		
		// Set all of the boxes to red
		
		
		// Do stuff for failure here!!!
		
		
    }
};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Miscellaneous Functions                                                   */
/* ------------------------------------------------------------------------- */

function enableRemovePhoneButton()
{
    var remove_phone = document.getElementById("remove-phone");

    if(remove_phone.className.indexOf("disabled") >= 0)
    {
        remove_phone.className = remove_phone.className.replace("disabled", "");
    }
};

function enableRemoveAddressButton()
{
    var remove_address = document.getElementById("remove-address");

    if(remove_address.className.indexOf("disabled") >= 0)
    {
        remove_address.className = remove_address.className.replace("disabled", "");
    }
};

function AddPhone()
{
	// Remove the title message
	ClearTitle();
	
	// Remove the box colors
	ClearAllInputForms()
	
	// Remove the phone warning title (if it exists)
	var phone_warning = document.getElementById("phone-warning");
	
	if(phone_warning != null)
	{
		var phone_title = document.getElementById("phone-title");
		phone_title.removeChild(phone_warning);
	}
	
    // First check to see if any of the previous phone boxes are empty.  If they
    // are, don't do anything.
    var i = 0;
    var success = true;
    var invalid = false;
    var empty = false;
    for(i = 1; i<=num_phone_boxes; i++)
    {
        var current_phone = document.getElementById("phone-" + String(i));

        // If the box is empty, add an error message
        if(current_phone.value == "")
        {
            // The add operation should fail after this
            success = false;
            empty = true;

            var phone_div = document.getElementById("phone-input-box-" + String(i));
            if(phone_div.className.indexOf("has-error") == -1)
            {
                phone_div.className = phone_div.className + " has-error";
            }
        }

        // If the box is not empty, check if it is valid.  If it is, remove 
        // any error messages remove any error messages
        else
        {
			var phone_value = current_phone.value.trim();
			phone_value = phone_value.replace(/\D/g, '');

			if(phone_value.length != 10)
			{
				// The add operation should fail after this
				success = false;
				invalid = true;

				var phone_div = document.getElementById("phone-input-box-" + String(i));
				if(phone_div.className.indexOf("has-error") == -1)
				{
					phone_div.className = phone_div.className + " has-error";
				}				
			}
			else
			{
				var phone_div = document.getElementById("phone-input-box-" + String(i));
				if(phone_div.className.indexOf("has-error") >= 0)
				{
					phone_div.className = phone_div.className.replace("has-error", "");
				}
			}
        }
    }

    // If one of the boxes was empty, don't add a new one
    if(success == false)
    {
        // Add a warning message next to the address field
        var phone_warning = document.createElement("h4");
        phone_warning.id = "phone-warning";
        phone_warning.className = "text-danger";
        phone_warning.innerHTML = "";
        
        if(empty == true)
        {
			phone_warning.innerHTML = "Marked fields cannot be blank";
		}

		if(invalid == true)
		{
			if(phone_warning.innerHTML == "")
			{
				phone_warning.innerHTML = "Contains Invalid Phone Numbers";
			}
			else
			{
				phone_warning.innerHTML = phone_warning.innerHTML + "<br>"
					+ "Invalid Phone Number(s)";
			}
		}

        var phone_tag = document.getElementById("phone-title");
        phone_tag.appendChild(phone_warning);
		
        return;
    }

    // Increment the number of phone boxes
    num_phone_boxes = num_phone_boxes + 1;

    var new_phone_input_box = document.createElement("div");
    new_phone_input_box.className = "row";
    new_phone_input_box.id = "phone-div-" + String(num_phone_boxes);

    var left_div = document.createElement("div");
    left_div.className = "col-md-4";

    var phone_box = document.createElement("div");
    phone_box.className = "col-md-4 form-group";
    phone_box.id = "phone-input-box-" + String(num_phone_boxes);
    phone_box.innerHTML = "<label for='phone-" + String(num_phone_boxes) + "' id='phone-overtext-"
        + String(num_phone_boxes) + "'>Phone Number:</label>"
        + "<input type='text' class='form-control' id='phone-" + String(num_phone_boxes) + "'>";

    var right_div = document.createElement("div");
    right_div.className = "col-md-4";

    new_phone_input_box.appendChild(left_div);
    new_phone_input_box.appendChild(phone_box);
    new_phone_input_box.appendChild(right_div);

    var existing_phone_list = document.getElementById("phone-list");
    existing_phone_list.appendChild(new_phone_input_box);

    // Enable the remove phone button
    if(num_phone_boxes == 2)
    {
        enableRemovePhoneButton();
    }
}

function RemovePhone()
{
	if(num_phone_boxes == 1)
	{
		return;
	}
	
	// Remove the title message
	ClearTitle();
	
	// Remove the box colors
	ClearAllInputForms()
	
	// Remove the phone warning title (if it exists)
	var phone_warning = document.getElementById("phone-warning");
	
	if(phone_warning != null)
	{
		var phone_title = document.getElementById("phone-title");
		phone_title.removeChild(phone_warning);
	}
	
    // Don't remove the very last phone box
    if(num_phone_boxes == 1)
    {
        return;
    }

    var parent = document.getElementById("phone-list");
    var to_remove = document.getElementById("phone-div-" + String(num_phone_boxes));

    parent.removeChild(to_remove);
    num_phone_boxes = num_phone_boxes - 1;

    if(num_phone_boxes == 1)
    {
        disableRemovePhoneButton();
    }
};

function validateEmail(email) 
{
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

/* ----------------------------------------------------------------------- */
/* AddAddress & Supporting Functions                                       */
/* ----------------------------------------------------------------------- */

function AddAddress()
{
	// Remove the title message
	ClearTitle();
	
	// Remove the box colors
	ClearAllInputForms()
	
	// Remove the address warning title (if it exists)
	var address_warning = document.getElementById("address-warning");
	
	if(address_warning != null)
	{
		var address_title = document.getElementById("address-title");
		address_title.removeChild(address_warning);
	}
	
    // First check to see if any of the previous address boxes are empty.  If they
    // are, don't do anything.
    var i = 0;
    var success = true;
    
    // Check all of the address boxes to make sure that they're all occupied
	// Each address has the following fields:
	//   - Username: id = number-i
	//      * number-input-box-i
	//   - Street Name: id = street-i
	//      * street-input-box-i
	//   - City: id = city-i
	//      * city-input-box-i
	//   - Zip Code: id = zip-i
	//      * zip-input-box-i
	//   - State: id = state-i
	//      * state-input-box-i
	//   - isGreenhouse: id = isGreenhouse-i
	//      * isGreenhouse-input-box-1
	//   - isResidence: id = isResidence-i
	//      * isGreenhouse-input-box-1
	list_of_forms = [["number-", "number-input-box-"],
		["street-", "street-input-box-"],
		["city-", "city-input-box-"],
		["zip-", "zip-input-box-"],
		["state-", "state-input-box-"],
		["isGreenhouse-", "isGreenhouse-input-box-"],
		["isResidence-", "isResidence-input-box-"]];
    
    for(i = 1; i<=num_address_fields; i++)
    {
        var current_address = document.getElementById("address-" + String(i));
        
		var j = 0;
		for(j = 1; j<=list_of_forms.length; j++)
		{
			if(InputFormSetError(list_of_forms[j - 1][0] + String(i), 
				list_of_forms[j - 1][1] + String(i)) == false)
			{
				success = false;
			}
		}
	}

    // If one of the addresses has empty fields, don't add a new one
    if(success == false)
    {
        // Add a warning message next to the address field
        var address_warning = document.createElement("h4");
        address_warning.id = "address-warning";
        address_warning.className = "text-danger";
        address_warning.innerHTML = "Marked fields cannot be blank";

        var address_tag = document.getElementById("address-title");
        address_tag.appendChild(address_warning);

        return;
    }
    else
    {
        // Remove the warning message if necessary.
        var parent = document.getElementById("address-title");
        var to_remove = document.getElementById("address-warning");

        if(to_remove !== null)
        {
            parent.removeChild(to_remove);
        }
    }

    // Create a new address and then add it in
    var parent_address = document.getElementById("address-list");

    // Since we're definitely adding a new address, increment the address counter
    num_address_fields = num_address_fields + 1;

    // Outer div which will contain the entire address element
    var new_address = document.createElement("div");
    new_address.id = "address-" + String(num_address_fields);


    // Add the address number field
    var new_row = document.createElement("div");
    new_row.className = "row";

    var left_div = document.createElement("div");
    left_div.className = "col-md-4";

    var title_div = document.createElement("div");
    title_div.className = "col-md-4";
    title_div.innerHTML = "<h4>Address " + String(num_address_fields) + ":</h4>";

    var right_div = document.createElement("div");
    right_div.className = "col-md-4";

    new_row.appendChild(left_div);
    new_row.appendChild(title_div);
    new_row.appendChild(right_div);

    new_address.appendChild(new_row);


    // Add the number and street name fields
    new_row = document.createElement("div");
    new_row.className = "row";

    left_div = document.createElement("div");
    left_div.className = "col-md-4";

    number_div = document.createElement("div");
    number_div.className = "col-md-1 form-group";
    number_div.id = "number-input-box-" + String(num_address_fields);

    number_div.innerHTML = "<label for='number-" + String(num_address_fields) + "' id='number-overtext-"
        + String(num_address_fields) + "'>Number:</label>\n"
        + "<input type='text' class='form-control' id='number-" + String(num_address_fields) + "'>";


    var street_div = document.createElement("div");
    street_div.className = "col-md-3 form-group";
    street_div.id = "street-input-box-" + String(num_address_fields);

    street_div.innerHTML = "<label for='street-" + String(num_address_fields) + "' id='street-overtext-"
        + String(num_address_fields) + "'>Street Name:</label>\n"
        + "<input type='text' class='form-control' id='street-" + String(num_address_fields) + "'>";

    right_div = document.createElement("div");
    right_div.className = "col-md-4";

    new_row.appendChild(left_div);
    new_row.appendChild(number_div);
    new_row.appendChild(street_div);
    new_row.appendChild(right_div);

    // Add the new number + street data to the new address
    new_address.appendChild(new_row)


    // Add the city and zip fields
    new_row = document.createElement("div");
    new_row.className = "row";

    left_div = document.createElement("div");
    left_div.className = "col-md-4";

    var city_div = document.createElement("div");
    city_div.className = "col-md-2 form-group";
    city_div.id = "city-input-box-" + String(num_address_fields);

    city_div.innerHTML = "<label for='city-" + String(num_address_fields) + "' id='city-overtext-"
        + String(num_address_fields) + "'>City:</label>\n"
        + "<input type='text' class='form-control' id='city-" + String(num_address_fields) + "'>";

    var zip_div = document.createElement("div");
    zip_div.className = "col-md-2 form-group";
    zip_div.id = "zip-input-box-" + String(num_address_fields);

    zip_div.innerHTML = "<label for='zip-" + String(num_address_fields) + "' id='zip-overtext-"
        + String(num_address_fields) + "'>Zip:</label>\n"
        + "<input type='text' class='form-control' id='zip-" + String(num_address_fields) + "'>";

    right_div = document.createElement("div");
    right_div.className = "col-md-4";

    new_row.appendChild(left_div);
    new_row.appendChild(city_div);
    new_row.appendChild(zip_div);
    new_row.appendChild(right_div);

    // Add the new city + zip data to the new address
    new_address.appendChild(new_row);

    // Add the state, isGreenhouse, and isResidence fields
    new_row = document.createElement("div");
    new_row.className = "row";

    left_div = document.createElement("div");
    left_div.className = "col-md-4";

    var state_div = document.createElement("div");
    state_div.className = "col-md-2 form-group";
    state_div.id="state-input-box-" + String(num_address_fields);

    state_div.innerHTML = '<label for="state-' + String(num_address_fields) + '" id="state-overtext-'
        + String(num_address_fields) + '">State:</label>\n'
        + '<select class="form-control" id="state-' + String(num_address_fields) + '" name="state-'
        + String(num_address_fields) + '">'
        + '<option value="">Select One</option>'
        + '<option value="AK">Alaska</option>'
        + '<option value="AL">Alabama</option>'
        + '<option value="AR">Arkansas</option>'
        + '<option value="AZ">Arizona</option>'
        + '<option value="CA">California</option>'
        + '<option value="CO">Colorado</option>'
        + '<option value="CT">Connecticut</option>'
        + '<option value="DC">District of Columbia</option>'
        + '<option value="DE">Delaware</option>'
        + '<option value="FL">Florida</option>'
        + '<option value="GA">Georgia</option>'
        + '<option value="HI">Hawaii</option>'
        + '<option value="IA">Iowa</option>'
        + '<option value="ID">Idaho</option>'
        + '<option value="IL">Illinois</option>'
        + '<option value="IN">Indiana</option>'
        + '<option value="KS">Kansas</option>'
        + '<option value="KY">Kentucky</option>'
        + '<option value="LA">Louisiana</option>'
        + '<option value="MA">Massachusetts</option>'
        + '<option value="MD">Maryland</option>'
        + '<option value="ME">Maine</option>'
        + '<option value="MI">Michigan</option>'
        + '<option value="MN">Minnesota</option>'
        + '<option value="MO">Missouri</option>'
        + '<option value="MS">Mississippi</option>'
        + '<option value="MT">Montana</option>'
        + '<option value="NC">North Carolina</option>'
        + '<option value="ND">North Dakota</option>'
        + '<option value="NE">Nebraska</option>'
        + '<option value="NH">New Hampshire</option>'
        + '<option value="NJ">New Jersey</option>'
        + '<option value="NM">New Mexico</option>'
        + '<option value="NV">Nevada</option>'
        + '<option value="NY">New York</option>'
        + '<option value="OH">Ohio</option>'
        + '<option value="OK">Oklahoma</option>'
        + '<option value="OR">Oregon</option>'
        + '<option value="PA">Pennsylvania</option>'
        + '<option value="PR">Puerto Rico</option>'
        + '<option value="RI">Rhode Island</option>'
        + '<option value="SC">South Carolina</option>'
        + '<option value="SD">South Dakota</option>'
        + '<option value="TN">Tennessee</option>'
        + '<option value="TX">Texas</option>'
        + '<option value="UT">Utah</option>'
        + '<option value="VA">Virginia</option>'
        + '<option value="VT">Vermont</option>'
        + '<option value="WA">Washington</option>'
        + '<option value="WI">Wisconsin</option>'
        + '<option value="WV">West Virginia</option>'
        + '<option value="WY">Wyoming</option>'
        + '</select>';


    var isGreenhouse_div = document.createElement("div");
    isGreenhouse_div.className = "col-md-1 form-group";
    isGreenhouse_div.id = "isGreenhouse-input-box-" + String(num_address_fields);

    isGreenhouse_div.innerHTML = '<label for="isGreenhouse-' + String(num_address_fields)
        + '" id="isGreenhouse-overtext-' + String(num_address_fields) + '">isGreenhouse:</label>'
        + '<select class="form-control" id="isGreenhouse-' + String(num_address_fields) + '" name="isGreenhouse-'
        + String(num_address_fields) + '">'
        + '<option value="">Select One</option>'
        + '<option value="yes">Yes</option>'
        + '<option value="no">No</option>'
        + '</select>';

    var isResidence_div = document.createElement("div");
    isResidence_div.className = "col-md-1 form-group";
    isResidence_div.id = "isResidence-input-box-" + String(num_address_fields);

    isResidence_div.innerHTML = '<label for="isResidence-' + String(num_address_fields)
        + '" id="isResidence-overtext-' + String(num_address_fields) + '">isResidence:</label>'
        + '<select class="form-control" id="isResidence-' + String(num_address_fields) + '" name="isResidence-'
        + String(num_address_fields) + '">'
        + '<option value="">Select One</option>'
        + '<option value="yes">Yes</option>'
        + '<option value="no">No</option>'
        + '</select>';

    right_div = document.createElement("div");
    right_div.className = "col-md-4";

    new_row.appendChild(left_div);
    new_row.appendChild(state_div);
    new_row.appendChild(isGreenhouse_div);
    new_row.appendChild(isResidence_div);
    new_row.appendChild(right_div);

    // Add the rest of the data to the document
    new_address.appendChild(new_row);

    // Append the final element onto the document
    parent_address.appendChild(new_address);

    // Enable the remove phone button
    if(num_address_fields == 2)
    {
        enableRemoveAddressButton();
    }
};

function RemoveAddress()
{	
	if(num_address_fields == 1)
	{
		return;
	}
	
	// Remove the title message
	ClearTitle();
	
	// Remove the box colors
	ClearAllInputForms()
	
	// Remove the address warning title (if it exists)
	var address_warning = document.getElementById("address-warning");
	
	if(address_warning != null)
	{
		var address_title = document.getElementById("address-title");
		address_title.removeChild(address_warning);
	}
	
    var parent = document.getElementById("address-list");
    var number_box_i = document.getElementById("address-" + String(num_address_fields));
    parent.removeChild(number_box_i);


    // Decrement the address number
    num_address_fields = num_address_fields - 1;



    // If there's only one address left, disable the remove address button.
    if(num_address_fields == 1)
    {
        disableRemoveAddressButton();
    }
};

function SubmitAccount()
{	
	// Remove the title message
	ClearTitle();
	
	// Remove the box colors
	ClearAllInputForms()

	// Remove the phone warning title (if it exists)
	var phone_warning = document.getElementById("phone-warning");
	
	if(phone_warning != null)
	{
		var phone_title = document.getElementById("phone-title");
		phone_title.removeChild(phone_warning);
	}
	
	// Remove the address warning title (if it exists)
	var address_warning = document.getElementById("address-warning");
	
	if(address_warning != null)
	{
		var address_title = document.getElementById("address-title");
		address_title.removeChild(address_warning);
	}
	
	// Remove the global header if there is one 
	var title = document.getElementById("message-title");
	title.innerHTML = "";
	
    // Only submit the account if all fields are filled in
    var success = true;
    var bad_email = false;
    var bad_phone = false;

    // Check the username, first name, and last name boxes
	if(InputFormSetError("usr", "username-input-box") == false)
	{
		success = false;
	}
	
	if(InputFormSetError("fname", "fname-input-box") == false)
	{
		success = false;
	}
	
	if(InputFormSetError("lname", "lname-input-box") == false)
	{
		success = false;
	}

	// Check the email and the password forms
	if(InputFormSetError("email", "email-input-box") == false)
	{
		success = false;
	}
	
	// Make sure that the email address is valid
	var email = document.getElementById("email");
	
	if(validateEmail(email.value.trim()) == false)
	{
		bad_email = true;
		
		var email_box = document.getElementById("email-input-box");
	
		if(email_box.className.indexOf("has-error") == -1)
		{
			email_box.className = email_box.className + " has-error";
		}
	}
	
	if(InputFormSetError("pwd", "password-input-box") == false)
	{
		success = false;
	}
	
	if(InputFormSetError("pwd-confirm", "password-confirm-input-box") == false)
	{
		success = false;
	}

    // Check the phone boxes to make sure they're all occupied
    var i = 0;
    var current_phone = null;
    var phone_value = "";
    var phone_box = null;
    for(i = 1; i<= num_phone_boxes; i++)
    {
		if(InputFormSetError("phone-" + String(i),
			"phone-input-box-" + String(i)) == false)
		{
			success = false;
		}
		
		current_phone = document.getElementById("phone-" + String(i));
		
		phone_value = current_phone.value.trim();
		phone_value = phone_value.replace(/\D/g, '');

		if(phone_value.length != 10)
		{
			bad_phone = true;
			
			
			phone_box = document.getElementById("phone-input-box-" + String(i));
			
			if(phone_box.className.indexOf("has-error") == -1)
			{
				phone_box.className = phone_box.className + " has-error";
			}
		}
		
    }

    // Check all of the address boxes to make sure that they're all occupied
	list_of_forms = [["number-", "number-input-box-"],
		["street-", "street-input-box-"],
		["city-", "city-input-box-"],
		["zip-", "zip-input-box-"],
		["state-", "state-input-box-"],
		["isGreenhouse-", "isGreenhouse-input-box-"],
		["isResidence-", "isResidence-input-box-"]];

    for(i = 1; i<=num_address_fields; i++)
    {
		var j = 0;
		for(j = 1; j<=list_of_forms.length; j++)
		{
			if(InputFormSetError(list_of_forms[j - 1][0] + String(i), 
				list_of_forms[j - 1][1] + String(i)) == false)
			{
				success = false;
			}
		}
    }

    // If one of the boxes hasn't been filled in, don't do anything.
    if(success == false)
    {
		var title = document.getElementById("message-title");
		
		var warning_message = document.createElement("h3");
		warning_message.className = "text-danger";
		warning_message.innerHTML = "Forms Left Empty";
		
		if(bad_email == true)
		{
			warning_message.innerHTML = warning_message.innerHTML + "<br>"
				+ "Invalid Email Address";
		}
		
		if(bad_phone == true)
		{
			warning_message.innerHTML = warning_message.innerHTML + "<br>"
				+ "Invalid Phone Number(s)";  
		}
		
		title.appendChild(warning_message);
		
        return;
    }
    else if(bad_email == true)
    {
		var title = document.getElementById("message-title");
		
		var warning_message = document.createElement("h3");
		warning_message.className = "text-danger";
		warning_message.innerHTML = "Invalid Email Addresses";
		
		if(bad_phone == true)
		{
			warning_message.innerHTML = warning_message.innerHTML + "<br>"
				+ "Invalid Phone Number(s)";  			
		}
		
		title.appendChild(warning_message);
		
		return;
	}
	else if(bad_phone == true)
	{
		var title = document.getElementById("message-title");
		
		var warning_message = document.createElement("h3");
		warning_message.className = "text-danger";
		warning_message.innerHTML = "Invalid Phone Number(s)";
		
		title.appendChild(warning_message);
		
		return;
	}
	else
	{
		// Check to make sure that the two password boxes are equal.  
		var password_1 = document.getElementById("pwd").value.trim();
		var password_2 = document.getElementById("pwd-confirm").value.trim();

		if(password_1 != password_2)
		{
			var title = document.getElementById("message-title");
			
			InputFormSetError("pwd", "password-input-box");
			InputFormSetError("pwd-confirm", "password-confirm-input-box");
			
			var warning_message = document.createElement("h3");
			warning_message.className = "text-danger";
			warning_message.innerHTML = "Passwords Do Not Match!";
			
			title.appendChild(warning_message);
			
			var password = document.getElementById("password-input-box");
			var password_confirm = document.getElementById("password-confirm-input-box");
			
			if(password.className.indexOf("has-error") == -1)
			{
				password.className = password.className + " has-error";
			}
			
			if(password_confirm.className.indexOf("has-error") == -1)
			{
				password_confirm.className = password_confirm.className + " has-error";
			}

			return;
		}
	}

    // Gather data to send back to the server.  The way I'm going to collect this data
    // is to build a string that follows a certain format as I step through all of the
    // boxes on a page.  Format:
    // |<tag>|<value>| where tag could be: Phone number and value could be (xxx) xxx-xxxx

    // Need to validate the username first to make sure that it is unique.  There are no
    // further attributes that must be saved.  This function has to be suspended here
    // because we have to wait to hear back from the server.

    // Update here: I basically want to prevent problems with atomicity and race conditions when inserting into
    // the database.  I don't want one user to begin the username validation process and then
    // have another user walk right in and create an account with the same name.  Therefore,
    // send all of the information needed to insert into the Users table if the requested
    // username is valid.  
    var username = document.getElementById("usr").value.trim();
    var fname = document.getElementById("fname").value.trim();
    var lname = document.getElementById("lname").value.trim();
    var email = document.getElementById("email").value.trim();
	var password = document.getElementById("pwd").value.trim();

    ws.send("ValidateUsername:" + String(username) + ":" + String(fname) + ":" + String(lname)
		+ ":" + String(email) + ":" + String(password));
};
