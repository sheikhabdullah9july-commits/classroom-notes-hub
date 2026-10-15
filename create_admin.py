"""Interactively create an admin; never publishes a default password."""
from getpass import getpass
from app import create_app, db
from app.models import User

def main():
    app = create_app()
    username = input('Admin username: ').strip()
    email = input('Admin email: ').strip()
    password = getpass('Password (at least 12 characters): ')
    if not username or '@' not in email or len(password) < 12:
        raise SystemExit('Provide a username, valid email, and password of at least 12 characters.')
    if password != getpass('Confirm password: '):
        raise SystemExit('Passwords do not match.')
    with app.app_context():
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            raise SystemExit('Account already exists. Use an existing administrator to manage roles.')
        user = User(username=username, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print('Admin created. Your password was not printed or stored in source.')

if __name__ == '__main__':
    main()
