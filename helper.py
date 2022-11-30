from flask import Flask, request, session, redirect, url_for, render_template
from cas import CASClient
import database.get_methods as get_methods
import database.post_methods as post_methods
import database.moderator_methods as moderator_methods
import database.strings as strings
from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient(strings.uri)


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


def is_user_moderator(user_id, group_id):
    moderator_ids = get_methods.get_group(client, ObjectId(group_id))[
        strings.key_group_moderatorids
    ]
    flag = False
    for moderator_id in moderator_ids:
        if moderator_id == user_id:
            flag = True
    return flag


def is_post_in_group(post_id, group_id):
    post_ids = get_methods.get_group(client, ObjectId(group_id))[
        strings.key_group_postids
    ]
    flag = False
    for curr_post_id in post_ids:
        if curr_post_id == ObjectId(post_id):
            flag = True
    return flag


def is_comment_in_post(comment_id, post_id):
    comment_ids = get_methods.get_post(client, ObjectId(post_id))[
        strings.key_post_commentids
    ]
    flag = False
    for curr_comment_id in comment_ids:
        if curr_comment_id == ObjectId(comment_id):
            flag = True
    return flag
