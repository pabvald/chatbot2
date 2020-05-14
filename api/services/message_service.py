
class MessageService(object):
    """ MessageService class. Interface to access a Dialogflow's 
        JSON response """ 

    def __init__(self, msg):
        """ Initializes a MessageService instance """
        self._msg = msg 

    @property 
    def intent(self):
        return self._msg['queryResult']

    @property 
    def lang(self):
        return  self._msg['queryResult']['languageCode']

    @property 
    def action(self):
        return self._msg['queryResult']['action']

    @property 
    def session(self):
        return self._msg['session']

    @property
    def parameters(self):
        return self._msg['queryResult']['parameters']

    @property 
    def user_id(self):
        session = self.session 
        user_id = session.split('/')[-1]
        return user_id

    @property
    def fulfillment_text(self):
        return self._msg['queryResult']['fulfillmentText']