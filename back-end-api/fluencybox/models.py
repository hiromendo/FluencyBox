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
    is_admin = db.Column(db.Boolean, default=0)

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


class Scene_Master_Response(db.Model):
    __tablename__ = 'scene_master_response'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    story_scene_id =  db.Column(db.Integer, db.ForeignKey('story_scene.id'), nullable=False)
    master_audio_response = db.Column(db.String(255))
    master_text_response = db.Column(db.Text)

    def __repr__(self):
        return f"Scene_Master_Response('{self.uid}', '{self.story_scene_id}', '{self.master_audio_response}', '{self.master_text_response}')"

class Scene_Master_Response_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "story_scene_id", "master_audio_response", "master_text_response")
        model = Scene_Master_Response

class Scene_Media(db.Model):
    __tablename__ = 'scene_media'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    story_scene_id =  db.Column(db.Integer, db.ForeignKey('story_scene.id'), nullable=False)
    media_order = db.Column(db.Integer)
    scene_image = db.Column(db.String(255))
    scene_audio = db.Column(db.String(255))
    scene_text = db.Column(db.Text)
    scene_hint = db.Column(db.String(255))
    show_single = db.Column(db.String(15), default=0)

    def __repr__(self):
        return f"Scene_Media('{self.uid}', '{self.story_scene_id}', '{self.media_order}', '{self.scene_image}', '{self.scene_audio}', '{self.scene_text}', '{self.scene_hint}')"

class Scene_Media_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "story_scene_id", "media_order", "scene_image", "scene_audio", "scene_text", "scene_hint")
        model = Scene_Media


class Story_Scene(db.Model):
    __tablename__ = 'story_scene'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    story_id =  db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    scene_order = db.Column(db.Integer)
    scene_keywords = db.Column(db.String(255))
    scene_type = db.Column(db.String(25))
    scene_medias = db.relationship('Scene_Media', backref='story_scene', lazy=True)
    scene_master_responses = db.relationship('Scene_Master_Response', backref='story_scene', lazy=True)

    def __repr__(self):
        return f"Story_Scene('{self.uid}', '{self.story_id}', '{self.scene_order}', '{self.scene_keywords}', '{self.scene_type}')"

class Story_Scene_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "story_id", "scene_order", "scene_keywords", "scene_type")
        model = Story_Scene


class Story(db.Model):
    __tablename__ = 'story'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    story_name = db.Column(db.String(75))
    story_desc = db.Column(db.Text)
    story_length = db.Column(db.String(15))
    story_image = db.Column(db.String(255))
    difficulty_level = db.Column(db.String(25))
    genre = db.Column(db.String(25))
    story_scenes = db.relationship('Story_Scene', backref='story', lazy=True)
    
    def __repr__(self):
        return f"Story('{self.uid}', '{self.story_name}', '{self.story_desc}', '{self.story_length}', '{self.story_image}', '{self.difficulty_level}', '{self.genre}')"

class Story_Schema(ma.ModelSchema):
    class Meta:
        fields = ("uid", "story_name", "story_desc", "story_length", "story_image", "difficulty_level", "genre")
        model = Story
