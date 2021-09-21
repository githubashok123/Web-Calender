from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields
from datetime import date
import sys

app = Flask(__name__)
db1 = SQLAlchemy(app)
# add database details here.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'


class Event(db1.Model):
    __tablename__ = 'events'
    id = db1.Column(db1.Integer, primary_key=True)
    event = db1.Column(db1.String, nullable=False)
    date = db1.Column(db1.Date, nullable=False)


resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.String
}

db1.create_all()
api = Api(app)


class EventCalender(Resource):
    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_time', type=inputs.date)
        parser.add_argument('end_time', type=inputs.date)

        try:
            args = parser.parse_args()

            start_time = args['start_time'].date()
            end_time = args['end_time'].date()
            event = Event.query.filter(Event.date.between(start_time, end_time)).all()
            return event
        except Exception:
            return Event.query.all()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'date',
            type=inputs.date,
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True
        )
        parser.add_argument(
            'event',
            type=str,
            help="The event name is required!",
            required=True
        )
        args = parser.parse_args()
        event = Event(id=len(Event.query.all()) + 1, event=args['event'], date=args['date'])

        db1.session.add(event)
        db1.session.commit()
        success = {'message': 'The event has been added!', 'event': args['event'], 'date': str(args['date'].date())}
        return success, 200


class EventByDate(Resource):
    @marshal_with(resource_fields)
    def get(self, get_date=date.today()):
        return Event.query.filter(Event.date == get_date).all()


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db1.session.delete(event)
        db1.session.commit()
        return {"message": "The event has been deleted!"}


# api.add_resource(BoundDate, '/event')

api.add_resource(EventByID, '/event/<int:event_id>')
api.add_resource(EventCalender, '/event', endpoint='event')
api.add_resource(EventByDate, '/event/today', endpoint='today')
# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
