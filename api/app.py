import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy


global db


app = Flask(__name__)
load_dotenv()
app.config.from_object(os.getenv('APP_SETTINGS'))
db = SQLAlchemy(app)


from brain.mastermind import MasterMind 
from logs.functions import init_log 


init_log(app)


@app.route('/')
def index():
    """ Does nothing """
    return 'index'


@app.route('/dialogflow', methods=['POST'])
def respond_dialogflow():
    try:
        msg = request.get_json(silent=True)
        mastermind = MasterMind(msg)
        response = mastermind.get_response()
    except Exception as e:
        app.logger.error(str(e))
        response = {
            "fulfillment_text": "There was an internal error. Please, try again later."
        }
    finally:
        return jsonify(response)



if __name__ == '__main__':
    app.run(port=5001, threaded=True)