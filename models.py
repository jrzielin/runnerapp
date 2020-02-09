from app import db, bcrypt
from datetime import datetime
from validate_email import validate_email
from constants import ISO_FORMAT

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    metric = db.Column(db.Boolean, nullable=False, default=False)

    def validate(self):
        if self.first_name is None:
            return 'Must supply first name'

        if self.last_name is None:
            return 'Must supply last name'

        if self.email is None:
            return 'Must supply email'

        if not validate_email(self.email):
            return 'Invalid email address'

        if self.password is None:
            return 'Must supply password'

        if self.is_active not in {True, False}:
            return 'Invalid is_active value'

        if self.metric not in {True, False}:
            return 'Invalid metric value'

        if len(self.password) < 8:
            return 'Password must be at least 8 characters'

    def serialize(self, include_runs=False):
        data =  {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_active': self.is_active,
            'metric': self.metric,
            'created': self.created.strftime(ISO_FORMAT),
            'updated': self.updated.strftime(ISO_FORMAT)
        }

        if include_runs:
            runs = self.runs
            data['runs'] = [run.serialize() for run in runs]

        return data

    def hash_password(self):
        pw_hash = bcrypt.generate_password_hash(self.password).decode('utf-8')
        self.password = pw_hash

    def __repr__(self):
        return '<User {}>'.format(self.id)

class Run(db.Model):
    __tablename__ = 'runs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('runs', lazy=True))
    run_date = db.Column(db.DateTime, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    metric = db.Column(db.Boolean, nullable=False, default=False)
    warmup = db.Column(db.Integer)
    cooldown = db.Column(db.Integer)
    run_type = db.Column(db.String(128))
    location = db.Column(db.String(128))
    notes = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self, include_comments=False, include_intervals=False):
        data =  {
            'id': self.id,
            'user': self.user.serialize(),
            'run_date': self.run_date.strftime(ISO_FORMAT),
            'distance': self.distance,
            'duration': self.duration,
            'metric': self.metric,
            'warmup': self.warmup,
            'cooldown': self.cooldown,
            'run_type': self.run_type,
            'location': self.location,
            'notes': self.notes,
            'created': self.created.strftime(ISO_FORMAT),
            'updated': self.updated.strftime(ISO_FORMAT)
        }

        if include_comments:
            comments = self.run_comments
            data['run_comments'] = [comment.serialize() for comment in comments]
        
        if include_intervals:
            intervals = self.intervals
            data['intervals'] = [interval.serialize() for interval in intervals]

        return data

    def validate(self):
        if self.run_date is None:
            return 'Invalid run date'

        if self.distance is None:
            return 'Must supply distance'

        if self.duration is None:
            return 'Must supply duration'

        if self.metric not in {True, False}:
            return 'Invalid metric setting'
        
        if self.run_type is None:
            return 'Must supply run type'
        
    def __repr__(self):
        return '<Run {}>'.format(self.id)

class Interval(db.Model):
    __tablename__ = 'intervals'
    
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('runs.id'), nullable=False)
    run = db.relationship('Run', backref=db.backref('intervals', lazy=True))
    distance = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    metric = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'run': self.run.serialize(),
            'distance': self.distance,
            'duration': self.duration,
            'metric': self.metric,
            'created': self.created.strftime(ISO_FORMAT),
            'updated': self.updated.strftime(ISO_FORMAT)
        }

    def __repr__(self):
        return '<Interval {}>'.format(self.id)

class RunComment(db.Model):
    __tablename__ = 'run_comments'

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('runs.id'), nullable=False)
    run = db.relationship('Run', backref=db.backref('run_comments', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('run_comments', lazy=True))
    comment = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'run': self.run.serialize(),
            'user': self.user.serialize(),
            'comment': self.comment,
            'created': self.created.strftime(ISO_FORMAT),
            'updated': self.updated.strftime(ISO_FORMAT)
        }

    def validate(self):
        if self.comment is None or self.comment == '':
            return 'Must supply comment text'

    def __repr__(self):
        return '<RunComment {}>'.format(self.id)
