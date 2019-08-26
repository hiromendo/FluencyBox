from fluencybox import app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager = Manager(app)

#Below command will allow user to call migrate commands as : python manage.py _____
manager.add_command('db', MigrateCommand) 

if __name__ == '__main__':
    manager.run()


