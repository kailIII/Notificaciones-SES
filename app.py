# -*- coding: utf-8 -*-
import datetime
import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_mongoengine import MongoEngine
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import helpers as admin_helpers
# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
# Creamos modelo relacional
db = SQLAlchemy(app)
#Creamos modelo
dbm = MongoEngine()
dbm.init_app(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

# No SQL
# Definimos modelo de la BD
class Status(dbm.Document):
    recipients = dbm.StringField()
    source = dbm.StringField()
    timestamp = dbm.DateTimeField()
    sendingAccountId = dbm.StringField()
    destination = dbm.StringField()
    notificationType = dbm.StringField()
    smtpResponse = dbm.StringField()
    reportingMTA = dbm.StringField()
    messageId = dbm.StringField()
    processingTimeMillis = dbm.IntField()
    sourceArn = dbm.StringField()
    bounceSubType = dbm.StringField()
    bouncedRecipients = dbm.StringField()
    bounceType = dbm.StringField()
    feedbackId = dbm.StringField()
    domains = dbm.StringField()
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
# Vistas Login
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active() or not current_user.is_authenticated():
            return False

        if current_user.has_role('superuser'):
            return True

        return True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated():
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
        
# Vista del Modelo no relacional
class StatusView(ModelView):

    def is_accessible(self):
        if not current_user.is_active() or not current_user.is_authenticated():
            return False

        if current_user.has_role('superuser'):
            return True

        return True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated():
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    column_filters = ['source',
                      'recipients',
                      'destination',
                      'notificationType',
                      'timestamp',
                      'domains']
    column_searchable_list = ['source',
                              'recipients',
                              'destination',
                              'domains',
                              'notificationType']
    column_exclude_list = ['sendingAccountId',
                           'reportingMTA',
                           'messageId',
                           'processingTimeMillis',
                           'sourceArn',
                           'feedbackId',
                           'smtpResponse']

# Template General
@app.route('/')
def index():
    return '<a href="/admin/">Ir a administrador</a>'
# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )    

if __name__ == '__main__':

    # Create admin
    admin = flask_admin.Admin(
        app,
        'Notificaciones SQS',
        base_template='my_master.html',
        template_mode='bootstrap3',
    )
    # Agregamos modelos
    admin.add_view(MyModelView(Role, db.session))
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(StatusView(Status))
    app.run(host='0.0.0.0', debug=True)

