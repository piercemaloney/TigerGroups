from flask import Flask, request, session, redirect, url_for, render_template
from cas import CASClient
import database.get_methods as get_methods
import database.post_methods as post_methods
import database.moderator_methods as moderator_methods
import database.strings as strings
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


app = Flask(__name__)
app.secret_key = "V7nlCN90LPHOTA9PGGyf"  # placeholder
app.config["ENV"] = "development"
app.config["DEBUG"] = True

cas_client = CASClient(
    version=3,
    service_url="http://localhost:5000/login?next=%2Fhome",
    server_url="https://fed.princeton.edu/cas/",
)


client = MongoClient(strings.uri)
SUCCESS = "200 OK"


def is_user_in_group(user_group_id):
    # check if user is authorized
    user_group_ids = get_methods.get_user_info(client, session["username"])[
        strings.key_user_groupids
    ]
    flag = False
    for group_id in user_group_ids:
        if group_id == ObjectId(user_group_id):
            flag = True
    return flag


@app.route("/")
def index():
    return login()


@app.route("/login")
def login():
    if "username" in session:
        # Already logged in
        return redirect(url_for("home"))

    next = request.args.get("next")
    ticket = request.args.get("ticket")
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        app.logger.debug("CAS login URL: %s", cas_login_url)
        return redirect(cas_login_url)

    # There is a ticket, the request come from CAS as callback.
    # need call `verify_ticket()` to validate ticket and get user profile.
    app.logger.debug("ticket: %s", ticket)
    app.logger.debug("next: %s", next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    app.logger.debug(
        "CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s",
        user,
        attributes,
        pgtiou,
    )

    if not user:
        return 'Failed to verify ticket. <a href="/login">Login</a>'
    else:  # Login successfully, redirect according `next` query parameter.
        session["username"] = user
        return redirect(next)


@app.route("/logout")
def logout():
    redirect_url = url_for("logout_callback", _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    app.logger.debug("CAS logout URL: %s", cas_logout_url)

    return redirect(cas_logout_url)


@app.route("/logout_callback")
def logout_callback():
    # redirect from CAS logout request after CAS logout successfully
    session.pop("username", None)
    return 'Logged out from CAS. <a href="/login">Login</a>'


@app.route("/profile")
def profile(method=["GET"]):
    if "username" in session:
        return 'Logged in as %s. <a href="/logout">Logout</a>' % session["username"]
    return 'Login required. <a href="/login">Login</a>', 403


@app.route("/home")
def home():
    # get groupid
    groupid = ObjectId("636344bcd77f507de97e277e")

    # get user info
    netid = session["username"]
    print(netid)

    # check if user is logging in for the first time, if yes call insert user
    user_info = get_methods.get_user_info(client, netid)
    if user_info == None:
        post_methods.insert_user(client, netid)
        user_info = get_methods.get_user_info(client, netid)

    # get information to display posts
    current_group = get_methods.get_group(client, groupid)
    groups = get_methods.get_groups(client, user_info[strings.key_user_groupids])
    posts = get_methods.get_posts(client, current_group[strings.key_group_postids])

    return render_template(
        "home.html", posts=posts, groups=groups, groupid=groupid, strings=strings
    )

@app.route("/get_posts")
def get_posts():
    # get the query
    request_group_id = "Princeton University"
    if request.args.get("groupid") is not None:
        request_group_id = request.args.get("groupid")

    # check if user is authorized
    is_user_valid = is_user_in_group(request_group_id)
    if is_user_valid is False:
        return redirect(url_for("permission_denied"))

    # get information to display posts
    current_group = get_methods.get_group(client, ObjectId(request_group_id))
    posts = get_methods.get_posts(client, current_group[strings.key_group_postids])
    users = current_group[strings.key_group_netids]

    for i in range(len(posts)):

        # create date generation time field (date post was created)
        def utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        today = datetime.datetime.now()
        created = utc_to_local(posts[i]["_id"].generation_time).replace(tzinfo=None) 

        time_delta = (today - created).total_seconds()
        if time_delta < 60:
            posts[i]["date_created"] = str(round(time_delta)) + " seconds ago"
        elif time_delta < 3600:
            posts[i]["date_created"] = str(round(time_delta/60)) + " minutes ago"
        elif time_delta < 86400:
            posts[i]["date_created"] = str(round(time_delta/3600)) + " hours ago"
        else:
            posts[i]["date_created"] = created.strftime('%B %d')

        # convert object id to str
        posts[i]["_id"] = str(posts[i]["_id"])
    
    return render_template("posts.html", posts=posts, users=users, strings=strings, key_post_date_created = "date_created")


@app.route("/permission_denied")
def permission_denied():
    return redirect(url_for("login"))


@app.route("/new_post")
def new_post():
    # get the values
    title, body, group_id = "", "", ""
    if request.args.get("title") is not None:
        title = request.args.get("title")
    if request.args.get("body") is not None:
        body = request.args.get("body")
    if request.args.get("group_id") is not None:
        group_id = request.args.get("group_id")

    print("title, body, group_id: ", title, body, group_id)

    # if post is empty
    if title == "" or body == "" or group_id == "":
        return redirect(url_for("login"))

    # check if user is authorized
    is_user_valid = is_user_in_group(group_id)
    if is_user_valid is False:
        return redirect(url_for("permission_denied"))

    post_methods.insert_post(
        client, session["username"], ObjectId(group_id), title, body
    )
    return redirect(url_for("login"))

@app.route("/new_group")
def new_group():
    print("hi")
    # get the values
    group_name, description, color = "", "", ""
    if request.args.get("title") is not None:
        group_name = request.args.get("title")
    if request.args.get("description") is not None:
        description = request.args.get("description")
    if request.args.get("color") is not None:
        color = request.args.get("color")
    else:
        # default color is light bg with dark text
        color = "bg-light text-dark"

    # if new group is empty
    if group_name == "" or description == "":
        return redirect(url_for("login"))

    print("asdf")
    post_methods.insert_group(
        client, session["username"], group_name, description, color
    )
    return redirect(url_for("login"))

@app.route("/add_user")
def add_user():
    print("hi")
    # get the values
    new_user = ""
    if request.args.get("new_user") is not None:
        new_user = request.args.get("new_user")
    if request.args.get("group_id") is not None:
        group_id = request.args.get("group_id")
    print("new_user, group_id: ", new_user, group_id)

    # if user doesn't exist return
    user_info = get_methods.get_user_info(client, new_user)
    if user_info == None:
        return redirect(url_for("login"))

    # otherwise add user to group
    moderator_methods.add_user_to_group(client, ObjectId(group_id), new_user)
    print(new_user)
    print(group_id)
    return redirect(url_for("login"))


@app.route("/get_comments", methods=["GET"])
def get_comments():
    # get the values
    post_id, group_id = "", ""
    if request.args.get("post_id") is not None:
        post_id = request.args.get("post_id")
    print(post_id)

    # if post is empty
    if post_id == "":
        return redirect(url_for("login"))

    # check if user is authorized
    # is_user_valid = is_user_in_group(group_id)
    # if is_user_valid is False:
    #    return redirect(url_for("permission_denied"))

    comment_ids = get_methods.get_post(client, ObjectId(post_id))[
        strings.key_post_commentids
    ]
    for i in range(len(comment_ids)):
        comment_ids[i] = ObjectId(comment_ids[i])
    comments = get_methods.get_comments(client, comment_ids)
    return render_template(
        "comments.html", comments=comments, strings=strings, post_id=post_id
    )


@app.route("/new_comment", methods=["POST"])
def new_comment():
    # get the values
    post_id = request.form.get("post_id")
    content = request.form.get("content")
    user_id = session["username"]

    post_methods.insert_comment(client, user_id, ObjectId(post_id), content)

    return SUCCESS

@app.route("/like_post", methods=["POST"])
def like_post():
    # get the values
    post_id = request.form.get("post_id")
    user_id = session["username"]

    post_methods.like_post(client, user_id, ObjectId(post_id))

    return SUCCESS

if __name__ == "__main__":
    app.run(debug=True)
