/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File: ./static/js/create_new_account.js                                   */
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Global Variables                                                          */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var host_name = host_parser.search;
var username = host_name.replace("?", "").replace("%20", " ");

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

// Schedule functions to run when the page loads
addLoadEvent(updateFooterDate);

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
	// Clear address boxes
	InputFormClearAll("greenhouse-width");
	InputFormClearAll("greenhouse-height");
	InputFormClearAll("number-input-box");
	InputFormClearAll("street-input-box");
	InputFormClearAll("city-input-box");
	InputFormClearAll("zip-input-box");
	InputFormClearAll("state-input-box");
}

/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_create_greenhouse";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{  
   ws.send("HasGreenhouses:" + String(username)); 
};

ws.onmessage = function(received_message)
{
    if(received_message.data.indexOf("UserHasGreenhouses") >= 0)
    {
        AddGreenhouse(received_message.data);
    }
    else if(received_message.data == "UserHasNoGreenhouses")
    {
        AddGreenhouse(received_message.data);
    }
    else if(received_message.data.indexOf("GreenhouseAddress") >= 0)
    {
        AddAddress(received_message.data);
    }
    else if(received_message.data == "Reload")
    {
        window.location.reload();
    }
};

ws.onclose = function()
{  };

function AddGreenhouse(greenhouse_ids)
{
    var body = document.getElementById("greenhouse_display");
    var message = greenhouse_ids.split(":");
    
    if(message.length == 1)
    {
        var title_box = document.createElement("row");
        var title = document.createElement("h3");
        title.innerHTML = "No Greenhouses Linked";
             
        body.appendChild(title_box);
        title_box.appendChild(title);  
    }
    else
    {
        var i = 0;
        for(i = 1; i<message.length; i++)
        {
            ws.send("SendGreenhouseInfo:" + String(message[i]));
            var title_box = document.createElement("row");
            title_box.id = "greenhouse" + String(message[i]);
            
            var title = document.createElement("h3");
            title.innerHTML = "Greenhouse " + String(message[i]); 
                 
            body.appendChild(title_box);
            title_box.appendChild(title);  
        }
    }
}

function AddAddress(data) 
{
    var message = data.split(":");
    var greenhouse_id = message[1];
    
    var address = message[3] + " " + message[4];
    var state = message[5] + ", " + message[7] + " " + message[6];
    
    var body = document.getElementById("greenhouse" + String(greenhouse_id));
    var first = document.createElement("h4");
    first.innerHTML = address; 
    var second = document.createElement("h4");
    second.innerHTML = state;
         
    body.appendChild(first);
    body.appendChild(second);
    
}

function Submit()
{
    ClearTitle();
    ClearAllInputForms();
    
    // Only submit the account if all fields are filled in
    var success = true;
    
    if(InputFormSetError("number","number-input-box") == false)
		success = false;

    if(InputFormSetError("street","street-input-box") == false)
		success = false;
		
	if(InputFormSetError("city","city-input-box") == false)
		success = false;
		
	if(InputFormSetError("zip","zip-input-box") == false)
		success = false;
		
	if(InputFormSetError("state","state-input-box") == false)
		success = false;

    // If one of the boxes hasn't been filled in, don't do anything.
    if(success == false)
    {
		var title = document.getElementById("message-title");
		
		var warning_message = document.createElement("h3");
		warning_message.className = "text-danger";
		warning_message.innerHTML = "Forms Left Empty";
		
		title.appendChild(warning_message);
		
        return;
    }
    
    var houseNumber = document.getElementById("number").value.trim();
    var street = document.getElementById("street").value.trim();
    var city = document.getElementById("city").value.trim();
    var zip = document.getElementById("zip").value.trim();
	var state = document.getElementById("state").value.trim();
	
	ws.send("CreateGreenhouse:" + String(username) + ":" + String(houseNumber) + ":" + String(street) + ":" + 
	    String(city) + ":" + String(zip) + ":" + String(state));
}