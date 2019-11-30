from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from fluencybox import db, app, ma
from marshmallow import fields
from sqlalchemy import Index

class Report_Images(db.Model):
    __tablename__ = "report_images"
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    filename = db.Column(db.String(255))
    scene_user_response_id = db.Column(db.Integer, db.ForeignKey('story_scene_user_response.id'), nullable=False)
    scene_user_response_score = db.Column(db.Float) #Added
    image_type = db.Column(db.String(50))

    def __repr__(self):
        return f"Report_Images('{self.report_id}', '{self.filename}', '{self.scene_user_response_id}', '{self.image_type}')"

class Report_Images_Schema(ma.ModelSchema):
    class Meta:
        fields = ("report_id", "filename", "scene_user_response_id", "image_type")
        model = Report_Images

class Story_Scene_User_Response(db.Model):
    __tablename__ = "story_scene_user_response"
    id = db.Column(db.Integer, primary_key=True)
    user_story_id = db.Column(db.Integer, db.ForeignKey('user_story.id'), nullable=False)
    story_scene_speaker_id =  db.Column(db.Integer, db.ForeignKey('story_scene_speaker.id'), nullable=False)
    audio_filename = db.Column(db.String(255))
    audio_text = db.Column(db.Text)
    report_images = db.relationship('Report_Images', backref='story_scene_user_response', lazy=True)

    def __repr__(self):
        return f"Story_Scene_User_Response('{self.user_story_id}', '{self.story_scene_speaker_id}', '{self.audio_filename}', '{self.audio_text}')"

class Story_Scene_User_Response_Schema(ma.ModelSchema):
    class Meta:
        fields = ("user_story_id", "story_scene_speaker_id", "audio_filename", "audio_text")
        model = Story_Scene_User_Response

class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    user_story_id = db.Column(db.Integer, db.ForeignKey('user_story.id'), nullable=False)
    score = db.Column(db.Float) #Changed to db.Column(db.Float)
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    report_images = db.relationship('Report_Images', backref='report', lazy=True)

    def __repr__(self):
        return f"Report('{self.uid}', '{self.user_story_id}', '{self.next_scene_order}', '{self.score}', '{self.uploaded_at}')"

class Report_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "user_story_id", "next_scene_order", "score", "uploaded_at")
        model = Report

class User_Story(db.Model):
    __tablename__ = 'user_story'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id =  db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=0)
    story_scene_user_response = db.relationship('Story_Scene_User_Response', backref='user_story', lazy=True)
    report = db.relationship('Report', backref='user_story', lazy=True)

    def __repr__(self):
        return f"User_Story('{self.user_id}', '{self.story_id}', '{self.created_at}')"

class User_Story_Schema(ma.ModelSchema):
    class Meta:
        fields = ("user_id", "story_id", "created_at")
        model = User_Story


class User_Purchase(db.Model):
    __tablename__ = "user_purchase"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float)
    stripe_charge_id = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    last_four = db.Column(db.String(25))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User_Purchase('{self.user_id}', '{self.amount}', '{self.stripe_charge_id}', '{self.brand}', '{self.last_four}', '{self.created_at}')"

class User_Purchase_Schema(ma.ModelSchema):
    class Meta:
        fields = ("user_id", "amount", "stripe_charge_id", "brand", "last_four", "created_at")
        model = User_Purchase

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
    profile_picture = db.Column(db.String(255), default = app.config.get('S3_URL') + app.config.get('S3_AVATAR_DIR') + '/' + app.config.get('DEFAULT_IMAGE'))
    failed_login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=0)
    created_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    refresh_token = db.Column(db.String(500))
    is_admin = db.Column(db.Boolean, default=0)
    user_story = db.relationship('User_Story', backref='user', lazy=True)
    user_purchase = db.relationship('User_Purchase', backref='user', lazy=True)

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

class User_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "first_name", "last_name", "email_address", "user_name", "phone_number", "profile_picture")
        model = User

class Story_Purchase(db.Model):
    __tablename__ = "story_purchase"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    __table_args__ = (Index('ix_user_id_story_id', "user_id", "story_id"), Index('user_id', "user_id"))

    def __repr__(self):
        return f"Story_Purchase('{self.user_id}', '{self.story_id}', '{self.created_at}')"

class Story_Purchase_Schema(ma.ModelSchema):
    class Meta:
        fields = ("user_id", "story_id", "created_at")
        model = Story_Purchase

class Story_Scene_Master_Response(db.Model):
    __tablename__ = 'story_scene_master_response'
    id = db.Column(db.Integer, primary_key=True)
    story_scene_speaker_id =  db.Column(db.Integer, db.ForeignKey('story_scene_speaker.id'), nullable=False)
    audio_filename = db.Column(db.String(255))
    audio_text = db.Column(db.Text)
    phoneme_filename = db.Column(db.String(255)) #Added

    def __repr__(self):
        return f"Story_Scene_Master_Response('{self.story_scene_speaker_id}', '{self.audio_filename}', '{self.audio_text}')"

class Story_Scene_Master_Response_Schema(ma.ModelSchema):
    class Meta:
        fields = ("story_scene_speaker_id", "audio_filename", "audio_text")
        model = Story_Scene_Master_Response

class Story_Scene_Speaker(db.Model):
    __tablename__ = 'story_scene_speaker'
    id = db.Column(db.Integer, primary_key=True)
    story_scene_id =  db.Column(db.Integer, db.ForeignKey('story_scene.id'), nullable=False)
    order = db.Column(db.Integer)
    image_filename = db.Column(db.String(255))
    audio_filename = db.Column(db.String(255))
    audio_text = db.Column(db.Text)
    prompt = db.Column(db.String(255))
    story_scene_master_responses = db.relationship('Story_Scene_Master_Response', backref='story_scene_speaker', lazy=True)
    story_scene_user_responses = db.relationship('Story_Scene_User_Response', backref='story_scene_speaker', lazy=True)

    def __repr__(self):
        return f"Story_Scene_Speaker('{self.story_scene_id}', '{self.order}', '{self.image_filename}', '{self.audio_filename}', '{self.audio_text}', '{self.prompt}')"

class Story_Scene_Speaker_Schema(ma.ModelSchema):
    class Meta:
        fields = ("id", "order", "image_filename", "audio_filename", "audio_text", "prompt")
        model = Story_Scene_Speaker

class Scene_Keyword(db.Model):
    __tablename__ = 'scene_keyword'
    id = db.Column(db.Integer, primary_key=True)
    story_scene_id =  db.Column(db.Integer, db.ForeignKey('story_scene.id'), nullable=False)
    keyword = db.Column(db.String(50))
    next_scene_order =  db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Scene_Keyword('{self.story_scene_id}', '{self.keyword}', '{self.next_scene_order}')"

class Scene_Keyword_Schema(ma.ModelSchema):
    class Meta:
        fields = ("keyword", "next_scene_order")
        model = Scene_Keyword

class Story_Scene(db.Model):
    __tablename__ = 'story_scene'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    story_id =  db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    order = db.Column(db.Integer)
    type = db.Column(db.String(25))
    next_scene_order = db.Column(db.Integer, nullable=True)
    story_scene_speakers = db.relationship('Story_Scene_Speaker', backref='story_scene', lazy=True)
    scene_keywords = db.relationship('Scene_Keyword', backref='story_scene', lazy=True)

    def __repr__(self):
        return f"Story_Scene('{self.uid}', '{self.story_id}', '{self.order}', '{self.type}', '{self.next_scene_order}')"

class Story_Scene_Schema(ma.ModelSchema):
    story_scene_speakers = fields.Nested(Story_Scene_Speaker_Schema, many=True)
    scene_keywords = fields.Nested(Scene_Keyword_Schema, many=True)
    class Meta:
        fields = ("uid", "order", "type", "next_scene_order", "story_scene_speakers", "scene_keywords")
        model = Story_Scene

class Story(db.Model):
    __tablename__ = 'story'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(75))
    description = db.Column(db.Text)
    length = db.Column(db.String(15))
    image_filename = db.Column(db.String(255))
    difficulty = db.Column(db.String(25))
    genre = db.Column(db.String(25))
    is_demo = db.Column(db.Boolean, default=0)

    story_scenes = db.relationship('Story_Scene', backref='story', lazy=True)
    user_story = db.relationship('User_Story', backref='story', lazy=True)
    
    def __repr__(self):
        return f"Story('{self.uid}', '{self.name}', '{self.description}', '{self.length}', '{self.image_filename}', '{self.difficulty}', '{self.genre}, '{self.is_demo} ')"

class Story_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "name", "description", "length", "image_filename", "difficulty", "genre", "is_demo")
        model = Story
        

db.create_all()