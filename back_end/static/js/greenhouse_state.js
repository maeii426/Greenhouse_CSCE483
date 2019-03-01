/* ------------------------------------------------------------------------- */
/* Developer: Andrew Kirfman                                                 */
/* Project: Smart Greenhouse                                                 */
/*                                                                           */
/* File: ./static/js/overview_screen.js                                      */
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Data Containers                                                           */
/* ------------------------------------------------------------------------- */

class DataItem
{
    constructor(unixTimestamp, value, sensorType, sensorId)
    {
        this._unixTimestamp = unixTimestamp;
        this._value = value;
        this._sensorType = sensorType;
        this._sensorId = sensorId;
    }
    
    /* Getter Functions */
    getUnixTimestamp() { return this._unixTimestamp; }
    getValue()         { return this._value; }
    getSensorType()    { return this._sensorType; }
    getSensorId()      { return this._sensorId; }
}

class Relay
{
    constructor(relayId, piId, portNumber, numberOfChannels, greenhouseId)
    {
        this._relayId = relayId;
        this._piId = piId;
        this._portNumber = portNumber;
        this._numberOfChannels = numberOfChannels;
        this._greenhouseId = greenhouseId;
        
        // I want this to contain a list of all of the channels that are 
        // connected to relay X.
        this._connectedItems = [];
        
        // Should contian the current state of all of the channels of the relay.
        this._currentState = [];
        
        // Initialize the relays as having nothing connected to them.  
        var i = 0;
        for(i = 0; i<numberOfChannels; i++)
        {
            this._connectedItems.push("None");
            this._currentState.push("N/A");
        }
    }
    
    /* Getter Function */
    getRelayId()          { return this._relayId; }
    getPiId()             { return this._piId; }
    getPortNumber()       { return this._portNumber; }
    getNumberOfChannels() { return this._numberOfChannels; }
    
    getConnectedItems(index)
    {
        if(index >= this._numberOfChannels || index < 0)
        {
            return null;
        }
        
        return this._connectedItems[index];
    }
    
    getCurrentState(index)
    {
        if(index >= this._numberOfChannels || index < 0)
        {
            return null;
        }
        
        return this._currentState[index];
    }
    
    /* Setter Functions */
    setConnectedItem(index, new_value)
    {
        document.write("IMPLEMENT SET CONNECTED ITEM IN CLASS RELAY");
    }

    setCurrentState(index, new_value)
    {
        document.write("IMPLEMENT SET CURRENT STATE IN CLASS RELAY!!!");
    }
}

class Solenoid
{
    constructor(actuatorId, type, relayId, channelId, greenhouse_id, state)
    {
        this._actuatorId = actuatorId;
        this._type = type;
        this._relayId = relayId;
        this._channelId = channelId;
        
        // The current state of this solenoid (i.e. open or closed)
        this._currentState = state;
    }

    /* Getter Functions */
    getActuatorId()   { return this._actuatorId; }
    getType()         { return this._type; }
    getRelayId()      { return this._relayId; } 
    getChannelId()    { return this._channelId; }
    getCurrentState() { return this._currentState; }
    
    /* Setter Functions */
    setCurrentState(new_state)
    {
        document.write("IMPLEMENT SET CURRENT STATE IN CLASS SOLENOID!!!");
        this._current_state = new_state;
    }
}

class Light
{
    constructor(actuatorId, relayId, channelId, greenhouse_id, state)
    {
        this._actuatorId = actuatorId;
        this._relayId = relayId;
        this._greenhouseId = greenhouse_id;
        this._channelId = channelId;
    
        // The current state of the light strip
        this._currentState = state;
    }
   
    /* Getter Functions */ 
    getActuatorId()   { return this._actuatorId; }
    getRelayId()      { return this._relayId; }
    getChannelId()    { return this._channelId; }
    getGreenhouseId() { return this._greenhouseId; }
    getCurrentState() { return this._currentState; }
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS LIGHT!!!");
    }
    
    setCurrentState(new_state)
    {
        document.write("IMPLEMENT SET CURRENT STATE IN CLASS LIGHT!!!");
        this._currentState = new_state;
    }
}

class Ventilation
{
    constructor(actuatorId, relayId, channelId, greenhouse_id, state)
    {
        this._actuatorId = actuatorId;
        this._relayId = relayId;
        this._channelId = channelId;
        this._currentState = state;
    }
    
    /* Getter Functions */
    getActuatorId()   { return this._actuatorId; }
    getRelayId()      { return this._relayId; }
    getChannelId()    { return this._channelId; }
    getCurrentState() { return this._currentState; }
    
    /* Setter Functions */
    setRelayId(new_relay)
    {
        document.write("IMPLEMENT SET RELAY ID IN CLASS VENTILATION!!!");
        this._relayId = new_relay;
    }
    
    setChannelId(new_channel)
    {
        document.write("IMPLEMENT SET CHANNEL ID IN CLASS VENTILATION!!!");
        this._channelId = new_channel;
    }
}

class SoilSensor
{
    constructor(sensorId, locationId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._locationId = locationId;
        this._greenhouseId = greenhouseId;
        this._currentState = "Unknown";
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId; }
    getLocationId()   { return this._locationId; }
    getGreenhouseId() { return this._greenhouseId; }
    getCurrentState() { return this._currentState; }
    
    /* Setter Functions */
    setLocationId(new_location)
    {
        document.write("IMPLEMENT SET LOCATION ID IN CLASS SOIL SENSOR!!!");
        this._locationId = new_location;
    }
    
    setGreenhouseId(new_greenhouse)
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS SOIL SENSOR!!!");
        this._greenhouseId = new_greenhouse;
    }
}

class Location
{
    constructor(type, locationId)
    {
        this._type = type;
        this._locationId = locationId;
    }
    
    /* Getter Function */
    getType()       { return this._type; }
    getLocationId() { return this._locationId; }
    
    /* Setter Functions */
    setType(new_type)
    {
        document.write("IMPLEMENT SET TYPE IN CLASS LOCATION!!!");
        this.locationId = new_type;
    }
    
}

class pHSensor
{
    constructor(phId, greenhouseId)
    {
        this._phId = phId;
        this._greenhouseId = greenhouseId;
        this._currentState = "Unknown";
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId; }
    getGreenhouseId() { return this._greenhouseId; }
    getCurrentState() { return this._currentState; }
    
    /* Setter Functions */
    setGreenhouseId(new_greenhouse)
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS PH SENSOR!!!")
        this._greenhouseId = new_greenhouse;
    }
}

class lightSensor
{
    constructor(sensorId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._greenhouseId = greenhouseId;
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId }
    getGreenhouseId() { return this._greenhouseId }
    
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS LIGHT SENSOR");   
    }
}

class waterLevelSensor
{
    constructor(sensorId, locationId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._locationId = locationId;
        this._greenhouseId = greenhouseId;
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId }
    getLocationId()   { return this._locationId }
    getGreenhouseId() { return this._greenhouseId }
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS WATER LEVEL SENSOR!!!");
    }
}

class waterTempSensor
{
    constructor(sensorId, locationId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._locationId = locationId;
        this._greenhouseId = locationId;
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId }
    getLocationId()   { return this._locationId }
    getGreenhouseId() { return this._greenhouseId }
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS WATER TEMP SENSOR!!!");
    }
}

class humiditySensor
{
    constructor(sensorId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._greenhouseId = greenhouseId;
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId }
    getGreenhouseId() { return this._greenhouseId } 
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS HUMIDITY SENSOR!!!");
    }
}

class airTempSensor
{
    constructor(sensorId, greenhouseId)
    {
        this._sensorId = sensorId;
        this._greenhouseId = greenhouseId;
    }
    
    /* Getter Functions */
    getSensorId()     { return this._sensorId }
    getGreenhouseId() { return this._greenhouseId }
    
    /* Setter Functions */
    setGreenhouseId()
    {
        document.write("IMPLEMENT SET GREENHOUSE ID IN CLASS AIR TEMP SENSOR!!!");    
    }
}


class Greenhouse
{
    constructor(greenhouseId)
    {
        // The constructor shouldn't take any input arguments other than the id.  Instead, it should
        // set up the data containers for individual objects inside of the greenhouse.  
        // These objects will be added on later when the server sends them to the client
        this._greenhouseId = greenhouseId;
        
        this._relays = [];
        this._solenoids = [];
        this._lights = [];
        this._ventilations = [];
        this._soils = [];
        this._locations = [];
        this._ph_sensors = [];
        this._light_sensors = [];
        this._water_level_sensors = [];
        this._water_temp_sensors = [];
        this._humidity_sensors = [];
        this._air_temp_sensors = [];
    }
    
    /* Functions to add new components to the greenhouse */
    addRelay(new_relay)                         { this._relays.push(new_relay); }
    addSolenoid(new_solenoid)                   { this._solenoids.push(new_solenoid); }
    addLight(new_light)                         { this._lights.push(new_light); }
    addVentilation(new_ventilation)             { this._ventilations.push(new_ventilation); }
    addSoil(new_soil)                           { this._soils.push(new_soil); }
    addLocation(new_location)                   { this._locations.push(new_location); }
    addpHSensor(new_ph_sensor)                  { this._ph_sensors.push(new_ph_sensor); }
    addLightSensor(new_light_sensor)            { this._light_sensors.push(new_light_sensor); }
    
    addWaterLevelSensor(new_water_level_sensor) { this._water_level_sensors.push(new_water_level_sensor); }
    addWaterTempSensor(new_water_temp_sensor)   { this._water_temp_sensors.push(new_water_temp_sensor); }
    addHumiditySensor(new_humidity_sensor)      { this._humidity_sensors.push(new_humidity_sensor); }
    addAirTempSensor(new_air_temp_sensor)       { this._air_temp_sensors.push(new_air_temp_sensor); }

    /* Getter Functions */
    getRelayById(relay_id)
    {
        var i = 0; 
        var found = false;
        for(i = 0; i<this._relays.length; i++)
        {
            if(this._relays[i]._relayId == relay_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
     
        return this._relays[i];   
    }
    
    getSolenoidById(solenoid_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._solenoids.length; i++)
        {
            if(this._solenoids[i]._actuatorId == solenoid_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._solenoids[i];
    }
    
    getLightById(light_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._lights.length; i++)
        {
            if(this._lights[i]._actuatorId == light_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._lights[i];
    }
    
    getVentilationById(ventilation_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._ventilations.length; i++)
        {
            if(this._ventilations[i]._actuatorId == ventilation_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._ventilations[i];
    }
    
    getSoilSensorById(soil_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._soils.length; i++)
        {
            if(this._soils[i].getSensorId() == soil_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._soils[i];
    }
    
    getLocationById(location_id)
    {
        var i = 0; 
        var found = false;
        for(i = 0; i<this._locations.length; i++)
        {
            if(this._locations[i]._locationId == location_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._locations[i];
    }
    
    getpHSensorById(ph_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._ph_sensors.length; i++)
        {
            if(this._ph_sensors[i]._sensorId == ph_sensor_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._ph_sensors[i];
    }
    
    getLightSensorById(light_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._light_sensors.length; i++)
        {
            if(this._light_sensors[i]._sensorId == light_sensor_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._light_sensors[i];
    }
    
    getWaterLevelSensorById(water_level_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._water_level_sensors.length; i++)
        {
            if(this._water_level_sensors[i]._sensorId == water_level_sensor_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._water_level_sensors[i];
    }
    
    getWaterTempSensorById(water_temp_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._water_temp_sensors.length; i++)
        {
            if(this._water_temp_sensors[i]._sensorId == water_temp_sensor_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._water_temp_sensors[i];
    }
    
    getHumiditySensorById(humidity_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._humidity_sensors.length; i++)
        {
            if(this._humidity_sensors[i]._sensorId == humidity_sensor_id)
            {
                found = true;
                break;
            }
        }
        
        if(found != true)
        {
            return null;
        }
        
        return this._humidity_sensors[i];
    }
    
    getAirTempSensorById(air_temp_sensor_id)
    {
        var i = 0;
        var found = false;
        for(i = 0; i<this._air_temp_sensors.length; i++)
        {
            if(this._air_temp_sensors[i]._sensorId == air_temp_sensor_id)
            {
                found = true;
                break;
            }
        }
    
        if(found != true)
        {
            return null;
        }
        
        return this._air_temp_sensors[i];
    }
}