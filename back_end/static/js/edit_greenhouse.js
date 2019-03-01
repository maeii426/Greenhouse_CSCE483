/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File: ./static/js/overview_screen.js                                      */
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

function enablePopovers()
{
$(document).ready(function(){
    $('[data-toggle="popover"]').popover(); 
});

$('[data-toggle="popover"]').popover({
    container: 'body'
});
}

// Schedule functions to run when the page loads
addLoadEvent(updateFooterDate);
addLoadEvent(enablePopovers);

/* ------------------------------------------------------------------------- */
/* Initial Variable Declarations                                             */
/* ------------------------------------------------------------------------- */

var host_parser = document.createElement('a');
host_parser.href = window.location.href;
var host_addr = host_parser.host;
var host_name = host_parser.search;
var username = host_name.replace("?", "").replace("%20", " ");


/* ------------------------------------------------------------------------- */
/* Global Greenhouse Variables                                               */
/* ------------------------------------------------------------------------- */

var greenhouse_list = [];

/* ------------------------------------------------------------------------- */
/* Websocket Communication                                                   */
/* ------------------------------------------------------------------------- */

var socket_addr = "ws://" + host_addr + "/ws_edit_greenhouse";
var ws = new WebSocket(socket_addr);

ws.onopen = function()
{  
    ws.send("HasGreenhouses:" + String(username));
};

ws.onmessage = function(received_message)
{
    ws.send("Got a message: " + String(received_message.data));
    
    // If you get here, then you should set up the 
    if(received_message.data.indexOf("UserHasGreenhouses") >= 0)
    {
        var message = received_message.data.split(":");
        
        var i = 0;
        for(i = 1; i<message.length; i++)
        {
            greenhouse_list.push(new Greenhouse(message[i]));
            ws.send("SendInitialConfiguration:" + String(message[i]));
            AddGreenhouse(message[i]);
        }
    }
    else if(received_message.data == "UserHasNoGreenhouses")
    {
        // Load the help page
        
        
    }
    // This is the server sending the user's current initial configuration
    else if(received_message.data.indexOf("IC") >= 0)
    {
        var initial_type = received_message.data.split(":")[1];
        
        if(initial_type == "Relay")
        {
            var message_array = received_message.data.split(":");
            var relay_id = message_array[2];
            var pi_ip = message_array[3];
            var port_number = message_array[4];
            var number_of_channels = message_array[5];
            var greenhouse_id = message_array[6];
            
            // Find what greenhouse this relay will eventually belong to
            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouse_id)
                {
                    break;
                }
            }

            var relay = new Relay(relay_id, pi_ip, port_number, 
                number_of_channels, greenhouse_id);
            
            greenhouse_list[i].addRelay(relay);
            
            AddRelay(greenhouse_id, relay_id);
        }
        else if(initial_type == "Solenoid")
        {
            var message_array = received_message.data.split(":");
            var actuatorId = message_array[2];
            var solenoidType = message_array[3];
            var relayId = message_array[4];
            var channelId = message_array[5];
            var greenhouseId = message_array[6];
            
            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouseId)
                {
                    break;
                }
            }
            
            var solenoid = new Solenoid(actuatorId, solenoidType, relayId,
                channelId, greenhouseId);
        
            greenhouse_list[i].addSolenoid(solenoid);
            
            AddSolenoid(greenhouseId, actuatorId);
        }
        else if(initial_type == "Light")
        {
            var message_array = received_message.data.split(":");
            var actuatorId = message_array[2];
            var relayId = message_array[3];
            var channelId = message_array[4];
            var greenhouseId = message_array[5];
            var state = message_array[6];

            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouseId)
                {
                    break;
                }
            }
            
            var light = new Light(actuatorId, relayId, channelId, greenhouseId, state);
            
            greenhouse_list[i].addLight(light);
            
            AddLight(greenhouseId, actuatorId);
        }
        else if(initial_type == "Ventilation")
        {
            var message_array = received_message.data.split(":");
            var actuatorId = message_array[2];
            var relayId = message_array[3];
            var channelId = message_array[4];
            var greenhouseId = message_array[5];
            
            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouseId)
                {
                    break;
                }
            }
            
            var ventilation = new Ventilation(actuatorId, relayId, channelId, greenhouseId);
            
            greenhouse_list[i].addVentilation(ventilation);
            
            AddVentilation(greenhouseId, actuatorId);
            
        }
        else if(initial_type == "Soil")
        {
            var message_array = received_message.data.split(":");
            var sensorId = message_array[2];
            var locationId = message_array[3];
            var greenhouseId = message_array[4];

            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouseId)
                {
                    break;
                }
            }
           
            var soil = new SoilSensor(sensorId, locationId, greenhouseId);
            
            greenhouse_list[i].addSoil(soil);
            
            AddSoilSensor(greenhouseId, sensorId);
        }
        else if(initial_type == "Location")
        {
            var message_array = received_message.data.split(":");
            var locationType = message_array[2];
            var locationId = message_array[3];
            var greenhouseId = message_array[4];
            
            var i = 0;
            for(i = 0; i<greenhouse_list.length; i++)
            {
                if(greenhouse_list[i]._greenhouseId == greenhouseId)
                {
                    break;
                }
            }
            
            var location = new Location(locationType, locationId, greenhouseId);
            
            greenhouse_list[i].addLocation(location);
            
            AddLocation(greenhouseId, locationId);
        }
    }

};

ws.onclose = function()
{  };


/* ------------------------------------------------------------------------- */
/* Acting Functions                                                          */
/* ------------------------------------------------------------------------- */

// These functions are called when one of the updating buttons are pressed
// They send messages to the server indicating the changes that need to be made to
// the current state of the greenhouse.  

function UpdateRelay(to_update)
{
    document.write("IMPLEMENT UPDATE RELAY!!!!!!!!!");
}

function DeleteRelay(relay_id, greenhouse_id)
{
    ws.send("Delete:" + String(relay_id) + ":" + String(greenhouse_id));
    document.write("Delete:" + String(relay_id) + ":" + String(greenhouse_id));
    document.write("IMPLEMENT DELETE RELAY FUNCTION!!!   " + String(to_delete) + "\n");
    document.write("Need to:\n");
    document.write("  - Send mesage to server\n");
    document.write("  - Server needs to delete the relay from the database.\n");
    document.write("  - Also needs to update all associated solenoids and lights to indicate that they are now unconnected\n");
}

function UpdateSolenoid(to_update)
{
    var new_relay_id = document.getElementById("solenoid-update-relay-" + String(to_update)).value;
    var new_channel_id = document.getElementById("solenoid-update-channel-" + String(to_update)).value;
    
    document.write("IMPLEMENT UPDATE SOLENOID: " + String(new_relay_id) + "  " + String(new_channel_id)) + "!!!!!!!";
    
}

function DeleteSolenoid(to_delete)
{
    ws.send("Delete:" + String(solenoid_id) + ":" + String(greenhouse_id));
    document.write("IMPLEMENT DELETE SOLENOID FUNCTION!!!   " + String(to_delete) + "\n");
    document.write("Need to:\n");
    document.write("  - Send mesage to server\n");
    document.write("  - Server needs to delete the relay from the database.\n");
    document.write("  - Also needs to update all associated solenoids and lights to indicate that they are now unconnected\n");    
}

function UpdateLight(to_delete)
{
    
}

function DeleteLight(to_delete)
{
    document.write("IMPLEMENT DELETE LIGHT FUNCTION!!! " + String(to_delete));
}


/* ------------------------------------------------------------------------- */
/* Miscallaneous Functions                                                   */
/* ------------------------------------------------------------------------- */

function AddGreenhouse(greenhouse_id)
{
    // Get the place where all of the panels will be stored
    document.getElementById("main-panel");
    
    var new_panel = document.createElement("div");
    new_panel.className = "panel panel-default";
    new_panel.id = "main-panel-greenhouse-" + String(greenhouse_id);

    new_panel.innerHTML = "<div class=\"panel-heading collapsed\" data-toggle=\"collapse\" data-parent=\"#main-panel-greenhouse-" + String(greenhouse_id)
        + "\" data-target=\"#collapse-" + String(greenhouse_id) + "\">"
        + "<h4 class=\"panel-title\">"
        + "<span class=\"glyphicon glyphicon-menu-down pull-right\"></span>"
        + "<a class=\"accordion-toggle\">"
        + "Greenhouse #" + String(greenhouse_id)
        + "</a>"
        + "</h4>"
        + "</div>";

    var collapsable_panel = document.createElement("div");
    collapsable_panel.id = "collapse-" + String(greenhouse_id);
    collapsable_panel.className = "panel-collapse collapse";
    
    var panel_body = document.createElement("div");
    panel_body.id = "panel-body-" + greenhouse_id;
    panel_body.className = "panel-body";
    
    collapsable_panel.appendChild(panel_body);
    
    /* --------------------------------------------------------------------- */
    /* Relays                                                                */
    /* --------------------------------------------------------------------- */
    
    var relay_row = document.createElement("div");
    relay_row.id = "relay-row-" + String(greenhouse_id);
    
    panel_body.appendChild(relay_row);
    
    // Setup the relay row with a nice title
    var relay_title = document.createElement("div");
    relay_title.id = "relay-title-" + String(greenhouse_id);
    relay_title.className = "row col-md-12";
    
    var relay_title_message = document.createElement("h3");
    relay_title_message.id = "relay-title-message-" + String(greenhouse_id);
    relay_title_message.innerHTML = "Connected Relays:";
    relay_title.appendChild(relay_title_message);
    
    // Add the relay title into the relay row
    relay_row.appendChild(relay_title);
    
    // Add a holder for the rest of the relays in the greenhouse
    var relay_outside = document.createElement("div");
    relay_outside.id = "relay-container-div-" + String(greenhouse_id);
    
    relay_row.appendChild(relay_outside);

    // Add the whole panel in on the main collapsable part
    new_panel.appendChild(collapsable_panel);

    /* --------------------------------------------------------------------- */
    /* Solenoids                                                             */
    /* --------------------------------------------------------------------- */

    // Create the master solenoid container.  
    var solenoid_row = document.createElement("div");
    solenoid_row.id = "solenoid-row-" + String(greenhouse_id);
    
    panel_body.appendChild(solenoid_row);
    
    // Setup the solenoid row with a nice title
    var solenoid_title = document.createElement("div");
    solenoid_title.id = "solenoid-title-" + String(greenhouse_id);
    solenoid_title.className = "row col-md-12";
    
    var solenoid_title_message = document.createElement("h3");
    solenoid_title_message.id = "solenoid-title-message-" + String(greenhouse_id);
    solenoid_title_message.innerHTML = "Connected Solenoids: ";
    solenoid_title.appendChild(solenoid_title_message);
    
    // Add the solenoid title to the solenoid row
    solenoid_row.appendChild(solenoid_title);
    
    // Add a holder for the rest of the solenoids in the greenhouse
    var solenoid_outside = document.createElement("div");
    solenoid_outside.id = "solenoid-container-div-" + String(greenhouse_id);
    
    solenoid_row.appendChild(solenoid_outside);
    
    /* --------------------------------------------------------------------- */
    /* Lights                                                                */
    /* --------------------------------------------------------------------- */
    
    var light_row = document.createElement("div");
    light_row.id = "light-row-" + String(greenhouse_id);
    
    panel_body.appendChild(light_row);
    
    // Setup the light row with a nice title
    var light_title = document.createElement("div");
    light_title.id = "light-title-" + String(greenhouse_id);
    light_title.className = "row col-md-12";
    
    var light_title_message = document.createElement("h3");
    light_title_message.id = "light-title-message-" + String(greenhouse_id);
    light_title_message.innerHTML = "Connected Lights: ";
    light_title.appendChild(light_title_message);
    
    // Add the light title to the light row
    light_row.appendChild(light_title);
    
    // Add a holder for the rest of the lights in the greenhouse
    var light_outside = document.createElement("div");
    light_outside.id = "light-container-div-" + String(greenhouse_id);
    
    light_row.appendChild(light_outside);
    
    /* --------------------------------------------------------------------- */
    /* Ventilation Systems                                                   */
    /* --------------------------------------------------------------------- */
    
    var ventilation_row = document.createElement("div");
    
    panel_body.appendChild(ventilation_row);
    
    // Setup the ventilation row with a nice title
    var ventilation_title = document.createElement("div");
    ventilation_title.id = "ventilation-title-" + String(greenhouse_id);
    ventilation_title.className = "row col-md-12";
    
    var ventilation_title_message = document.createElement("h3");
    ventilation_title_message.id = "ventilation-title-message-" + String(greenhouse_id);
    ventilation_title_message.innerHTML = "Connected Ventilation Systems: ";
    ventilation_title.appendChild(ventilation_title_message);
    
    // Add the ventilation title to the ventilation row
    ventilation_row.appendChild(ventilation_title);
    
    // Add a holder for the rest of the ventilation systems in the greenhouse
    var ventilation_outside = document.createElement("div");
    ventilation_outside.id = "ventilation-container-div-" + String(greenhouse_id);
    
    ventilation_row.appendChild(ventilation_outside);
    
    /* --------------------------------------------------------------------- */
    /* Soil Sensors                                                          */
    /* --------------------------------------------------------------------- */
    
    var soil_row = document.createElement("div");
    
    panel_body.appendChild(soil_row);
    
    // Setup the soil row with a nice title
    var soil_title = document.createElement("div");
    soil_title.id = "soil-title-" + String(greenhouse_id);
    soil_title.className = "row col-md-12";
    
    var soil_title_message = document.createElement("h3");
    soil_title_message.id = "soil-title-message-" + String(greenhouse_id);
    soil_title_message.innerHTML = "Connected Soil Moisture Sensors: ";
    soil_title.appendChild(soil_title_message);
    
    // Add the soil title to the soil row
    soil_row.appendChild(soil_title);
    
    // Add a holder for the rest of the soil systems in the greenhouse
    var soil_outside = document.createElement("div");
    soil_outside.id = "soil-container-div-" + String(greenhouse_id);
    
    soil_row.appendChild(soil_outside);
    
    /* --------------------------------------------------------------------- */
    /* Locations                                                             */
    /* --------------------------------------------------------------------- */
    
    var location_row = document.createElement("div");
    
    panel_body.appendChild(location_row);
    
    // Setup the location row with a nice title
    var location_title = document.createElement("div");
    location_title.id = "location-title-" + String(greenhouse_id);
    location_title.className = "row col-md-12";
    
    var location_title_message = document.createElement("h3");
    location_title_message.id = "location-title-message-" + String(greenhouse_id);
    location_title_message.innerHTML = "Connected Locations: ";
    location_title.appendChild(location_title_message);
    
    // Add the location title to the location row
    location_row.appendChild(location_title);
    
    // Add a holder for the rest of the locations in the greenhouse
    var location_outside = document.createElement("div");
    location_outside.id = "location-container-div-" + String(greenhouse_id);
    
    location_row.appendChild(location_outside);
    
    /* --------------------------------------------------------------------- */
    /* ph Sensors                                                            */
    /* --------------------------------------------------------------------- */    
    
    var ph_row = document.createElement("div");
    
    panel_body.appendChild(ph_row);
    
    // Setup the ph row with a nice title
    var ph_title = document.createElement("div");
    ph_title.id = "ph-title-" + String(greenhouse_id);
    ph_title.className = "row col-md-12";
    
    var ph_title_message = document.createElement("h3");
    ph_title_message.id = "ph-title-message-" + String(greenhouse_id);
    ph_title_message.innerHTML = "Connected pH Sensors: ";
    ph_title.appendChild(ph_title_message);
    
    // Add the ph title to the ph row
    ph_row.appendChild(ph_title);
    
    // Add a holder for the rest of the locations in the greenhouse
    var ph_outside = document.createElement("div");
    ph_outside.id = "ph-container-div-" + String(greenhouse_id);
    
    ph_row.appendChild(ph_outside);

    /* --------------------------------------------------------------------- */
    /* waterLevel Sensors                                                    */
    /* --------------------------------------------------------------------- */ 
    
    var water_level_row = document.createElement("div");
    
    panel_body.appendChild(water_level_row);
    
    // Setup the water level row with a nice title
    var water_level_title = document.createElement("div");
    water_level_title.id = "water-level-title-" + String(greenhouse_id);
    water_level_title.className = "row col-md-12";
    
    var water_level_title_message = document.createElement("h3");
    water_level_title_message.id = "water-level-title-message-" + String(greenhouse_id);
    water_level_title_message.innerHTML = "Connected Water Level Sensors: ";
    water_level_title.appendChild(water_level_title_message);
    
    // Add the water level title to the water level row
    water_level_row.appendChild(water_level_title);
    
    // Add a holder for the rest of the water level sensors in the greenhouse
    var water_level_outside = document.createElement("div");
    water_level_outside.id = "water-level-container-div-" + String(greenhouse_id);
    
    water_level_row.appendChild(water_level_outside);
    
    /* --------------------------------------------------------------------- */
    /* waterTemp Sensors                                                     */
    /* --------------------------------------------------------------------- */ 
    
    var water_temp_row = document.createElement("div");
    
    panel_body.appendChild(water_temp_row);
    
    // Setup the water temp row with a nice title
    var water_temp_title = document.createElement("div");
    water_temp_title.id = "water-temp-title-" + String(greenhouse_id);
    water_temp_title.className = "row col-md-12";
    
    var water_temp_title_message = document.createElement("h3");
    water_temp_title_message.id = "water-temp-title-message-" + String(greenhouse_id);
    water_temp_title_message.innerHTML = "Connected Water Temp Sensors: ";
    water_temp_title.appendChild(water_temp_title_message);
    
    // Add the water temp title to the water temp row
    water_temp_row.appendChild(water_temp_title);
    
    // Add a holder for the rest of the water temp sensors in the greenhouse
    var water_temp_outside = document.createElement("div");
    water_temp_outside.id = "water-temp-container-div-" + String(greenhouse_id);
    
    water_temp_row.appendChild(water_temp_outside);
    
    /* --------------------------------------------------------------------- */
    /* airHumidity Sensors                                                   */
    /* --------------------------------------------------------------------- */    
    
    var air_humidity_row = document.createElement("div");
    
    panel_body.appendChild(air_humidity_row);
    
    // Setup the air humidity row with a nice title
    var air_humidity_title = document.createElement("div");
    air_humidity_title.id = "air-humidity-title-" + String(greenhouse_id);
    air_humidity_title.className = "row col-md-12";
    
    var air_humidity_title_message = document.createElement("h3");
    air_humidity_title_message.id = "air-humidity-title-message-" + String(greenhouse_id);
    air_humidity_title_message.innerHTML = "Connected Air Humidity Sensors: ";
    air_humidity_title.appendChild(air_humidity_title_message);
    
    // Add the air humidity title to the air humidity row
    air_humidity_row.appendChild(air_humidity_title);
    
    // Add a holder for the rest of the air humidity sensors in the greenhouse
    var air_humidity_outside = document.createElement("div");
    air_humidity_outside.id = "air-humidity-container-div-" + String(greenhouse_id);
    
    air_humidity_row.appendChild(air_humidity_outside);
    
    /* --------------------------------------------------------------------- */
    /* airTemp Sensors                                                       */
    /* --------------------------------------------------------------------- */
   
    var air_temp_row = document.createElement("div");
    
    panel_body.appendChild(air_temp_row);
    
    // Setup the air temp row with a nice title
    var air_temp_title = document.createElement("div");
    air_temp_title.id = "air-temp-title-" + String(greenhouse_id);
    air_temp_title.className = "row col-md-12";
    
    var air_temp_title_message = document.createElement("h3");
    air_temp_title_message.id = "air-temp-title-message-" + String(greenhouse_id);
    air_temp_title_message.innerHTML = "Connected Air Temperature Sensors: ";
    air_temp_title.appendChild(air_temp_title_message);
    
    // Add the air temp title to the air temp row
    air_temp_row.appendChild(air_temp_title);
    
    // Add a holder for the rest of the air temp sensors in the greenhouse
    var air_temp_outside = document.createElement("div");
    air_temp_outside.id = "air-temp-container-div-" + String(greenhouse_id);
    
    air_temp_row.appendChild(air_temp_outside);
    
    // Get the parent where I'm appending the datab onto
    var greenhouse_parent = document.getElementById("main-panel");    
    
    // Finally add the greenhouse panel onto the webpage
    greenhouse_parent.appendChild(new_panel);
}

function AddRelay(greenhouse_id, relay_id)
{
    // <div class = "row">
    //     <div class = "col-md-12">
    //         <h4>Relay #<relay name></h4>
    //     </div>
    //     <div class = "col-md-12">
    //         
    //
    //     </div>
    // </div>
    
    
    // Get the parent element that the relay will be appended on to
    var parent = document.getElementById("relay-container-div-" + String(greenhouse_id));
    
    // Create the element that will contain the relay
    var relay_row = document.createElement("div");
    relay_row.className = "row";
    relay_row.id = "relay-" + String(greenhouse_id) + "-" + String(relay_id);
    
    var relay_title = document.createElement("div");
    relay_title.className = "col-md-12";
    relay_title.innerHTML = "<h4 style='padding-left:0%;'>Relay #" + String(relay_id) + "</h4>";
    
    relay_row.appendChild(relay_title);
    
    // Figure out how many channels this relay has.  
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    var relay = greenhouse_list[i].getRelayById(relay_id);
    
    // Add some statistics about the relay to the relay screen
    var stats_row = document.createElement("div");
    stats_row.id = "relay-stats-row-" + String(relay_id);
    stats_row.className = "row";
    
    var stats_container = document.createElement("div");
    stats_container.id = "relay-stats-container-" + String(relay_id);
    stats_container.className = "col-md-11";
    
    
    var connected_ip = relay.getPiId();
    var connected_port = relay.getPortNumber();
    var num_channels = relay.getNumberOfChannels();

    var ip_par = document.createElement("p");
    var channel_par = document.createElement("p");
    
    ip_par.innerHTML = "&nbsp;&nbsp- Connected to: " + String(connected_ip) + ":" + String(connected_port);
    ip_par.style = "padding-left:1%";
    channel_par.innerHTML = "&nbsp;&nbsp;- Number of Channels: " + String(num_channels);
    channel_par.style = "padding-left:1%;";
    
    stats_container.appendChild(ip_par);
    stats_container.appendChild(channel_par);
    
    var delete_relay_row = document.createElement("div");
    delete_relay_row.className = "col-md-1";
    
    var delete_relay_button = document.createElement("div");
    
    delete_relay_button.innerHTML = "<button type=\"button\" class=\"btn btn-danger\" id=\"relay-delete-button-"
        + String(relay_id) + "\" data-toggle=\"popover\" data-placement=\"auto bottom\" title=\"<b>Are you sure?</b>\" data-html=\"true\" data-content=\""
        + "<div class='text-center'><button type='button' class='btn btn-danger' onclick='DeleteRelay(" + String(relay_id) + "," + String(greenhouse_id) + ")'>Yes</button></div>"
        + "\">Delete Relay</button>";
    
    delete_relay_row.appendChild(delete_relay_button);
    
    stats_row.appendChild(stats_container);
    stats_row.appendChild(delete_relay_row);
    relay_row.appendChild(stats_row);
    
    // Now, add boxes for each of the individual channels of the relay
    var channel_row = document.createElement("div");
    channel_row.className = "row";
    channel_row.id = "relay-channels-row-" + String(relay_id);

    var spacer_div = document.createElement("div");
    spacer_div.className = "col-md-1";
    
    channel_row.appendChild(spacer_div);
    

    for(i = 0; i<relay._numberOfChannels; i++)
    {
        var channel_div = document.createElement("div");
        channel_div.id = "relay-channel-" + String(relay_id) + "-" + String(i);
        channel_div.className = "col-md-1";
        
        var channel_div_well = document.createElement("div");
        channel_div_well.id = "relay-channel-well-" + String(relay_id) + "-" + String(i);
        channel_div_well.className = "well";
        //channel_div_well.innerHTML ="<h4 class='text-success' style='text-align:center;'>Channel</h4>"
        
        // Title div
        var title_div = document.createElement("div");
        title_div.innerHTML = "<b>Channel #" + String(i + 1) + "</b>";
        
        // Add a row to the div to contain information
        var channel_div_data_row = document.createElement("div");
        channel_div_data_row.id = "channel-div-data-row-" + String(relay_id) + "-" + String(i);
    
        var channel_par_data_row_connected = document.createElement("p");
        channel_par_data_row_connected.id = "channel-par-data-row-connected-" + String(relay_id) + "-" + String(i);
        channel_par_data_row_connected.innerHTML = "<h6>Conn: <br>" + String(relay.getConnectedItems(i)) + "</h6>";
        
        var channel_par_data_row_status = document.createElement("p");
        channel_par_data_row_status.id = "channel-par-data-row-status-" + String(relay_id) + "-" + String(i);
        channel_par_data_row_status.innerHTML = "<h6>Status: <br>" + String(relay.getCurrentState(i)) + "</h6>";
        
        channel_div_data_row.appendChild(channel_par_data_row_connected);
        channel_div_data_row.appendChild(channel_par_data_row_status);
        
        
        // Add a button to have users update the relay channel
        var channel_div_button_row = document.createElement("div");             
        channel_div_button_row.id = "channel-div-button-row-" + String(relay_id) + "-" + String(i);
        
        channel_div_button_row.innerHTML = "<button type=\"button\""
            + "class=\"btn btn-primary btn-sm\" id=\"channel-div-button-" + String(relay_id) + "-" + String(i) + "\"" 
            + "onclick=\"document.write('IMPLEMENT UPDATE RELAY CHANNEl!!!');\"><h6>Update</h6></button>";

        // Add the insides of the well into the well
        channel_div_well.appendChild(title_div);
        channel_div_well.appendChild(channel_div_data_row);
        channel_div_well.appendChild(channel_div_button_row);    
        
        // Add the well to the channel div
        channel_div.appendChild(channel_div_well);
        channel_row.appendChild(channel_div);
    }
    
    relay_row.appendChild(channel_row);
    
    parent.appendChild(relay_row);
}

function AddSolenoid(greenhouse_id, solenoid_id)
{
    var parent = document.getElementById("solenoid-container-div-" + String(greenhouse_id));
    
    // Create the element that will contain the solenoid
    var solenoid_row = document.createElement("div");
    solenoid_row.className = "row";
    solenoid_row.id = "solenoid-" + String(greenhouse_id) + "-" + String(solenoid_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className = "col-md-3";
    
    var solenoid_well = document.createElement("div");
    solenoid_well.className = "well";
    
    middle_div.appendChild(solenoid_well);
    
    solenoid_row.appendChild(left_div);
    solenoid_row.appendChild(middle_div);
    solenoid_row.appendChild(right_div);
    
    // Grab the solenoid object from the greenhouse
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    var solenoid_object = greenhouse_list[i].getSolenoidById(solenoid_id);
    
    // Add some things inside of the solenoid well
    var well_row = document.createElement("div");
    well_row.id = "solenoid-well-" + String(solenoid_id);
    well_row.className = "row";
    
    solenoid_well.appendChild(well_row);
    
    var ldiv_1 = document.createElement("div");
    ldiv_1.className = "col-md-6";
    
    well_row.appendChild(ldiv_1);
    
    var solenoid_well_title = document.createElement("b");
    solenoid_well_title.innerHTML = "Solenoid #" + String(solenoid_id);
    solenoid_well_title.id = "solenoid-well-title-" + String(solenoid_id);
    
    var connected_relay_message = document.createElement("h6");
    connected_relay_message.innerHTML = "  - Connected To Relay #" + String(solenoid_object.getRelayId()) 
        +  "  Channel #" + String(solenoid_object.getChannelId());
    connected_relay_message.id = "solenoid-connected-relay-message-" + String(solenoid_id);
    
    var current_state_message = document.createElement("h6");
    current_state_message.innerHTML = "  - Current State: " + String(solenoid_object.getCurrentState());
    current_state_message.id = "solenoid-current-state-message-" + String(solenoid_id);
    
    
    ldiv_1.appendChild(solenoid_well_title);
    ldiv_1.appendChild(connected_relay_message);
    ldiv_1.appendChild(current_state_message);
    
    var middle_div_1 = document.createElement("div");
    middle_div_1.className = "col-md-2";
    
    well_row.appendChild(middle_div_1);
    
    var rdiv_1 = document.createElement("div");
    rdiv_1.className = "col-md-2";
    
    var rdiv_1_1 = document.createElement("div");
    rdiv_1_1.className = "col-md-2";
    
    var update_button_wrapper = document.createElement("div");
    
    update_button_wrapper.innerHTML = "<button type=\"button\" class=\"btn btn-primary\" id=\"solenoid-update-button-"
        + String(solenoid_id) + "\" data-toggle=\"popover\" title=\"<b>Update Relay Parameters</b>\" data-html=\"true\" data-content=\""
        + "<div class='text-center'><h4>New Relay Id</h4><input type='text' class='form-control' id='solenoid-update-relay-" 
        + String(solenoid_id) + "'><h4>New Channel Id</h4><input type='text' class='form-control' id='solenoid-update-channel-" 
        + String(solenoid_id) + "'><p>&nbsp</p><button type='button' class='btn btn-primary' onclick='UpdateSolenoid(" 
        + String(solenoid_id) + ")'>Submit Changes</button></div>\">Update Solenoid</button>";

    var delete_solenoid_button = document.createElement("div");

    delete_solenoid_button.innerHTML = "<button type=\"button\" class=\"btn btn-danger\" id=\"solenoid-delete-button-"
    + String(solenoid_id) + "\" data-toggle=\"popover\" data-placement=\"auto bottom\" title=\"<b>Are you sure?</b>\" data-html=\"true\" data-content=\""
    + "<div class='text-center'><button type='button' class='btn btn-danger' onclick='DeleteSolenoid(" + String(solenoid_id) +":"+ String(greenhouse_id) + ")'>Yes</button></div>"
    + "\">Delete Relay</button>";

    rdiv_1.appendChild(update_button_wrapper);
    rdiv_1_1.appendChild(delete_solenoid_button);
    
    well_row.appendChild(rdiv_1);
    well_row.appendChild(rdiv_1_1);
    
    parent.appendChild(solenoid_row);
}

function AddLight(greenhouse_id, light_id)
{
    var parent = document.getElementById("light-container-div-" + String(greenhouse_id));
    
    // Create an element that will contain the light
    var light_row = document.createElement("div");
    light_row.className = "row";
    light_row.id = "light-" + String(light_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className = "col-md-3";
    
    var light_well = document.createElement("div");
    light_well.className = "well";
    
    middle_div.appendChild(light_well);
    
    light_row.appendChild(left_div);
    light_row.appendChild(middle_div);
    light_row.appendChild(right_div);
    
    // Grab the solenoid object from the greenhouse
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    var light_object = greenhouse_list[i].getLightById(light_id);
    
    // Add some things inside of the solenoid well
    var well_row = document.createElement("div");
    well_row.id = "light-well-" + String(light_id);
    well_row.className = "row";
    
    light_well.appendChild(well_row);
    
    var ldiv_1 = document.createElement("div");
    ldiv_1.className = "col-md-6";
    
    well_row.appendChild(ldiv_1);
    
    var light_well_title = document.createElement("b");
    light_well_title.innerHTML = "Light #" + String(light_id);
    light_well_title.id = "light-well-title-" + String(light_id);
    
    var connected_relay_message = document.createElement("h6");
    connected_relay_message.innerHTML = "  - Connected To Relay #" + String(light_object.getRelayId())
        + " Channel #" + String(light_object.getChannelId());
    connected_relay_message.id = "light-connected-relay-message-" + String(light_id);
    
    var current_state_message = document.createElement("h6");
    current_state_message.innerHTML = "  - Current State: " + String(light_object.getCurrentState());
    current_state_message.id = "light-current-state-message-" + String(light_id);
    
    ldiv_1.appendChild(light_well_title);
    ldiv_1.appendChild(connected_relay_message);
    ldiv_1.appendChild(current_state_message);
    
    var middle_div_1 = document.createElement("div");
    middle_div_1.className = "col-md-2";
    
    well_row.appendChild(middle_div_1);
    
    var rdiv_1 = document.createElement("div");
    rdiv_1.className = "col-md-2";
    
    var rdiv_1_1 = document.createElement("div");
    rdiv_1_1.className = "col-md-2";
    
    // Update button
    var update_button_wrapper = document.createElement("div");
    
    update_button_wrapper.innerHTML = "<button type=\"button\" class=\"btn btn-primary\" id=\"light-update-button-"
        + String(light_id) + "\" data-toggle=\"popover\" title=\"<b>Update Light Parameters</b>\" data-html=\"true\" data-content=\""
        + "<div class='text-center'><h4>New Relay Id</h4><input type='text' class='form-control' id='light-update-relay-" 
        + String(light_id) + "'><h4>New Channel Id</h4><input type='text' class='form-control' id='light-update-channel-" 
        + String(light_id) + "'><p>&nbsp</p><button type='button' class='btn btn-primary' onclick='UpdateLight(" 
        + String(light_id) + ")'>Submit Changes</button></div>\">Update Light</button>";

    // Delete button
    var delete_light_button = document.createElement("div");

    delete_light_button.innerHTML = "<button type=\"button\" class=\"btn btn-danger\" id=\"light-delete-button-"
    + String(light_id) + "\" data-toggle=\"popover\" data-placement=\"auto bottom\" title=\"<b>Are you sure?</b>\" data-html=\"true\" data-content=\""
    + "<div class='text-center'><button type='button' class='btn btn-danger' onclick='DeleteLight(" + String(light_id) + ")'>Yes</button></div>"
    + "\">Delete Relay</button>";

    rdiv_1.appendChild(update_button_wrapper);
    rdiv_1_1.appendChild(delete_light_button);
    
    well_row.appendChild(rdiv_1);
    well_row.appendChild(rdiv_1_1);
    
    // Add the light row into the list of light objects
    parent.appendChild(light_row);
}

function AddVentilation(greenhouse_id, ventilation_id)
{
    var parent = document.getElementById("ventilation-container-div-" + String(greenhouse_id));
    
    // Create an element that will contain the light
    var ventilation_row = document.createElement("div");
    ventilation_row.className = "row";
    ventilation_row.id = "ventilation-" + String(ventilation_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className= "col-md-3";
    
    var ventilation_well = document.createElement("div");
    ventilation_well.className = "well";
    
    middle_div.appendChild(ventilation_well);
    
    ventilation_row.appendChild(left_div);
    ventilation_row.appendChild(middle_div);
    ventilation_row.appendChild(right_div);
    
    // Grab the ventilation object from the database
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    var ventilation_object = greenhouse_list[i].getVentilationById(ventilation_id);
    
    // Add some things inside of the ventilation well
    var well_row = document.createElement("div");
    well_row.id = "ventilation-well-" + String(ventilation_id);
    well_row.className = "row";
    
    ventilation_well.appendChild(well_row);
    
    var ldiv_1 = document.createElement("div");
    ldiv_1.className = "col-md-6";
    
    well_row.appendChild(ldiv_1);
    
    var ventilation_well_title = document.createElement("b");
    ventilation_well_title.innerHTML = "Fan #" + String(ventilation_id);
    ventilation_well_title.id = "ventilation-well-title-" + String(ventilation_id);
    
    var connected_relay_message = document.createElement("h6");
    connected_relay_message.innerHTML = "  - Connected To Relay #" + String(ventilation_object.getRelayId())
        + " Chanel #" + String(ventilation_object.getChannelId());
    connected_relay_message.id = "ventilation-connected-relay-message-" + String(ventilation_id);
        
    var current_state_message = document.createElement("h6");
    current_state_message.innerHTML = "  - Current State: " + String(ventilation_object.getCurrentState());
    current_state_message.id = "ventilation-current-state-message-" + String(ventilation_id);
    
    ldiv_1.appendChild(ventilation_well_title);
    ldiv_1.appendChild(connected_relay_message);
    ldiv_1.appendChild(current_state_message);
    
    var middle_div_1 = document.createElement("div");
    middle_div_1.className = "col-md-2";
    
    well_row.appendChild(middle_div_1);
    
    var rdiv_1 = document.createElement("div");
    rdiv_1.className = "col-md-2";
    
    var rdiv_1_1 = document.createElement("div");
    rdiv_1_1.className = "col-md-2";
    
    // Update button
    var update_button_wrapper = document.createElement("div");
    
    update_button_wrapper.innerHTML = "<button type=\"button\" class=\"btn btn-primary\" id=\"ventilation-update-button-"
        + String(ventilation_id) + "\" data-toggle=\"popover\" title=\"<b>Update Ventilation Parameters</b>\" data-html=\"true\" data-content=\""
        + "<div class='text-center'><h4>New Relay Id</h4><input type='text' class='form-control' id='ventilation-update-relay-" 
        + String(ventilation_id) + "'><h4>New Channel Id</h4><input type='text' class='form-control' id='ventilation-update-channel-" 
        + String(ventilation_id) + "'><p>&nbsp</p><button type='button' class='btn btn-primary' onclick='UpdateVentilation(" 
        + String(ventilation_id) + ")'>Submit Changes</button></div>\">Update Ventilation</button>";
    
    // Delete button
    var delete_ventilation_button = document.createElement("div");

    delete_ventilation_button.innerHTML = "<button type=\"button\" class=\"btn btn-danger\" id=\"ventilation-delete-button-"
    + String(ventilation_id) + "\" data-toggle=\"popover\" data-placement=\"auto bottom\" title=\"<b>Are you sure?</b>\" data-html=\"true\" data-content=\""
    + "<div class='text-center'><button type='button' class='btn btn-danger' onclick='DeleteVentilation(" + String(ventilation_id) + ")'>Yes</button></div>"
    + "\">Delete Fan</button>";
    
    rdiv_1.appendChild(update_button_wrapper);
    rdiv_1_1.appendChild(delete_ventilation_button);
    
    well_row.appendChild(rdiv_1);
    well_row.appendChild(rdiv_1_1);
    
    // Add the light row into the list of light objects
    parent.appendChild(ventilation_row);

}

function AddSoilSensor(greenhouse_id, soil_id)
{
    var parent = document.getElementById("soil-container-div-" + String(greenhouse_id));

    // Create an element that will contain the soil sensor
    var soil_row = document.createElement("div");
    soil_row.className = "row";
    soil_row.id = "soil-" + String(soil_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className = "col-md-3";
    
    var soil_well = document.createElement("div");
    soil_well.className = "well";
    
    middle_div.appendChild(soil_well);
    
    soil_row.appendChild(left_div);
    soil_row.appendChild(middle_div);
    soil_row.appendChild(right_div);
    
    // Grab the soil sensor object from the database
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }    
 
    var soil_object = greenhouse_list[i].getSoilSensorById(soil_id);
    
    
    // Add some things inside of the ventilation well
    var well_row = document.createElement("div");
    well_row.id = "soil-well-" + String(soil_id);
    well_row.className = "row";
    
    soil_well.appendChild(well_row);
    
    var ldiv_1 = document.createElement("div");
    ldiv_1.className = "col-md-6";
    
    well_row.appendChild(ldiv_1);
    
    var soil_well_title = document.createElement("b");
    soil_well_title.innerHTML = "Soil Sensor #" + String(soil_id);
    soil_well_title.id = "soil-well-title-" + String(soil_id);
    
    var connected_location_message = document.createElement("h6");
    connected_location_message.innerHTML = "  -  Connected to Location #" + String(soil_object.getLocationId());
    
    ldiv_1.appendChild(soil_well_title);
    ldiv_1.appendChild(connected_location_message);
    
    var middle_div_1 = document.createElement("div");
    middle_div_1.className = "col-md-2";
    
    well_row.appendChild(middle_div_1);
    
    var rdiv_1 = document.createElement("div");
    rdiv_1.className = "col-md-2";
    
    var rdiv_1_1 = document.createElement("div");
    rdiv_1_1.className = "col-md-2";
    
    var delete_button = document.createElement("button");
    delete_button.className = "btn btn-danger";
    delete_button.type = "button";
    delete_button.onclick = function(){ document.write('IMPLEMENT DELETE SOIL!!!'); };
    delete_button.innerHTML = "Delete Soil Sensor";
    delete_button.id = "soil-delete-button-" + String(soil_id);
    
    rdiv_1_1.appendChild(delete_button);
    
    well_row.appendChild(rdiv_1);
    well_row.appendChild(rdiv_1_1);
    
    // Add the soil row into the list of light objects
    parent.appendChild(soil_row);
    
}

function AddLocation(greenhouse_id, location_id)
{
    var parent = document.getElementById("location-container-div-" + String(greenhouse_id));
    
    // Create an element that will contain the location 
    var location_row = document.createElement("div");
    location_row.className = "row";
    location_row.id = "location-" + String(location_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className = "col-md-3";
    
    var location_well = document.createElement("div");
    location_well.className = "well";
    
    middle_div.appendChild(location_well);
    
    location_row.appendChild(left_div);
    location_row.appendChild(middle_div);
    location_row.appendChild(right_div);
    
    // Grab the location object from the database
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    var location_object = greenhouse_list[i].getLocationById(location_id);
    
    
    // Add some things inside of the location well
    var well_row = document.createElement("div");
    well_row.id = "location-well-" + String(location_id);
    well_row.className = "row";
    
    location_well.appendChild(well_row);
    
    var ldiv_1 = document.createElement("div");
    ldiv_1.className = "col-md-6";
    
    well_row.appendChild(ldiv_1);

    var location_well_title = document.createElement("b");
    location_well_title.innerHTML = "Location #" + String(location_id);
    location_well_title.id = "location-well-title-" + String(location_id);
    
    var location_type_message = document.createElement("h6");
    location_type_message.innerHTML = "  - Location Type: " + String(location_object.getType());
    
    ldiv_1.appendChild(location_well_title);
    ldiv_1.appendChild(location_type_message);
    
    
    var middle_div_1 = document.createElement("div");
    middle_div_1.className = "col-md-2";
    
    well_row.appendChild(middle_div_1);
    
    var rdiv_1 = document.createElement("div");
    rdiv_1.className = "col-md-2";
    
    var rdiv_1_1 = document.createElement("div");
    rdiv_1_1.className = "col-md-2";
    
    var delete_button = document.createElement("button");
    delete_button.className = "btn btn-danger";
    delete_button.type = "button";
    delete_button.onclick = function(){ document.write("IMPLEMENT DELETE LOCATION!!!") };
    delete_button.innerHTML = "Delete Location";
    delete_button.id = "location-delete-button-" + String(location_id);
    
    rdiv_1_1.appendChild(delete_button);

    well_row.appendChild(rdiv_1);
    well_row.appendChild(rdiv_1_1);

    // Add the location row into the list of light objects
    parent.appendChild(location_row);
}

function AddpHSensor(greenhouse_id, ph_sensor_id)
{
    var parent = document.getElementById("ph-container-div-" + String(greenhouse_id));
    
    // Create an element that will contain the soil sensor
    var ph_row = document.createElement("div");
    ph_row.className = "row";
    ph_row.id = "ph-" + String(ph_sensor_id);
    
    var left_div = document.createElement("div");
    left_div.className = "col-md-1";
    
    var middle_div = document.createElement("div");
    middle_div.className = "col-md-8";
    
    var right_div = document.createElement("div");
    right_div.className = "col-md-3";
    
    var ph_well = document.createElement("div");
    ph_well.className = "well";
    
    middle_div.appendChild(ph_well);
    
    ph_row.appendChild(left_div);
    ph_row.appendChild(middle_div);
    ph_row.appendChild(right_div);
    
    // Grab the ph sensor object from the database
    var i = 0;
    var found = false;
    for(i = 0; i<greenhouse_list.length; i++)
    {
        if(greenhouse_list[i]._greenhouseId == greenhouse_id)
        {
            found = true;
            break;
        }
    }
    
    if(found != true)
    {
        return;
    }
    
    
    // ADD MORE STUFF HERE!!!!!!!
    
    
    
    
}

function AddWaterLevelSensor(greenhouse_id, water_level_id)
{
    
}

function AddWaterTempSensor(greenhouse_id, water_temp_id)
{
    
}

function AddAirHumiditySensor(greenhouse_id, air_humidity_id)
{
    
}

function AddAirTempSensor(greenhouse_id, air_temp_id)
{
    
}