#-----------------------------------------------------------------------

### GET METHODS ###

#-----------------------------------------------------------------------

from strings import (database_name, user_collection_title, 
                      comment_collection_title, post_collection_title, 
                      group_collection_title) 
from bson.objectid import ObjectId

#-----------------------------------------------------------------------

def get_comment(client, commentid):
    commentid = ObjectId(commentid)
    db = client[database_name]
    comment_table = db[comment_collection_title]
    comment = comment_table.find_one({"_id": commentid})
    return comment

def get_comments(client, commentids):
    commentids = [ObjectId(id) for id in commentids]
    db = client[database_name]
    comment_table = db[comment_collection_title]
    comment_list = list(comment_table.find({'_id': {'$in': commentids}}))
    return comment_list

#-----------------------------------------------------------------------

def get_post(client, postid):
    postid = ObjectId(postid)
    db = client[database_name]
    post_table = db[post_collection_title]
    post = post_table.find_one({"_id": postid})
    return post
    
def get_posts(client, postids):
    postids = [ObjectId(id) for id in postids]
    db = client[database_name]
    post_table = db[post_collection_title]
    post_list = list(post_table.find({"_id": {'$in' : postids}}))
    return post_list
    
#-----------------------------------------------------------------------

def get_group(client, groupid):
    groupid = ObjectId(groupid)
    db = client[database_name]
    group_table = db[group_collection_title]
    group = group_table.find_one({"_id": groupid})
    return group

def get_groups(client, groupids):
    groupids = [ObjectId(id) for id in groupids]
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