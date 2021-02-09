import os

class Settings:
    def __init__(self):
        self.ADMIN_ROLE=os.getenv('BOT_ADMIN_ROLE','Admin')
        self.GUILD_NAME=os.getenv('GUILD_NAME')

        

    def as_string(self):
        ret=""
        for k,v in self.__dict__.items():
            if not k.startswith('_') and k.upper()==k:
                ret+=f"{k}={v}\n"
                
        return ret