from app import create_app, db
from app.models import User
import os
import json

app = create_app()

# Handler ultra-simplifié pour Vercel
def handler(request):
    # Obtenir la méthode et le chemin
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    query_string = request.get('queryString', '') or ''
    
    # Headers de base pour WSGI
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': 'vercel.app',
        'SERVER_PORT': '443',
        'wsgi.url_scheme': 'https',
        'wsgi.input': __import__('io').BytesIO(),
        'wsgi.errors': __import__('sys').stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Headers de la requête
    headers = request.get('headers', {})
    for key, value in headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Fonction start_response simplifiée
    status = '200 OK'
    response_headers = []
    
    def start_response(status_line, headers_list):
        nonlocal status, response_headers
        status = status_line
        response_headers = headers_list
    
    # Appeler l'app Flask
    try:
        result = app.wsgi_app(environ, start_response)
        response_body = b''.join(result)
        return response_body
    except Exception as e:
        error_msg = f"Erreur interne: {str(e)}"
        return error_msg.encode('utf-8')

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