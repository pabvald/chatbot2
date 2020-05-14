from app import app
from brain import ACTIONS, LANGUAGES, SOURCE
from utils import get_content 
from datetime import datetime, date, time 
from dateparser import parse 
from babel.dates import format_date, format_time
from services import UserService, AppointmentService, MessageService


class MasterMind(object):
    """ MasterMind class """

    def __init__(self, msg):
        """ Initializes a MasterMind instance """
        self.msg = MessageService(msg)
        self.user = UserService(self.msg.user_id)

    def get_response(self):
        """ Generates a response based on the received message """
        response = None
        try:
            if self.msg.lang not in LANGUAGES:
                response = self._unavailable_language_msg()
            else:
                response = self._do_action() 
        
        except Exception as e:
            app.logger.error(str(e))
            response = self._internal_error_msg()

        finally:
            return response

    @staticmethod
    def _simple_response(text):
        """ Generates a simple response"""
        return {
                "fulfillment_text": text,
                "source": SOURCE
            }

    def _internal_error_msg(self):
        """ Generates an internal error message in the corresponding language """
        return MasterMind._simple_response(get_content(self.msg.lang, ['internal_error']))

    def _unavailable_language_msg(self):
        """ Generates a simple response indicating that the used language is not 
            available """ 
        text = "The language '{}' is not available.".format(self.msg.lang)
        return MasterMind._simple_response(text)

    def _fail_action_msg(self, errors):
        """ Generates a response for a failed action """
        parameters = self.msg.parameters
        invalid_param = list(errors.keys())[0]
        if invalid_param in list(parameters.keys()):
            parameters[invalid_param] = ''

        return {
                    "followup_event_input": {
                        "name": "re_{}".format(self.msg.action),                       
                        "parameters": parameters,
                        "language_code": self.msg.lang
                    },
                    "fulfillment_text": errors[invalid_param],
                    "source": SOURCE                    
                }   

    def _do_action(self):
        """ Executes the corresponding action """ 
        if self.msg.action not in ACTIONS:
            raise AttributeError("Action '{}' is not a valid action".format(self.msg.action))
        if self.msg.action  == 'make_appointment':
            response = self._make_appointment()
        return response     

    def _make_appointment(self):
        """ Registers an appointment """
        errors = {}
        required_parameters = 2
        content = get_content(self.msg.lang, ['make_appointment'])
        t_date = parse(self.msg.parameters['date'], languages=[self.msg.lang]).date()
        t_time =  parse(self.msg.parameters['time'], languages=[self.msg.lang]).time()
        t_datetime = datetime.combine(t_date, t_time)
        text_params = {
            'topic': self.msg.parameters['topic'],
            'time': format_time(t_time, 'H:mm', locale=self.msg.lang),
            'date': format_date(t_date, format='full', locale=self.msg.lang)
        }
        available_slots = AppointmentService.get_available_slots(t_date.isoformat())        

        # Validate date         
        if t_date < date.today():
            errors['date'] = content['past_date'].format(**text_params)

        elif not AppointmentService.office_is_open_on_date(t_date.isoformat()):
            errors['date'] =  content['office_close_date'].format(**text_params)

        elif not available_slots:
            errors['date'] =  content['not_available_date'].format(**text_params)
        else:
            required_parameters -= 1       

        # Validate time
        if t_datetime < datetime.now():
            errors['time'] =  content['past_datetime'].format(**text_params)

        elif not AppointmentService.office_is_open_on_datetime(
                                            t_datetime.isoformat()):
            errors['time'] =  content['office_close_time'].format(**text_params)
        
        elif not AppointmentService.is_available(t_datetime.isoformat()):
            errors['time'] =  content['not_available_time'].format(**text_params)     
        else:
            required_parameters -= 1 

        # Make appointment
        if required_parameters == 0:
            closest_datetime = AppointmentService.closest_half(t_datetime.isoformat())
            t_time = datetime.fromisoformat(closest_datetime).time()

            try:
                self.user.make_appointment(t_date, t_time, text_params['topic'])
            except Exception as e:
                app.logger.error(str(e))
                errors['main'] =  content['error']
        
        if errors:
            response = self._fail_action_msg(errors)
        else:
            response = MasterMind._simple_response(content['success'].format(**text_params))

        return response
