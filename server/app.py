from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages',methods=['GET', 'POST'])
def messages():
    
    if request.method=='GET':
        messages=Message.query.order_by(Message.created_at.asc()).all()
        if not messages:
            return make_response({"error":"There are no messages at the time"},404)
        response=make_response(jsonify([message.to_dict() for message in messages]),200)
        return response
    
    elif request.method=='POST':
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()
        response=make_response(jsonify(new_message.to_dict()),201)
        return response

@app.route('/messages/<int:id>',methods=['PATCH','DELETE'])
def messages_by_id(id):
    message=Message.query.filter_by(id=id).first()
    if not message:
        return make_response({"error":f"Message of id:{id} not found"},404)
    if request.method=='PATCH':
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])

        db.session.commit()

        message_dict = message.to_dict()

        response = make_response(
            jsonify(message_dict),
            200
        )

        return response
    
    elif request.method=='DELETE':
        db.session.delete(message)
        db.commit()
        
        response_body = {
        "delete_successful": True,
        "message": "Message deleted."
        }

        response = make_response(
            response_body,
            200
        )

        return response

if __name__ == '__main__':
    app.run(port=5555)
