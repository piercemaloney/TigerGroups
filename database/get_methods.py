#-----------------------------------------------------------------------

### GET METHODS ###

#-----------------------------------------------------------------------

from database.strings import (database_name, user_collection_title, 
                      comment_collection_title, post_collection_title, 
                      group_collection_title) 
import pymongo

#-----------------------------------------------------------------------

def get_comment(client, commentid):
    db = client[database_name]
    comment_table = db[comment_collection_title]
    comment = comment_table.find_one({"_id": commentid})
    return comment

def get_comments(client, commentids):
    db = client[database_name]
    comment_table = db[comment_collection_title]
    comment_list = list(comment_table.find({'_id': {'$in': commentids}}.sort('_id', -1)))
    return comment_list

#-----------------------------------------------------------------------

def get_post(client, postid):
    db = client[database_name]
    post_table = db[post_collection_title]
    post = post_table.find_one({"_id": postid})
    return post
    
def get_posts(client, postids):
    db = client[database_name]
    post_table = db[post_collection_title]
    post_list = list(post_table.find({"_id": {'$in' : postids}}).sort('_id', -1))
    return post_list
    
#-----------------------------------------------------------------------

def get_group(client, groupid):
    db = client[database_name]
    group_table = db[group_collection_title]
    group = group_table.find_one({"_id": groupid})
    return group

def get_groups(client, groupids):
    db = client[database_name]
    group_table = db[group_collection_title]
    group_list = list(group_table.find({"_id": {'$in' : groupids}}))
    return group_list

#-----------------------------------------------------------------------

def get_user_info(client, netid):
    db = client[database_name]
    user_table = db[user_collection_title]
    user_info = user_table.find_one({"_id": netid})
    return user_info

def get_user_infos(client, netids):
    db = client[database_name]
    user_table = db[user_collection_title]
    user_info_list = list(user_table.find({"_id": {'$in' : netids}}))
    return user_info_list