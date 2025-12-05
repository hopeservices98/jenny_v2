import sys
import io
from app import create_app, db
from app.models import User

app = create_app()

# Handler WSGI pour Vercel
def handler(request):
    # Créer un objet requête WSGI à partir de la requête Vercel
    environ = {
        'REQUEST_METHOD': request['method'],
        'PATH_INFO': request['path'],
        'QUERY_STRING': request['queryString'] or '',
        'CONTENT_TYPE': request['headers'].get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(request.get('body', '') or '')),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': io.StringIO(request.get('body', '') or ''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'SERVER_NAME': request['headers'].get('Host', 'vercel.app'),
        'SERVER_PORT': '443',
        'HTTP_HOST': request['headers'].get('Host', 'vercel.app'),
    }
    
    # Ajouter les headers HTTP
    for key, value in request['headers'].items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    def start_response(status, headers):
        pass
    
    response_body = app.wsgi_app(environ, start_response)
    return list(response_body)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@example.com', is_admin=True, is_active=True)
            admin_user.set_password('Admin123!') # Mot de passe par défaut plus standard (à changer)
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True, port=5000)