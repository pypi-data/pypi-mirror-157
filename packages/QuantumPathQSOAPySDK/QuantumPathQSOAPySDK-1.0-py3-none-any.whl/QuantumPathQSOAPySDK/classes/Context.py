from .apiConnection import apiConnection

class Context:

    # CONSTRUCTOR
    def __init__(self, username, password, url):
        self.__credentials = {
            "Username": username,
            "Password": password
        }

        self.__authToken = apiConnection(url, self.__credentials, 'string', 'data')

        self.__header = {
            "Authorization": 'Bearer ' + str(self.__authToken)
        }


    # GETTERS
    def getCredentials(self):
        return self.__credentials

    def getAuthToken(self):
        return self.__authToken
    
    def getHeader(self):
        return self.__header