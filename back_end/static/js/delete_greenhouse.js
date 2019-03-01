/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File:                          */
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
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_delete_greenhouse";
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
    // Why are you sending websocket messages here?
    // In the else statement?
    
    var body = document.getElementById("greenhouse_display");
    var message = greenhouse_ids.split(":");
    
    if(message.length == 1)
    {
        var title_box = document.createElement("div");
        title_box.style = "padding-left=0px; padding-right=0px;";
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
            var title_box = document.createElement("div");
            title_box.style = "padding-left:0px; padding-right:0px;";
            title_box.id = "greenhouse:" + String(message[i]);
            title_box.onmouseover = function() {darken(this)};
            title_box.onmouseout = function() {normal(this)};
            title_box.onclick = function() {remove(this)};
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
    
    var body = document.getElementById("greenhouse:" + String(greenhouse_id));
    var first = document.createElement("h4");
    first.innerHTML = address; 
    var second = document.createElement("h4");
    second.innerHTML = state;
         
    body.appendChild(first);
    body.appendChild(second);
}

function darken(x)
{
    x.style = "background:#f2f2f2 !important";
}

function normal(x)
{
    x.style = "background:#ffffff !important";
}

function make_warning(x)
{
    x.style = "background:#ffe6e6 !important";
}

function remove(x)
{
    var message = x.id.split(":");
    x.style = "background:#ffe6e6 !important";
    var div_contain = document.createElement("div");
    div_contain.id = "wrapper" + String(message[1]);
    div_contain.className = "span12";
    div_contain.style = "padding-left:12px; padding-right:12px;";
    var proceed_btn = document.createElement("button");
    proceed_btn.id = "proceed_btn";
    proceed_btn.innerHTML = "I'm Sure";
    proceed_btn.className = "btn btn-success";
    proceed_btn.onclick = function() {proceed_fnc(x)};
    var cancel_btn = document.createElement("button");
    cancel_btn.id = "cancel_btn";
    cancel_btn.innerHTML = "Wait...";
    cancel_btn.className = "btn btn-primary";
    cancel_btn.onclick = function() {cancel_fnc(x)};
    var warn_msg = document.createElement("h5");
    warn_msg.id = "warn_msg";
    warn_msg.innerHTML = "Are you sure you want to delete everything associated with Greenhouse " + String(message[1]) + "?";
    var button_group = document.createElement("div");
    button_group.id = "warn_btn";
    button_group.className = "form-group";
    button_group.style = "padding-top:0px;"
    button_group.appendChild(proceed_btn);
    button_group.appendChild(cancel_btn);
    
    x.appendChild(div_contain);
    div_contain.appendChild(warn_msg);
    div_contain.appendChild(button_group);
    x.onmouseover = function() {};
    x.onmouseout = function() {};
    x.onclick = function() {};
}

function proceed_fnc(x)
{
    var message = x.id.split(":");
    x.style = "background:#ffffff !important";
    ws.send("RemoveGreenhouse:" + String(message[1]));
}

function cancel_fnc(x)
{
    var message = x.id.split(":");
    x.style = "background:#ffffff !important";
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    x.removeChild(div_contain);
    
    window.location.reload();
}