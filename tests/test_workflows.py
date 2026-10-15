import io
import tempfile
import unittest
from app import create_app, db, socketio
from app.models import User, Course, Note

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        class TestConfig:
            TESTING = True
            SECRET_KEY = 'isolated-test-secret'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = self.temp.name
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context(); self.ctx.push()
        self.client = self.app.test_client()
        admin = User(username='admin-test',email='admin@example.test',role='admin')
        admin.set_password('test-password-123')
        db.session.add_all([admin,Course(name='Software Engineering',code='SE101')]); db.session.commit()
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop(); self.temp.cleanup()
    def register(self):
        return self.client.post('/auth/register',data={'username':'learner','email':'learner@example.test','password':'test-password-123','role':'admin'})
    def login(self,email='learner@example.test'):
        return self.client.post('/auth/login',data={'email':email,'password':'test-password-123'})
    def test_registration_cannot_grant_admin(self):
        self.register()
        self.assertEqual(User.query.filter_by(username='learner').one().role,'student')
        self.login()
        self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_upload_approval_and_download(self):
        self.register(); self.login()
        response=self.client.post('/notes/upload/1',data={'title':'Study notes','description':'Demo notes','file':(io.BytesIO(b'Demo study material'),'notes.txt')})
        self.assertEqual(response.status_code,302)
        note=Note.query.one(); note_id=note.id
        self.client.get('/auth/logout')
        self.assertEqual(self.client.get(f'/notes/{note_id}').status_code,404)
        self.assertEqual(self.client.get(f'/notes/download/{note_id}').status_code,404)
        self.login('admin@example.test')
        self.assertEqual(self.client.post(f'/admin/approve/{note_id}').status_code,302)
        self.client.get('/auth/logout')
        self.assertEqual(self.client.get(f'/notes/{note_id}').status_code,200)
        with self.client.get(f'/notes/download/{note_id}') as downloaded:
            self.assertEqual(downloaded.data,b'Demo study material')
    def test_pages_reset_and_unauthenticated_chat(self):
        for path in ('/','/courses/','/notes/','/auth/login','/auth/register'):
            self.assertEqual(self.client.get(path).status_code,200,path)
        self.assertEqual(self.client.get('/auth/forgot-password').status_code,503)
        client=socketio.test_client(self.app)
        client.emit('message',{'room':1,'msg':'unauthenticated'})
        self.assertEqual(client.get_received(),[])
        client.disconnect()
    def test_external_login_redirect_is_rejected(self):
        self.register()
        response=self.client.post('/auth/login?next=https://example.invalid',data={'email':'learner@example.test','password':'test-password-123'})
        self.assertEqual(response.location,'/')

if __name__=='__main__': unittest.main()
