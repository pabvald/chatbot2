from app import app, db 
from models import User, Appointment


class UserService(object):
    """ UserService class. """

    def __init__(self, df_session):
        """ Initializes an UserService instance """
        try:
            user = db.session.query(User).filter_by(df_session=df_session).first()
            if not user:
                user = User(df_session)
                db.session.add(user) 
                db.session.commit() 

            self.user_id = user.id 

        except Exception as e:
            app.logger.error(str(e))
            raise

    def make_appointment(self, t_date, t_time, topic):
        """ Makes an appointment for the user. """
        try:
            appointment = Appointment(t_date, t_time, topic, self.user_id)
            db.session.add(appointment)
            db.session.commit()
    
        except Exception as e:
            app.logger.error(str(e))
            raise

    def get_appointments(self):
        """ Returns all user's appointments """
        try:
            user = db.session.query(User).get(self.user_id)
            return user.appointments

        except Exception as e:
            app.logger.error(str(e))
            raise
