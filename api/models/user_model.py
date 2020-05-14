from app import db


class User(db.Model):
    """ User model """
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)    
    df_session = db.Column(db.String(120), unique=True)
    appointments = db.relationship("Appointment", cascade="all, delete-orphan")

    def __init__(self, df_session):
        """ Initializes an UserModel instance """ 
        self.df_session = df_session
        
    def __repr__(self):
        """Obtains a representation of the User model """
        return '<User {}>'.format(self.id)
