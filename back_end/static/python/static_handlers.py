#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./static/python/static_handlers.py                                     #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import tornado.web
import os

# ---------------------------------------------------------------------------- #
# Static Handlers                                                              #
# ---------------------------------------------------------------------------- #

class LoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/login.html")

class ErrorHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/dummy.html")

class CreateAccountHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/create_new_account.html")

class CredentialRecoveryHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/credential_recovery.html")

class OverviewScreenHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/overview_screen.html")
        
class CreateGreenhouseHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/create_greenhouse.html")        

class EditGreenhouseHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/edit_greenhouse.html")

class DeleteGreenhouseHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/delete_greenhouse.html")
        
class AddComponentHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/add_component.html")
        
# ---------------------------------------------------------------------------- #
# Generic File Handler                                                         #
# ---------------------------------------------------------------------------- #

class ProgramFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(ProgramFileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        program_file = str(self.dirname) + '/' + str(self.filename) + '/' + str(path)

        super(ProgramFileHandler, self).get(program_file, include_body)

class FaviconFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(FaviconFileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        program_file = str(self.dirname) + '/' + str(self.filename) + '/' + str(path)

        self.absolute_path = "./favicon.ico"
        
        super(FaviconFileHandler, self).get("./favicon.ico", include_body)