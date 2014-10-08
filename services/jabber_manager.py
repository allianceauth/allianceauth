import os
from django.conf import settings
from openfire import exception
from openfire import UserService
from urlparse import urlparse


class JabberManager():
    
    def __init__(self):
        pass

    def __add_address_to_username(self, username):
        address = urlparse(settings.OPENFIRE_ADDRESS).netloc.split(":")[0]
        completed_username = username + "@" + address
        return completed_username

    def __santatize_username(self, username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    def __generate_random_pass(self):
        return os.urandom(8).encode('hex')

    def add_user(self, username):

        try:
            sanatized_username = self.__santatize_username(username)
            password = self.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.add_user(sanatized_username, password)

        except exception.UserAlreadyExistsException:
            # User exist
            return "", ""

        return sanatized_username, password

    def delete_user(self, username):
        try:
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.delete_user(username)
            return True
        except exception.UserNotFoundException:
            return False

    def lock_user(self, username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.lock_user(username)

    def unlock_user(self, username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.unlock_user(username)

    def update_user_pass(self, username):
        try:
            password = self.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.update_user(username, password)
            return password
        except exception.UserNotFoundException:
            return ""
