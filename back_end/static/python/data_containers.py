#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./static/python/data_containers.py                                     #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import logging

# ---------------------------------------------------------------------------- #
# Console/File Logger                                                          #
# ---------------------------------------------------------------------------- #

print_logger = logging.getLogger(__name__)
print_logger.setLevel(logging.DEBUG)

def upload_website_state(websocket_object, current_greenhouse_database, component_name, table_name, greenhouse_id):
    database_result = current_greenhouse_database.issue_db_command("SELECT * FROM %s WHERE greenhouseId = \"%s\";" % (table_name, greenhouse_id))

    if database_result is False:
        return

    for relay_tuple in database_result:
        send_string = ""
                
        for feature in relay_tuple:
            send_string = send_string + ":" + str(feature)
                
        websocket_object.write_message("IC:%s%s" % (component_name, send_string))
        print_logger.debug("Sending Message: IC:%s%s" %(component_name, send_string))
