from re import template
from flask import Blueprint, render_template, request, flash, jsonify, render_template_string, Flask, make_response
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from uuid import uuid1
from base64 import b64decode, b64encode
import pickle


views = Blueprint('views', __name__)
app = Flask(__name__)

class UserID:
    def __init__(self, uuid=None) -> None:
        self.uuid = str(uuid1())

    def __str__(self) -> str:
        return self.uuid


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    messages = Note.query.order_by(Note.date).all()

    user_obj = request.cookies.get('uuid')
    if user_obj == None:
        response = make_response(render_template("home.html", msg = messages, user = current_user))
        user_obj = UserID()
        response.set_cookie('uuid', b64encode(pickle.dumps(user_obj)))
        return response
    else:
        pickle.loads(b64decode(user_obj))
    
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            messages = Note.query.order_by(Note.date).all()

            flash('Note added!', category='success')
            return render_template("home.html", msg = messages, user = current_user)

    return render_template("home.html", msg = messages, user = current_user)


@views.route('/server', methods=['GET', 'POST'])
def server():
    id = request.args.get('id') or None
    current = Note.query.filter_by(user_id=id).order_by(Note.date).all()
    template = f"<h1>Notes of user with ID:{id}</h1>"

    for note in current:
        template += f"<p>{note.date}: {note.data}</p>"
    

    return render_template_string(template)


@views.route('/test', methods=['GET', 'POST'])
def test():
    # cookie = request.args.get('cookie') or None
    template = "<h1>YOUR COOKIE: {cookie} </h1>"

    user_obj = request.cookies.get('uuid')
    if user_obj == None:
        msg = "no cookies, making one"
        response = make_response(msg)
        user_obj = UserID()
        response.set_cookie('uuid', b64encode(pickle.dumps(user_obj)))
        return response
    else:
        return render_template_string(template.format(cookie=pickle.loads(b64decode(user_obj))))

    
    # return render_template_string(template)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})



