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
var locations = ''

function emptyRefresh()
{
    var parent = document.getElementById("greenhouse_display");
    while (parent.hasChildNodes()) {
        parent.removeChild(parent.firstChild);
    }
    
    ws.send("HasGreenhouses:" + String(username)); 
}

function checkTitle()
{
    var title = document.getElementById("message-title");
    while (title.childElementCount > 2)
    {
        title.removeChild(title.firstChild);
    }
}

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

var socket_addr = "ws://" + host_addr + "/ws_add_component";
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
    else if(received_message.data == "Reload")
    {
        window.location.reload();
    }
    else if(received_message.data.indexOf("ShowSuccess") >= 0)
    {
        show_success(received_message.data);
    }
    else if(received_message.data.indexOf("MakeWarning") >= 0)
    {
        make_warning(received_message.data);
    }
    else if(received_message.data.indexOf("Details") >= 0)
    {
        store_data(received_message.data);
    }
};

ws.onclose = function()
{  };

function AddGreenhouse(greenhouse_ids)
{
    checkTitle();
    
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
            
            var address = message[i+3] + " " + message[i+4];
            var state = message[i+5] + ", " + message[i+7] + " " + message[i+6];
            var first = document.createElement("h4");
            first.innerHTML = address; 
            var second = document.createElement("h4");
            second.innerHTML = state;
            var uninit_relays = document.createElement("h5");
            uninit_relays.innerHTML = "Number of uninitialized relays: " + String(message[i+8]);
            uninit_relays.id = "greenhouse" + message[i] + "relays";
            uninit_relays.name = String(message[i+8]);
            var locs = document.createElement("h5");
            locs.innerHTML = "Number of pots and planters: " + String(message[i+9]);
            locs.id = "greenhouse" + message[i] + "locations";
            locs.name = String(message[i+9]);
                 
            i = i + 9;
                 
            body.appendChild(title_box);
            title_box.appendChild(title);  
            title_box.appendChild(first);
            title_box.appendChild(second);
            title_box.appendChild(uninit_relays);
            title_box.appendChild(locs);
        }
    }
    
    var memory = sessionStorage.getItem('state');
    sessionStorage.removeItem('state');
    if(memory.indexOf('location') >= 0)
    {
        create_location(memory);
    }
    else if(memory.indexOf('solenoid') >= 0)
    {
        var message = memory.split(":");
        var check_relay = document.getElementById("greenhouse" + message[1] + "relays");
        var uninit = parseInt(check_relay.name);
        var check_locs = document.getElementById("greenhouse" + message[1] + "locations");
        var locs = parseInt(check_locs.name);
        if(uninit > 0 && locs > 0)
        {
            create_solenoid(memory);
        }
        else
        {
            explain(String(message[1]) + ":You need an uninitialized relay and a plant location to add this component");
        }
    }
    else if(memory.indexOf('vent') >= 0)
    {
        var message = memory.split(":");
        var check_relay = document.getElementById("greenhouse" + message[1] + "relays");
        var uninit = parseInt(check_relay.name);
        if(uninit > 0)
        {
            create_vent(memory);
        }
        else
        {
            explain(String(message[1]) + ":You need an uninitialized relay to add this component");
        }
    }
    else if(memory.indexOf('light') >= 0)
    {
        var message = memory.split(":");
        var check_relay = document.getElementById("greenhouse" + message[1] + "relays");
        var uninit = parseInt(check_relay.name);
        if(uninit > 0)
        {
            create_light(memory);
        }
        else
        {
            explain(String(message[1]) + ":You need an uninitialized relay to add this component");
        }
    }
    
    var warning = sessionStorage.getItem('warn');
    sessionStorage.removeItem('warn');
    if(warning.indexOf('warn') >= 0)
    {
        make_warning(warning);
    }
}

function store_data(data) 
{
    var message = data.split(":");
    
    if(locations.indexOf("greenhouse" + String(message[1])) >= 0)
    {
        locations = '';
        var i = 0;
        var add_this = true;
        var first = true;
        var save_data = locations.split(":");
        for(i=0; i<save_data.length; i++)
        {
            if(i == locations.indexOf("greenhouse" + String(save_data[1])))
                add_this = false;
            else if(add_this == false && save_data[i].indexOf(String(save_data[1])) >= 0)
                add_this = true;
            if(add_this)
                if(first)
                {
                    locations = locations + String(save_data[i]);
                    first = false;
                }
                else
                {
                    locations = locations + ":" + String(save_data[i]);
                }
        }
        if (locations.length != 0)
        {
            locations = locations + ":";
        }
        locations = locations + "greenhouse" + String(message[1]) + ":";
        var i = 0;
        for(i=2; i<message.length; i++)
        {
            if(i == message.length - 1)
            {
                locations = locations + String(message[i]);
            }
            else
            {
                locations = locations + String(message[i]) + ":";
            }
        }
    }
    else 
    {
        if (locations.length != 0)
        {
            locations = locations + ":";
        }
        locations = locations + "greenhouse" + String(message[1]) + ":";
        var i = 0;
        for(i=2; i<message.length; i++)
        {
            if(i == message.length - 1)
            {
                locations = locations + String(message[i]);
            }
            else
            {
                locations = locations + String(message[i]) + ":";
            }
        }
    }
}

function darken(x)
{
    x.style = "background:#f2f2f2 !important";
}

function normal(x)
{
    x.style = "background:#ffffff !important";
}

function remove(x)
{
    var message = x.id.split(":");
    x.style = "background:#ffffff !important";
    
    var warn_msg = document.createElement("label");
    warn_msg.id = "warn_msg";
    warn_msg.innerHTML = "Select component type:";
    var selection = document.createElement("select");
    selection.className = "selectpicker";
    selection.id = "selection" + String(message[1]);
    selection.className = "form-control";
    
    var plants = document.createElement("optgroup");
    plants.label = "Plants";
    selection.appendChild(plants);
    var type_loc = document.createElement("option");
    type_loc.value = "loc";
    type_loc.innerHTML = "Location";
    plants.appendChild(type_loc);
    var control = document.createElement("optgroup");
    control.label = "Control";
    selection.appendChild(control);
    var type_relay = document.createElement("option");
    type_relay.value = "relay";
    type_relay.innerHTML = "Relay";
    control.appendChild(type_relay);
    var relay_req = document.createElement("optgroup");
    relay_req.label = "Require Relay";
    selection.appendChild(relay_req);
    var type_vent = document.createElement("option");
    type_vent.value = "vent";
    type_vent.innerHTML = "Fan";
    relay_req.appendChild(type_vent);
    var type_lights = document.createElement("option");
    type_lights.value = "light";
    type_lights.innerHTML = "LED strip";
    relay_req.appendChild(type_lights);
    var type_solenoid = document.createElement("option");
    type_solenoid.value = "solenoid";
    type_solenoid.innerHTML = "Solenoid";
    relay_req.appendChild(type_solenoid);
    /*var other = document.createElement("optgroup");
    other.label = "Sensors and Actuators";
    selection.appendChild(other);
    var type_airt = document.createElement("option");
    type_airt.value = "airt";
    type_airt.innerHTML = "Air Temperature";
    other.appendChild(type_airt);
    var type_hum = document.createElement("option");
    type_hum.value = "humidity";
    type_hum.innerHTML = "Humidity";
    other.appendChild(type_hum);
    var type_ph = document.createElement("option");
    type_ph.value = "ph";
    type_ph.innerHTML = "pH";
    other.appendChild(type_ph);
    var type_soilm = document.createElement("option");
    type_soilm.value = "soilm";
    type_soilm.innerHTML = "Soil Moisture";
    other.appendChild(type_soilm);
    var type_wlev = document.createElement("option");
    type_wlev.value = "wlev";
    type_wlev.innerHTML = "Water Level";
    other.appendChild(type_wlev);
    var type_wtemp = document.createElement("option");
    type_wtemp.value = "wtemp";
    type_wtemp.innerHTML = "Water Temp";
    other.appendChild(type_wtemp);*/
    
    var div_contain = document.createElement("div");
    div_contain.id = "wrapper" + String(message[1]);
    div_contain.className = "span12";
    div_contain.style = "padding-left:12px; padding-right:12px;";
    var proceed_btn = document.createElement("button");
    proceed_btn.id = "proceed_btn";
    proceed_btn.innerHTML = "Proceed";
    proceed_btn.className = "btn btn-success";
    proceed_btn.onclick = function() {proceed_fnc(x)};
    var cancel_btn = document.createElement("button");
    cancel_btn.id = "cancel_btn";
    cancel_btn.innerHTML = "Nevermind";
    cancel_btn.className = "btn btn-primary";
    cancel_btn.onclick = function() {cancel_fnc(x)};
    var button_group = document.createElement("div");
    button_group.id = "warn_btn";
    button_group.className = "form-group";
    button_group.style = "padding-top:12px;"
    button_group.appendChild(proceed_btn);
    button_group.appendChild(cancel_btn);
    
    x.appendChild(div_contain);
    div_contain.appendChild(warn_msg);
    div_contain.appendChild(selection);
    div_contain.appendChild(button_group);
    x.onmouseover = function() {};
    x.onmouseout = function() {};
    x.onclick = function() {};
}

function proceed_fnc(x)
{
    var message = x.id.split(":");
    x.style = "background:#ffffff !important";
     
    var selector = document.getElementById("selection" + String(message[1]));
    var svalue = selector.value;
    
    if (svalue == "relay")
    {
        do_relay(x);   
    }
    else if (svalue == "solenoid")
    {
        do_solenoid(x);   
    }
    else if (svalue == "loc")
    {
        do_location(x);   
    }
    else if (svalue == "vent")
    {
        do_vent(x);   
    }
    else if (svalue == "light")
    {
        do_light(x);
    }
}

function submit_fnc(x, selection, type)
{
    var message = x.id.split(":");
    var value = selection.value;
    
    if(type.indexOf("location") >= 0)
    {
        ws.send("CreateLocation:" + String(message[1]) + ":" + String(value));
    }
    emptyRefresh();
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
    
    emptyRefresh();
}

function submit_solenoid(x, selection, mapping)
{
    var message = x.id.split(":");
    var value = selection.value;
    var all_selects = getSelectValues(mapping);
    
    ws.send("CreateSolenoid:" + String(message[1]) + ":" + String(value) + ":" + all_selects);
    emptyRefresh();
}

function do_location(x)
{
    var message = x.id.split(":");
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    var state = "location:" + String(message[1]);
    sessionStorage.setItem('state', state);
    emptyRefresh();
}

function create_location(memory)
{
    var message = memory.split(":");
    var x = document.getElementById("greenhouse:" + String(message[1]))
    x.onmouseover = function() {};
    x.onmouseout = function() {};
    x.onclick = function() {};
    
    var div_contain = document.createElement("div");
    div_contain.id = "wrapper" + String(message[1]);
    div_contain.className = "span12";
    div_contain.style = "padding-left:12px; padding-right:12px;";
    
    var warn_msg = document.createElement("label");
    warn_msg.id = "warn_msg";
    warn_msg.innerHTML = "Select location type:";
    var selection = document.createElement("select");
    selection.className = "selectpicker";
    selection.id = "selection" + String(message[1]);
    selection.className = "form-control";
    
    var pot = document.createElement("option");
    pot.value = "pot";
    pot.innerHTML = "Soil Based";
    selection.appendChild(pot);
    var hydro = document.createElement("option");
    hydro.value = "hydroponic";
    hydro.innerHTML = "Hydroponic";
    selection.appendChild(hydro);
    
    var proceed_btn = document.createElement("button");
    proceed_btn.id = "proceed_btn";
    proceed_btn.innerHTML = "Submit";
    proceed_btn.className = "btn btn-success";
    proceed_btn.onclick = function() {submit_fnc(x, selection, "location")};
    var cancel_btn = document.createElement("button");
    cancel_btn.id = "cancel_btn";
    cancel_btn.innerHTML = "Nevermind";
    cancel_btn.className = "btn btn-primary";
    cancel_btn.onclick = function() {cancel_fnc(x)};
    var button_group = document.createElement("div");
    button_group.id = "warn_btn";
    button_group.className = "form-group";
    button_group.style = "padding-top:12px;"
    button_group.appendChild(proceed_btn);
    button_group.appendChild(cancel_btn);
    
    x.appendChild(div_contain);
    div_contain.appendChild(warn_msg);
    div_contain.appendChild(selection);
    div_contain.appendChild(button_group);
}

function do_relay(x) 
{
    var message = x.id.split(":");
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    
    var warn_msg = document.createElement("h5");
    warn_msg.id = "warn_msg";
    warn_msg.innerHTML = "Turn on the connected raspberry pi and input this server's IP address: 192.168.1.100. Then follow the prompts to complete setup.";
    div_contain.appendChild(warn_msg);
    ws.send("SetupPi:" + String(message[1]));
    
    window.location.reload();
}

function do_solenoid(x)
{
    var message = x.id.split(":");
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    var state = "solenoid:" + String(message[1]);
    sessionStorage.setItem('state', state)
    emptyRefresh();
}

function create_solenoid(memory)
{
    var message = memory.split(":");
    var x = document.getElementById("greenhouse:" + String(message[1]))
    x.onmouseover = function() {};
    x.onmouseout = function() {};
    x.onclick = function() {};
    
    var div_contain = document.createElement("div");
    div_contain.id = "wrapper" + String(message[1]);
    div_contain.className = "span12";
    div_contain.style = "padding-left:12px; padding-right:12px;";
    
    var warn_msg = document.createElement("label");
    warn_msg.id = "warn_msg";
    warn_msg.innerHTML = "Select solenoid type:";
    var selection = document.createElement("select");
    selection.className = "selectpicker";
    selection.id = "selection" + String(message[1]);
    selection.className = "form-control";
    
    var pot = document.createElement("option");
    pot.value = "drip";
    pot.innerHTML = "Drip";
    selection.appendChild(pot);
    var pot2 = document.createElement("option");
    pot2.value = "mainDrip";
    pot2.innerHTML = "Main Drip";
    selection.appendChild(pot2);
    var hydro = document.createElement("option");
    hydro.value = "hydroponic";
    hydro.innerHTML = "Hydroponic";
    selection.appendChild(hydro);
    
    // Make option for every existing relay
    var map_msg = document.createElement("label");
    map_msg.id = "warn_msg";
    map_msg.innerHTML = "Assign to a location";
    var mapping = document.createElement("select");
    mapping.className = "selectpicker";
    mapping.id = "selection" + String(message[1]);
    mapping.multiple = true;
    mapping.className = "form-control";
    
    // Make option for every existing location
    // Select multiple locations with ctrl + click
    var places = locations.split(':');
    var j = 0;
    var current_greenhouse = false;
    for(j = 0; j < places.length; j++)
    {
        if(places[j] == "greenhouse" + String(message[1]))
        {
            current_greenhouse = true;
        }
        else if(places[j].indexOf("greenhouse") >= 0)
        {
            current_greenhouse = false;
        }
        else if(current_greenhouse)
        {
            var opt = document.createElement("option");
            opt.value = String(places[j]);
            opt.innerHTML = "Loc: " + String(places[j]);
            mapping.appendChild(opt);
        }
    }
    
    var proceed_btn = document.createElement("button");
    proceed_btn.id = "proceed_btn";
    proceed_btn.innerHTML = "Submit";
    proceed_btn.className = "btn btn-success";
    proceed_btn.onclick = function() {submit_solenoid(x, selection, mapping)};
    var cancel_btn = document.createElement("button");
    cancel_btn.id = "cancel_btn";
    cancel_btn.innerHTML = "Nevermind";
    cancel_btn.className = "btn btn-primary";
    cancel_btn.onclick = function() {cancel_fnc(x)};
    var button_group = document.createElement("div");
    button_group.id = "warn_btn";
    button_group.className = "form-group";
    button_group.style = "padding-top:12px;";
    button_group.appendChild(proceed_btn);
    button_group.appendChild(cancel_btn);
    
    x.appendChild(div_contain);
    div_contain.appendChild(warn_msg);
    div_contain.appendChild(selection);
    div_contain.appendChild(map_msg);
    div_contain.appendChild(mapping);
    div_contain.appendChild(button_group);
}

function do_vent(x) 
{
    var message = x.id.split(":");
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    var state = "vent:" + String(message[1]);
    sessionStorage.setItem('state', state);
    emptyRefresh();
}

function create_vent(memory)
{
    var message = memory.split(":");
    ws.send("CreateVent:" + String(message[1]));
    emptyRefresh();
}

function do_light(x) 
{
    var message = x.id.split(":");
    
    var div_contain = document.getElementById("wrapper" + String(message[1]));
    while (div_contain.hasChildNodes()) {
        div_contain.removeChild(div_contain.firstChild);
    }
    var state = "light:" + String(message[1]);
    sessionStorage.setItem('state', state);
    emptyRefresh();
}

function create_light(memory)
{
    var message = memory.split(":");
    ws.send("CreateLight:" + String(message[1]));
    emptyRefresh();
}

function show_success(data)
{
    var message = data.split(":");
    var wrapper = document.getElementById("message-title");
    var warn_msg = document.createElement("h5");
    warn_msg.id = "warn_msg";
    
    if(message[1] == 'relay')
        warn_msg.innerHTML = "Successfully added a relay with " + String(message[2]) + " channels";
    else
        warn_msg.innerHTML = "Success!";
    wrapper.appendChild(warn_msg);
}

function make_warning(data)
{
    var message = data.split(":");
    
    var wrapper = document.getElementById("message-title");
    var warn_msg = document.createElement("h5");
    warn_msg.id = "warn_msg";
    
    if(data.indexOf("location") >= 0)
        warn_msg.innerHTML = "Please label the new " + String(message[2]) + ", its id is " + String(message[3]) + ".";
    else
        warn_msg.innerHTML = String(message[1]);

    wrapper.appendChild(warn_msg);
}

function explain(data)
{
    var message = data.split(":");
    var wrapper = document.getElementById("greenhouse:" + message[0]);
    
    var warn_msg = document.createElement("h5");
    warn_msg.id = "greenhouse" + message[0] + "note";
    warn_msg.className = "text-danger";
    
    warn_msg.innerHTML = message[1];

    wrapper.appendChild(warn_msg);
}

function getSelectValues(selector) 
{
    var result = '';
    var options = selector && selector.options;
    var opt;
    
    var first = true;
    for (var i=0; i<options.length; i++) 
    {
        opt = options[i];
        if (opt.selected) 
        {
            if (first)
            {
                result = result + opt.value;
                first = false;
            }
            else
            {
                result = result + ":" + opt.value;
            }
        }
    }
    return result;
}