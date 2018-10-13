from flask import Flask, render_template, request, redirect, g, url_for, session, flash
from flask_session import Session #??????
# @Login_required
from functools import wraps
# Password function
from werkzeug.security import check_password_hash, generate_password_hash
# Session in file system
from tempfile import mkdtemp

import sqlite3

app = Flask(__name__)

# Secret key
app.secret_key = b'\x1a`\x8c?]\xd7\xc7\xaeFt\xf2\xf4\xc2c\x0bM'

########## Session in file system
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)


# Connect database
connect_db = sqlite3.connect("unigroop.db", check_same_thread=False)
db = connect_db.cursor()

# Ensure responses aren't cached
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

####################################
###            #####################
####  Routes  ######################
###            #####################

@app.route("/")
@login_required
def index():
    """Render Home Page"""

    # Get username and displayname
    db.execute("SELECT username, displayname FROM users WHERE user_id=?", (session["user_id"],))
    user = db.fetchall()

    # Query database for timetable data
    db.execute("SELECT availability FROM users WHERE user_id=?", (session["user_id"],))
    availability = db.fetchall()

    db.execute("SELECT group_id FROM group_log WHERE user_id=?", (session["user_id"],))
    group_ids = db.fetchall()


    group_data = {}
    group_members = {}
    all_group_members = []

    if not group_ids:
        if not availability:
            return render_template("index.html", availability=None, username=user[0][0], displayname=user[0][1])
        else:
            return render_template("index.html", availability=availability[0][0],
                group_data=group_data, username=user[0][0], displayname=user[0][1])
    else:
        for ids in group_ids:

            db.execute("SELECT name, code FROM groups WHERE group_id=?", (ids[0],))
            name_code = db.fetchall()
            group_data.update({ids[0] : [name_code[0][0], name_code[0][1]]})

            db.execute("SELECT user_id FROM group_log WHERE group_id=?", (ids[0],))
            member_ids = db.fetchall()

            if not member_ids:
                group_members.update({"-" : "-"})
            else:
                member_username = []
                member_displayname = []

                for member_id in member_ids:
                    db.execute("SELECT username, displayname FROM users WHERE user_id=?", (member_id[0],))
                    member_data = db.fetchall()
                    member_username.append(member_data[0][0])
                    member_displayname.append(member_data[0][1])

                for i in range(len(member_username)):
                    group_members.update({member_username[i] : member_displayname[i]})

            all_group_members.append(group_members)
            group_members = {}

        if not availability:
            return render_template("index.html", availability=None, group_data=group_data,
            all_group_members=all_group_members, username=user[0][0], displayname=user[0][1])
        else:
            return render_template("index.html", availability=availability[0][0], group_data=group_data,
                        all_group_members=all_group_members, username=user[0][0], displayname=user[0][1])


@app.route("/save", methods=['GET', 'POST'])
@login_required
def save():
    """Save availability to database"""
    # If user clicks save button, insert availability data into database
    if request.method == "POST":
        availability = request.form.get("timetable-data")
        db.execute("UPDATE users SET availability = ? WHERE user_id = ?", (availability, session["user_id"]))
        connect_db.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route("/collab", methods=['GET', 'POST'])
@login_required
def collab():
    """Render collaborated timetable"""
    if request.method == "POST":

        # Save availability as marked on timetable before collaborating
        availability = request.form.get("timetable-data")
        db.execute("UPDATE users SET availability = ? WHERE user_id = ?", (availability, session["user_id"]))
        connect_db.commit()

        group_id = request.form.get("collab-group")

        # Get group name
        db.execute("SELECT name FROM groups WHERE group_id=?", (group_id,))
        group = db.fetchall()

        # Get number of members in group
        db.execute("SELECT members FROM groups WHERE group_id=?", (group_id,))
        members = db.fetchall()

        # Get user displayname and availability data to insert into collab table
        db.execute("SELECT displayname, availability FROM users WHERE user_id=?", (session["user_id"],))
        user_data = db.fetchall()

        # Check if previously collaborated availability with group
        db.execute("SELECT availability FROM collabs WHERE user_id=? AND group_id=?", (session["user_id"], group_id))
        check = db.fetchall()

        # Update collabs table
        if not check:
            db.execute("INSERT INTO collabs (group_id, user_id, displayname, availability) VALUES (?,?,?,?)",
                                            (group_id, session["user_id"], user_data[0][0], user_data[0][1]))
            connect_db.commit()
        else:
            db.execute("UPDATE collabs SET availability = ? WHERE group_id=? AND user_id=?",
                                                (user_data[0][1], group_id, session["user_id"]))
            connect_db.commit()

        # Get members who have collaborated with group
        db.execute("SELECT user_id, availability FROM collabs WHERE group_id=?", (group_id,))
        group_members_id = db.fetchall()

        names = []
        availabilities = []

        # Get names and availabilities of group members
        for i in range(len(group_members_id)):
            db.execute("SELECT displayname, availability FROM collabs WHERE group_id=? AND user_id=?", (group_id, group_members_id[i][0]))
            name_availability = db.fetchall()

            names.append(name_availability[0][0])
            availabilities.append(name_availability[0][1])

        total_members = int(members[0][0])
        collaborated_members = len(names)
        n = []
        name_groups = []
        collab_data = []
        a_count = 0

        # Collaborate and organize data for template
        for i in range(182):
            for j in range(collaborated_members):
                digit = availabilities[j][i]
                if digit == "1":
                    a_count = a_count + 1
                    n.append(names[j])
            if a_count == 0:
                name_groups.append(None)
                collab_data.append(0)
            else:
                name_groups.append(",".join(n))
                collab_data.append((a_count * 100) // total_members)
            a_count = 0
            del n[:]
        # return render_template("test.html", data1=name_groups, data2=collab_data)
        return render_template("collab.html", collab_data=collab_data, name_groups=name_groups, group=group[0][0])


@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    """Create group"""
    if request.method == "POST":

        name = request.form.get("group_name-create").replace(" ","")
        group = name.upper()
        code = request.form.get("group-code-create")

        # Check if group name and code combination exists
        db.execute("SELECT * FROM groups WHERE name=? AND code=?", (group, code))
        check = db.fetchall()

        if not check:
            # Update groups
            db.execute("INSERT INTO groups (name, code, members) VALUES (?,?,?)", (group, code, 1))
            connect_db.commit()

            db.execute("SELECT group_id FROM groups WHERE name=? AND code=?", (group, code))
            group_id = db.fetchall()

            # Update group_log
            db.execute("INSERT INTO group_log (group_id, user_id) VALUES (?,?)", (group_id[0][0], session["user_id"]))
            connect_db.commit()

            return redirect("/")
        else:
            flash("Sorry, group name and code combination already exist.")
            return redirect("/")
    else:
        return redirect("/")


@app.route("/join", methods=['GET', 'POST'])
@login_required
def join():
    """Join group"""
    if request.method == "POST":

        group = request.form.get("group_name-join").upper()
        code = request.form.get("group-code-join")

        # Check group name and code are correct
        db.execute("SELECT * FROM groups WHERE name=? AND code=?", (group, code))
        group_data = db.fetchall()

        if not group_data:
            flash("Group name or code was incorrect.")
            return redirect("/")

        # Check user isn't already in group
        db.execute("SELECT * FROM group_log WHERE group_id=? AND user_id=?", (group_data[0][0], session["user_id"]))
        check = db.fetchall()

        if not check:
            if not group_data:
                flash("Group name or code was incorrect")
                return redirect("/")
            else:
                # Update number of group members
                db.execute("UPDATE groups SET members = ? WHERE group_id = ?", (group_data[0][3] + 1, group_data[0][0]))
                connect_db.commit()

                # Update group_log
                db.execute("INSERT INTO group_log (group_id, user_id) VALUES (?,?)", (group_data[0][0], session["user_id"]))
                connect_db.commit()

                return redirect("/")
        else:
            return redirect("/")
    else:
        return redirect("/")


@app.route("/member", methods=['GET', 'POST'])
@login_required
def member():
    """Add member"""
    if request.method == "POST":

        member = request.form.get("add-member")
        group_id = request.form.get("group_id")

        # Get members user_id
        db.execute("SELECT user_id FROM users WHERE username=?", (member,))
        member_check = db.fetchall()

        if not member_check:
            flash("Username does not exist.")
            return redirect("/")
        else:
            # Check member isn't already in group
            db.execute("SELECT * FROM group_log WHERE group_id=? AND user_id=?", (group_id, member_check[0][0]))
            check = db.fetchall()

            if not check:
                # Get number of members in group
                db.execute("SELECT members FROM groups WHERE group_id=?", (group_id,))
                members = db.fetchall()

                # Update number of group members
                db.execute("UPDATE groups SET members = ? WHERE group_id = ?", (members[0][0] + 1, group_id))
                connect_db.commit()

                # Update group_log
                db.execute("INSERT INTO group_log (group_id, user_id) VALUES (?,?)", (group_id, member_check[0][0]))
                connect_db.commit()

                return redirect("/")
            else:
                flash("Already member")
                return redirect("/")
    else:
        return redirect("/")

@app.route("/leave", methods=['GET', 'POST'])
@login_required
def leave():
    """Leave group"""
    if request.method == "POST":

        group_id = request.form.get("leave")

        # Delete member record in group_log
        db.execute("DELETE FROM group_log WHERE group_id=? AND user_id=?", (group_id, session["user_id"]))
        connect_db.commit()

        db.execute("SELECT members FROM groups WHERE group_id=?", (group_id,))
        members = db.fetchall()
        # return render_template("test.html", data1=members, data2=group_id, data3=members[0][0])
        if members[0][0] == 1:
            # Delete group if no members left
            db.execute("DELETE FROM groups WHERE group_id=?", (group_id,))
            connect_db.commit()
        else:
            # Update number of group members
            db.execute("UPDATE groups SET members = ? WHERE group_id = ?", ((members[0][0] - 1), group_id))
            connect_db.commit()

        return redirect("/")


@app.route("/username", methods=['GET', 'POST'])
@login_required
def username():
    """Change username"""
    if request.method == "POST":
        name = request.form.get("username").replace(" ","")
        if not name:
            return redirect("/")
        else:
            db.execute("UPDATE users SET username = ? WHERE user_id = ?", (name, session["user_id"]) )
            connect_db.commit()

            return redirect("/")


@app.route("/displayname", methods=['GET', 'POST'])
@login_required
def displayname():
    """Change displayname"""
    if request.method == "POST":
        name = request.form.get("displayname").replace(" ","")
        if not name:
            return redirect("/")
        else:
            db.execute("UPDATE users SET displayname = ? WHERE user_id = ?", (name, session["user_id"]) )
            connect_db.commit()

            return redirect("/")


###################################################
####                             ##################
#####                           ###################
######  Login/logout/register  ####################
#####                           ###################
####                             ##################

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        displayname = request.form.get("displayname")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"),
                                method='pbkdf2:sha256', salt_length=8)

        db.execute("SELECT * FROM users WHERE username=?", (username,))
        result = db.fetchall()
        if not result:

            db.execute("INSERT INTO users (username, displayname, password, email) VALUES(?,?,?,?)", (username, displayname, password, email))
            connect_db.commit()

            db.execute("SELECT * FROM users WHERE username=?", (username,))
            data = db.fetchall()

            session["user_id"] = data[0][0]

            return redirect("/")
        else:
            message = "Username already exists"
            return render_template("register.html", message=message)
    else:
        return render_template("register.html", message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db.execute("SELECT * FROM users WHERE username=?", (username,))
        result = db.fetchall()
        if not result or not check_password_hash(result[0][3], password):
            message = "Login details incorrect"
            return render_template("login.html", message=message)
        else:
            session["user_id"] = result[0][0]
            return redirect("/")
    else:
        return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")