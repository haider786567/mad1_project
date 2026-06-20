from flask import Flask,render_template
from config import Config
from models import User, db
from flask_login import LoginManager
from controller.auth import auth_bp
from controller.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        db.session.execute(db.text("SELECT 1"))
        print("✅ Database Connection Successful")
    except Exception as e:
        print("❌ Database Connection Failed")
        print(e)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
if __name__ == '__main__':
    app.run(debug=True)