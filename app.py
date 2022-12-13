from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    render_template,
    make_response,
)

from cas import CASClient
import database.get_methods as get_methods
import database.post_methods as post_methods
import database.moderator_methods as moderator_methods
import database.strings as strings
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import helper

# -----------------------------------------------------------------------
# Setup

app = Flask(__name__)
app.secret_key = "V7nlCN90LPHOTA9PGGyf"  # placeholder
app.config["ENV"] = "development"
app.config["DEBUG"] = True
client = MongoClient(strings.uri)
SUCCESS = "200 OK"

PRINCETON_GROUP_ID = "638585e9048ae719be1cba4c"

# -----------------------------------------------------------------------
# Login Functions

cas_client = CASClient(
    version=3,
    service_url="https://tigergroups2.onrender.com/home",
    server_url="https://fed.princeton.edu/cas/",
)


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


@app.route("/set_default_cookie")
def set_default_cookie():
    response = make_response(redirect("/home"))
    response.set_cookie("groupid", PRINCETON_GROUP_ID)
    return response


@app.route("/permission_denied")
def permission_denied():
    return redirect(url_for("login"))


# -----------------------------------------------------------------------


@app.route("/home")
def home():
    # get groupid
    groupid = ObjectId(request.cookies.get("groupid"))
    # get user info
    netid = session["username"]
    # check if user is logging in for the first time, if yes call insert user
    user_info = get_methods.get_user_info(client, netid)
    if user_info == None:
        post_methods.insert_user(client, netid)
        user_info = get_methods.get_user_info(client, netid)
        moderator_methods.add_user_to_group(client, groupid, netid)

    # get information to display posts
    current_group = get_methods.get_group(client, groupid)
    groups = []
    if current_group is not None:
        groups = get_methods.get_groups(client, user_info[strings.key_user_groupids])
        if groups is None:
            groups = [PRINCETON_GROUP_ID]
    htmlcode = render_template("home.html", groups=groups, netid=netid, strings=strings)
    home_response = make_response(htmlcode)
    print(home_response)
    return htmlcode


# -----------------------------------------------------------------------


@app.route("/get_posts")
def get_posts():
    # get the query
    request_group_id = ObjectId(request.cookies.get("groupid"))

    # check if user is authorized
    is_user_valid = helper.is_user_in_group(request_group_id)
    if is_user_valid is False:
        return 'removing last user in group', 400

    # get information to display posts
    current_group = get_methods.get_group(client, ObjectId(request_group_id))
    posts = get_methods.get_posts(client, current_group[strings.key_group_postids])
    users = current_group[strings.key_group_netids]
    print("USERS:", users)

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
            posts[i]["date_created"] = str(round(time_delta / 60)) + " minutes ago"
        elif time_delta < 86400:
            posts[i]["date_created"] = str(round(time_delta / 3600)) + " hours ago"
        else:
            posts[i]["date_created"] = created.strftime("%B %d")

        # convert object id to str
        posts[i]["_id"] = str(posts[i]["_id"])

    is_member_moderator = {}
    for user in users:
        is_member_moderator[user] = helper.is_user_moderator(user, request_group_id)

    # check if user is moderator of group
    user_id = session["username"]
    is_moderator = helper.is_user_moderator(user_id, request_group_id)
    return render_template(
        "posts.html",
        current_group=current_group,
        posts=posts,
        users=users,
        strings=strings,
        key_post_date_created="date_created",
        is_moderator=is_moderator,
        is_member_moderator=is_member_moderator,
        user_id=user_id,
    )


# -----------------------------------------------------------------------


@app.route("/new_post", methods=["POST"])
def new_post():
    # get the values
    title, body, group_id = (
        request.form.get("title"),
        request.form.get("body"),
        request.form.get("group_id"),
    )

    print("title, body, group_id: ", title, body, group_id)

    # check if user is authorized
    is_user_valid = helper.is_user_in_group(group_id)
    if is_user_valid is False:
        return redirect(url_for("permission_denied"))

    post_methods.insert_post(
        client, session["username"], ObjectId(group_id), title, body
    )

    return redirect(url_for("home"))


# -----------------------------------------------------------------------


@app.route("/new_group", methods=["POST"])
def new_group():
    print("hi")
    # get the values
    group_name, description, color = (
        request.form.get("title"),
        request.form.get("description"),
        request.form.get("color"),
    )

    # default color is light bg with dark text
    if color == "":
        color = "bg-light text-dark"

    # if new group is empty
    if group_name == "" or description == "":
        return redirect(url_for("login"))

    post_methods.insert_group(
        client, session["username"], group_name, description, color
    )
    return redirect(url_for("login"))


# -----------------------------------------------------------------------


@app.route("/add_user", methods=["POST"])
def add_user():
    # get the values
    new_user = request.form.get("new_user")
    group_id = request.form.get("group_id")
    print("new_user, group_id: ", new_user, group_id)

    # if user doesn't exist return
    user_info = get_methods.get_user_info(client, new_user)
    if user_info == None:
        print("no user_info")
        return "user not found!", 400

    # if user in group already return
    if helper.is_new_user_in_group(group_id, new_user):
        print("is in group")
        return "user already in group", 400

    # otherwise add user to group
    moderator_methods.add_user_to_group(client, ObjectId(group_id), new_user)
    print(new_user)
    print(group_id)
    return redirect(url_for("login"))

# -----------------------------------------------------------------------

@app.route("/remove_user", methods=["POST"])
def remove_user():
    group_id = request.form.get("group_id")
    netid = request.form.get("netid")  # target
    user_id = session["username"]

    flag = True
    # verify user is moderator in group
    flag = flag and helper.is_user_moderator(user_id, group_id)
    if flag:
        print(group_id, netid)
        moderator_methods.remove_user_from_group(client, ObjectId(group_id), netid)
    return SUCCESS

# -----------------------------------------------------------------------

@app.route("/make_user_moderator", methods=["POST"])
def make_user_moderator():
    group_id = request.form.get("group_id")
    netid = request.form.get("netid")  # target
    user_id = session["username"]

    flag = True
    # verify user is moderator in group
    flag = flag and helper.is_user_moderator(user_id, group_id)
    if flag:
        print(group_id, netid)
        moderator_methods.promote_to_moderator(
            client, ObjectId(group_id), netid
        )

    return redirect(url_for("login"))

# -----------------------------------------------------------------------

@app.route("/make_user_normal", methods=["POST"])
def make_user_normal():
    group_id = request.form.get("group_id")
    netid = request.form.get("netid") # target
    user_id = session["username"]

    flag = True
    # verify user is moderator in group
    flag = flag and helper.is_user_moderator(user_id, group_id)
    if flag:
        print(group_id, netid)
        moderator_methods.demote_from_moderator(
            client, ObjectId(group_id), netid
        )

    return redirect(url_for("login"))

# -----------------------------------------------------------------------

@app.route("/get_comments", methods=["GET"])
def get_comments():
    # get the values
    post_id, group_id = "", request.cookies["groupid"]
    if request.args.get("post_id") is not None:
        post_id = request.args.get("post_id")
    user_id = session["username"]

    # if post is empty
    if post_id == "":
        return redirect(url_for("login"))

    flag = True
    # check if user is in group
    flag = flag and helper.is_user_in_group(group_id)
    # check if post is in group
    flag = flag and helper.is_post_in_group(post_id, group_id)

    is_moderator = helper.is_user_moderator(user_id, group_id)

    comment_ids = get_methods.get_post(client, ObjectId(post_id))[
        strings.key_post_commentids
    ]
    comments = get_methods.get_comments(client, comment_ids)
    
    for i in range(len(comment_ids)):
        # create date generation time field (date post was created)
        def utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

        today = datetime.datetime.now()
        created = utc_to_local(comments[i]["_id"].generation_time).replace(tzinfo=None)

        time_delta = (today - created).total_seconds()
        if time_delta < 60:
            comments[i]["date_created"] = str(round(time_delta)) + " seconds ago"
        elif time_delta < 3600:
            comments[i]["date_created"] = str(round(time_delta / 60)) + " minutes ago"
        elif time_delta < 86400:
            comments[i]["date_created"] = str(round(time_delta / 3600)) + " hours ago"
        else:
            comments[i]["date_created"] = created.strftime("%B %d")

        # convert object id to str
        comments[i]["_id"] = str(comments[i]["_id"])

    # show nothing if no comments
    if len(comments) == 0:
        return None

    
    return render_template(
        "comments.html",
        comments=comments,
        strings=strings,
        post_id=post_id,
        is_moderator=is_moderator,
        key_comment_date_created="date_created",
    )


# -----------------------------------------------------------------------


@app.route("/new_comment", methods=["POST"])
def new_comment():
    # get the values
    post_id = request.form.get("post_id")
    content = request.form.get("content")
    user_id = session["username"]

    post_methods.insert_comment(client, user_id, ObjectId(post_id), content)

    return SUCCESS


# -----------------------------------------------------------------------


@app.route("/like_post", methods=["POST"])
def like_post():
    # get the values
    post_id = request.form.get("post_id")
    user_id = session["username"]

    post_methods.like_post(client, user_id, ObjectId(post_id))
    post = get_methods.get_post(client, ObjectId(post_id))

    num_like = post[strings.key_post_numlike]

    return str(num_like)


# -----------------------------------------------------------------------

@app.route("/delete_post", methods=["POST"])
def delete_post():
    print("asdfsdfsdfdsfds")

    post_id = request.form.get("post_id")
    group_id = request.form.get("group_id")
    user_id = session["username"]
    print(post_id, ", ", group_id)

    # verify user is moderator of group
    flag = helper.is_user_moderator(user_id, group_id)

    # verify post belongs in group
    flag = helper.is_post_in_group(post_id, group_id) and flag

    if flag is True:
        moderator_methods.delete_post(client, ObjectId(post_id), ObjectId(group_id))
        return SUCCESS
    return

# -----------------------------------------------------------------------

@app.route("/delete_comment", methods=["POST"])
def delete_comment():
    comment_id = request.form.get("comment_id")
    group_id = request.form.get("group_id")
    user_id = session["username"]
    post_id = request.form.get("post_id")

    flag = True
    # verify comment is in post
    flag = flag and helper.is_comment_in_post(comment_id, post_id)
    # verify post is in group
    flag = flag and helper.is_post_in_group(post_id, group_id)
    # verify user is moderator in group
    flag = flag and helper.is_user_moderator(user_id, group_id)

    print(flag)
    if flag is True:
        print(comment_id, post_id)
        moderator_methods.delete_comment(
            client, ObjectId(comment_id), ObjectId(post_id)
        )
    return SUCCESS

# -----------------------------------------------------------------------

@app.route("/change_description", methods=["POST"])
def change_description():
    user_id = session["username"]
    group_id = request.form.get("group_id")
    des = request.form.get("des")
    print('asdfjasdjfha;sdad')
    print(des)
    flag = True
    # verify user is moderator in group
    flag = flag and helper.is_user_moderator(user_id, group_id)
    if flag is True:
        moderator_methods.change_group_description(client, ObjectId(group_id), des)

    return SUCCESS


# -----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)


