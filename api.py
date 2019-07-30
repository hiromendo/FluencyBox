from flask import Flask, request, jsonify, make_response
from flaskext.mysql import MySQL
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config.from_pyfile('config.py')

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def index():
    return jsonify({"Page" : "Index"})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = None
        refresh_token = None

        if 'x-access-token' in request.headers:
            access_token = request.headers['x-access-token']
        if 'x-refresh-token' in request.headers:
            refresh_token = request.headers['x-refresh-token']

        if not access_token:
            return jsonify({'message' : 'Token is missing!'}), 401
        
        try:
            payload = jwt.decode(access_token, app.config.get('SECRET_KEY'))
            print(payload['UID'])
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message' : 'Token has expired!'}), 401
            #Refesh token logic
        except jwt.InvalidTokenError:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated


    
#Get a complete list of Users
@app.route('/user',methods=['GET'])
@token_required
def Get_All_Users():
    try:
        args = []
        Users = MakeProcedureCall('p_GetAllUsers', args)
 
        output = []
        for user in Users:
            user_data = {}
            user_data['FirstName'] = user[0]
            user_data['LastName'] = user[1]
            user_data['UserName'] = user[2]
            output.append(user_data)
        
        return jsonify({'users' : output}), 200
        
    except Exception as e:
        return jsonify({'error' : str(e)})

#Get a Users by UID
@app.route('/user/<User_UID>',methods=['GET'])
def Get_User_By_UID(User_UID):
    try:
        args = [User_UID]
        Users = MakeProcedureCall('p_GetUserByUID', args)
        if len(Users) is 0:
            return jsonify({'message' : "No User found"}), 200
        user_data = {}
        user_data['User_UID'] = Users[0][0]
        user_data['FirstName'] = Users[0][1]
        user_data['LastName'] = Users[0][2]
        user_data['EmailAddress'] = Users[0][3]
        user_data['PhoneNumber'] = Users[0][4]
        user_data['CreatedOn'] = Users[0][5]
        
        return jsonify({'users' : user_data}), 200
        
    except Exception as e:
        return jsonify({'error' : str(e)})


@app.route('/user', methods=["POST"])
def Create_User():
    try:
        User_Data = request.get_json()
        Hashed_Password = generate_password_hash(User_Data['Password'], method='sha256')
        User_UID = str(uuid.uuid4())
        FirstName = User_Data['FirstName'] 
        LastName = User_Data['LastName'] 
        EmailAddress = User_Data['EmailAddress'] 
        PhoneNumber = User_Data['PhoneNumber'] 
        args = [User_UID, FirstName, LastName, EmailAddress, Hashed_Password, PhoneNumber]
        result = MakeProcedureCall('p_Registration', args)
        return jsonify({"status" : result})
    except Exception as e:
        return jsonify({'error' : str(e)})

@app.route('/login')
def login():
    try:
        auth = request.authorization

        #This can change to email address being sent as JSON
        if not auth or not auth.username or not auth.password:
            return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

        args = [auth.username]
        User = MakeProcedureCall('p_GetValidUser', args)
        if len(User) is 0:
            return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        user_data = {}
        user_data['User_UID'] = User[0][0]
        user_data['Password'] = User[0][1]
        
        if check_password_hash(user_data['Password'], auth.password):
            token = jwt.encode({'UID' : user_data['User_UID'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['TOKEN_EXPIRY'])}, app.config['SECRET_KEY'])
            return jsonify({'token' : token.decode('UTF-8')})

        return make_response('Invalid Credentials', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    except Exception as e:
        return jsonify({'error' : str(e)})

#Method to make database procedure calls
def MakeProcedureCall(ProcedureName, ParamList):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc(ProcedureName, ParamList)
        result = cursor.fetchall()
        cursor.close()
        cursor = con.cursor()
        return result
    except Exception as e:
         print(str(e))
         return jsonify({'error' : str(e)})
    finally:
        cursor.close()
        con.close()

if __name__ == '__main__':
    app.run()
