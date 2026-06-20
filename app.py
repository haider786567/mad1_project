from flask import Flask,render_template
from config import Config
from models import User, db
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from controller.auth import auth_bp
from controller.admin import admin_bp
from controller.staff import staff_bp
from controller.user import user_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        db.session.execute(db.text("SELECT 1"))
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created with email: admin@example.com")
        print("✅ Database Connection Successful")
    except Exception as e:
        print("❌ Database Connection Failed")
        print(e)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/')
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
if __name__ == '__main__':
    app.run(debug=True)