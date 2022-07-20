'''
Created on 29 Sep 2021

@author: acmt2
'''

from eka.dt_mngmnt import DtMngmnt
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for)
# from werkzeug.security import check_password_hash, generate_password_hash
# from eka import create_app
# # application = create_app()

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        # password = request.form['password']
        # db = get_db()
        
        # verify if already register, a file with the name in the folder
        # eg: amorales
        res = DtMngmnt()
        res.set_directory(0)
        user_exist = res.verify_user(username)
        error = None

        if not username:
            error = 'Username is required.'
        # validate that the username is not already in the DB
        elif user_exist:
            error = 'User "{}" is already registered.'.format(username)

        if error is None:
            # create file with user's name
            res.create_user_file(username)
            # res.createCSVresultsFile(username)
            return redirect(url_for('auth.login'))
        
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']

        error = None

        # validate username is already in the files
        res = DtMngmnt()
        res.set_directory(0)
        exist = res.verify_user(username)
        
        if not exist:
            error = 'Incorrect username.'
        
        if error is None:
            user_file = res.load_user_file(username)
            session.clear()
            session['user_id'] = user_file['id']
            session['username'] = username
            
            # in case is admin
            if res.verify_admin(user_file):
                session['admin'] = True
            else:
                session['admin'] = False

            return redirect(url_for('evaluation.index'))
        
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    res = DtMngmnt()
    res.set_directory(0)
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = res.load_user_file(session.get('username'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('evaluation.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
