import datetime
import sqlite3

from flask import Flask, request, g, redirect

app = Flask(__name__)

DATABASE = './database.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# /reflected?name=<script>alert(1)</script>
@app.route("/reflected")
def reflected():
    if name := request.args.get('name'):
        return f'<p>Hello, {name}</p>'
    return "<p>Hello, World!</p>"


# <script>alert(1)</script>
@app.route("/stored")
def stored():
    db = get_db()
    cur = db.cursor()
    # cur.execute('delete from text_board')
    # db.commit()
    cur.execute('select * from text_board')
    records = cur.fetchall()

    html = ''
    for record in records:
        html += f'<div><p>{record[0]}</p><span>{record[1]}</span></div>'

    html += '''
        <form method='post' action="/stored">
            <input type='text' name='content'>
            <button type='submit'>Submit</button>
        </form>
    '''
    return html


@app.route("/stored", methods=['POST'])
def post_stored():
    if content := request.values.get('content'):
        db = get_db()
        cur = db.cursor()
        c_at = datetime.datetime.now()
        cur.execute('insert into text_board(content, c_at) values(?, ?)', (content, c_at))
        db.commit()

    return redirect('/stored')


# <img src=# onerror="alert(123)">
@app.route("/dom-based")
def dom_based():
    return '''
        <script>
            var display_name = function() {
                var name = document.getElementById('name').value;
                document.getElementById('display_name').innerHTML = name;
            }
        </script>

        <p>Hello, <span id="display_name"></span></p>
        <input id="name" type="text">
        <button onclick="display_name();">display</button>
    '''
