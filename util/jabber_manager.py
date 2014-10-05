from django.conf import settings
from django.db import connections, transaction
from openfire import UserService

class JabberManager():
    
    def __init__(self):
        pass
    
    def add_user(self, username, password):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        print str(username)
        print str(password)
        api.add_user(self.__santatize_username(username), str(password))
        
    def delete_user(self, username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.delete_user(username, password)
        
    def lock_user(self, username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.lock_user(username, password)
        
    def unlock_user(self, username):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.unlock_user(username, password)
        
    def update_user_pass(self, username, password):
        api = UserService(settings.OPENFIRE_ADDRESS, settings.OPENFIRE_SECRET_KEY)
        api.update_user(username, password)
        
    def __santatize_username(self, username):
        sanatized = username.replace(" ","_")
        return sanatized.lower()