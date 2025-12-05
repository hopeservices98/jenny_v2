from app import create_app, db
from app.models import User
import os

app = create_app()

# Handler simple pour Vercel
def handler(request):
    try:
        # Créer l'environnement WSGI
        body = request.get('body', '') or ''
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        query_string = request.get('queryString', '') or ''
        
        headers = request.get('headers', {})
        
        # Créer l'environnement WSGI de base
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': __import__('io').BytesIO(body.encode('utf-8')) if body else __import__('io').BytesIO(),
            'wsgi.errors': __import__('sys').stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
            'SERVER_NAME': headers.get('host', 'vercel.app'),
            'SERVER_PORT': '443',
        }
        
        # Ajouter les headers HTTP
        for key, value in headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        # Fonction de réponse
        response_status = [200]
        response_headers = []
        
        def start_response(status, headers):
            response_status[0] = status
            response_headers.extend(headers)
        
        # Appeler l'application Flask
        result = app.wsgi_app(environ, start_response)
        
        # Convertir le résultat en bytes
        response_body = b''.join(result)
        
        return response_body
        
    except Exception as e:
        return f"Erreur: {str(e)}".encode('utf-8')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(username='admin').first():
                admin_user = User(username='admin', email='admin@example.com', is_admin=True, is_active=True)
                admin_user.set_password('Admin123!')
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
    app.run(debug=True, port=5000)