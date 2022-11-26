#-----------------------------------------------------------------------

### MODERATOR METHODS ###

#-----------------------------------------------------------------------

from database.strings import * 
from database.get_methods import *

#-----------------------------------------------------------------------

def delete_comment(client, commentid, postid):
   
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    comment_col = db[comment_collection_title]
    post_col = db[post_collection_title]
    
    # pull commentid from commentids list in user collection and post collection
    comment = get_comment(client, commentid)
    netid = comment[key_comment_user]
    user_col.update_one({'_id': netid}, {'$pull': {key_user_commentids: commentid}})
    post_col.update_one({'_id': postid}, {'$pull': {key_post_commentids: commentid}})

    # pull commentid from likedcommentids list in user collection
    userlike = comment[key_comment_userlike]
    for user in userlike:
        user_col.update_one({'_id': user}, {'$pull': {key_user_likedcommentids: commentid}})

    # delete comment from comment collection
    comment_col.delete_one({'_id': commentid})

#-----------------------------------------------------------------------

def delete_post(client, postid, groupid):

    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    group_col = db[group_collection_title]
    post_col = db[post_collection_title]

    # delete each comment under post
    post = get_post(client, postid)
    commentids = post[key_post_commentids]
    for commentid in commentids:
        delete_comment(client, commentid, postid)
    
    # pull postid from postids list in user collection and group collection
    netid = post[key_post_user]
    group_col.update_one({'_id': groupid}, {'$pull': {key_group_postids: postid}})
    user_col.update_one({'_id': netid}, {'$pull': {key_user_postids: postid}})

    # pull postid from likedpostids list in user collection
    userlike = post[key_post_userlike]
    for user in userlike:
        user_col.update_one({'_id': user}, {'$pull': {key_user_likedpostids: postid}})

    # delete post from post collection
    post_col.delete_one({'_id': postid})

#-----------------------------------------------------------------------

def delete_group(client, groupid):

     # get collection
    db = client[database_name]
    group_col = db[group_collection_title]

    # delete each post under group
    group = get_group(client, groupid)
    postids = group[key_group_postids]
    for postid in postids:
        delete_post(client, postid, groupid)

    # pull netid from netids list in users in group in user collection
    netids = group[key_group_netids]
    for netid in netids:
        remove_user_from_group(client, groupid, netid)  

    # delete group
    group_col.delete_one({'_id': groupid})

#-----------------------------------------------------------------------

def promote_to_moderator(client, groupid, netid):
   
    # update moderator list
    db = client[database_name]
    group_col = db[group_collection_title]
    group_col.update_one({'_id': groupid}, {'$push': {key_group_moderatorids: netid}})

#-----------------------------------------------------------------------

def demote_from_moderator(client, groupid, netid):
   
    # update moderator list
    db = client[database_name]
    group_col = db[group_collection_title]
    group_col.update_one({'_id': groupid}, {'$pull': {key_group_moderatorids: netid}})
    
#-----------------------------------------------------------------------

def add_user_to_group(client, groupid, netid):

    # get collection
    db = client[database_name]
    group_col = db[group_collection_title]
    user_col = db[user_collection_title]

    # update group table and user table
    group_col.update_one({'_id': groupid}, {'$push': {key_group_netids: netid}})
    user_col.update_one({'_id': netid}, {'$push': {key_user_groupids: groupid}})

#-----------------------------------------------------------------------
                    
def remove_user_from_group(client, groupid, netid):

    # get collection
    db = client[database_name]
    group_col = db[group_collection_title]
    user_col = db[user_collection_title]

    # update group table and user table
    group_col.update_one({'_id': groupid}, {'$pull': {key_group_netids: netid}})
    user_col.update_one({'_id': netid}, {'$pull': {key_user_groupids: groupid}})