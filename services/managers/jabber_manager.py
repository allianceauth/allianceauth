import os
from django.conf import settings
from openfire import exception
from openfire import UserService
from urlparse import urlparse


class JabberManager:
    
    def __init__(self):
        pass

    @staticmethod
    def __add_address_to_username(username):
        address = urlparse(settings.OPENFIRE_ADDRESS).netloc.split(":")[0]
        completed_username = username + "@" + address
        return completed_username

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def add_user(username):

        try:
            sanatized_username = JabberManager.__santatize_username(username)
            password = JabberManager.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.add_user(sanatized_username, password)

        except exception.UserAlreadyExistsException:
            # User exist
            return "", ""

        return sanatized_username, password

    @staticmethod
    def delete_user(username):
        try:
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.delete_user(username)
            return True
        except exception.UserNotFoundException:
            return False

    @staticmethod
    def lock_user(username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.lock_user(username)

    @staticmethod
    def unlock_user(username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.unlock_user(username)

    @staticmethod
    def update_user_pass(username):
        try:
            password = JabberManager.__generate_random_pass()
            api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
            api.update_user(username, password)
            return password
        except exception.UserNotFoundException:
            return ""