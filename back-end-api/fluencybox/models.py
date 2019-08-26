from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from fluencybox import db, app, ma

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    user_name = db.Column(db.String(25), unique=True, nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100))
    phone_number = db.Column(db.String(25))
    profile_picture = db.Column(db.String(255), default = app.config.get('S3_URL') + app.config.get('S3_AVATAR_DIR') + '/default_image.png')
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    refresh_token = db.Column(db.String(500))

    def get_reset_token(self):
        expires_sec = app.config['PASSWORD_RESET_TOKEN_EXPIRY']
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            id = s.loads(token)['id']
        except:
            return None
        return User.query.get(id)

    def __repr__(self):
        return f"User('{self.uid}', '{self.first_name}', '{self.last_name}', '{self.user_name}', '{self.email_address}', '{self.phone_number}', '{self.profile_picture}')"

class user_schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "first_name", "last_name", "email_address", "user_name", "phone_number", "profile_picture")
        model = User

db.create_all()