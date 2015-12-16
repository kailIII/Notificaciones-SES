#Receptor de notificaciones SES (AWS) a través de SQS (AWS) V0.1

### Resumen
Sistema para recibir notificaciones SQS de SES

### Licencia
Este software esta licenciado bajo la licencia GPLv2

### Librerias

* https://flask-login.readthedocs.org/en/latest/
* https://flask-admin.readthedocs.org/en/latest/
* https://boto.readthedocs.org/en/latest/

### Plataforma, Framework o Lenguaje de Programación / BBDD
- Python, HTML, Javascript, CSS, MySQL  
- Django
- Twitter Bootstrap
- jQuery

### Requisitos Técnicos
- Nginx con sporte de Proxy
- Gunicorn y Supervisord
- MySQL >= 5.5.x
- MongoDB >= 2.6
- PIP

### Deploy
Ejecutar:
```
pip install -r requirements.txt
```

Ejecutar en contrab (tiempo y usuario a criterio)
```
{repo}/sqs.py
```

Importar tablas para administrar usuarios
```
mysql -u username -p dbname < schema.sql
```
Por defecto
 - Username: admin
 - Password: admin

Setear variables de Entorno en:
* {repo}/config.py a partir de * {repo}/config.py.template
* {repo}/configSQS.py a partir de * {repo}/configSQS.py.template

# Modo de Uso de Admin CRUD

```
python app.py
```
