#-----------------------------------------------------------------------

### POST METHODS ###

#-----------------------------------------------------------------------

from strings import * 

#-----------------------------------------------------------------------

def insert_comment(client, netid, postid, comment_content):
   
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    comment_col = db[comment_collection_title]
    post_col = db[post_collection_title]

    # add comment into comment collection
    comment = {
        key_comment_numlike: 0,
        key_comment_content: comment_content,
        key_comment_user: netid,
        key_comment_userlike: [],
        }
    commentid = comment_col.insert_one(comment).inserted_id
    
    # push commentid into commentids list in user collection and post collection
    user_col.update_one({'_id': netid}, {'$push': {key_user_commentids: commentid}})
    post_col.update_one({'_id': postid}, {'$push': {key_post_commentids: commentid}})

    return commentid
    
#-----------------------------------------------------------------------

def insert_post(client, netid, groupid, post_title, post_body):
   
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    group_col = db[group_collection_title]
    post_col = db[post_collection_title]

    # insert post into post collection
    post = {
        key_post_title: post_title, 
        key_post_body: post_body,
        key_post_commentids: [],
        key_post_numlike: 0,
        key_post_userlike: [],
        key_post_user: netid
        }
    postid = post_col.insert_one(post).inserted_id

    # update commentid into user collection and post collection
    user_col.update_one({'_id': netid}, {'$push': {key_user_postids: postid}})
    group_col.update_one({'_id': groupid}, {'$push': {key_group_postids: postid}})

    return postid

#-----------------------------------------------------------------------

def insert_group(client, netid, group_name, group_description, group_color):
    
    # get collection
    db = client[database_name]
    group_col = db[group_collection_title]
    user_col = db[user_collection_title]

    # insert group into group collection
    group = {
        key_group_name: group_name,
        key_group_description: group_description,
        key_group_color: group_color,
        key_group_netids: [netid],
        key_group_moderatorids: [netid],
        key_group_postids: []
        }
    groupid = group_col.insert_one(group).inserted_id

    # push groupid into groupids list in user collection
    user_col.update_one({'_id': netid}, {'$push': {key_user_groupids: groupid}})

    return groupid

#-----------------------------------------------------------------------

def insert_user(client, netid):
 
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    
    # insert new user into table
    new_user = {
        '_id': netid,
        key_user_commentids: [],
        key_user_groupids: [],
        key_user_postids: [],
        key_user_likedcommentids: [],
        key_user_likedpostids: [],
        }
    user_col.insert_one(new_user)

#-----------------------------------------------------------------------

def like_comment(client, netid, commentid):
 
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    comment_col = db[comment_collection_title]

    # update numlike in comment collection and likedcommentids in user collection
    comment_col.update_one({"_id": commentid}, {"$inc": {key_comment_numlike: 1}})
    comment_col.update_one({"_id": commentid}, {"$push": {key_comment_userlike: netid}})
    user_col.update_one({"_id": netid}, {"$push": {key_user_likedcommentids: commentid}})


def dislike_comment(client, netid, commentid):
 
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    comment_col = db[comment_collection_title]
    
    comment_col.update_one({"_id": commentid}, {"$inc": {key_comment_numlike: -1}})
    comment_col.update_one({"_id": commentid}, {"$pull": {key_comment_userlike: netid}})
    user_col.update_one({"_id": netid}, {"$pull": {key_user_likedcommentids: commentid}})

#-----------------------------------------------------------------------

def like_post(client, netid, postid):
 
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    post_col = db[comment_collection_title]

    # update numlike in comment collection and likedpostids in user collection
    post_col.update_one({"_id": postid}, {"$inc": {key_post_numlike: 1}})
    post_col.update_one({"_id": postid}, {"$push": {key_comment_userlike: netid}})
    user_col.update_one({"_id": netid}, {"$push": {key_user_likedpostids: postid}})

def dislike_post(client, netid, postid):
 
    # get collection
    db = client[database_name]
    user_col = db[user_collection_title]
    post_col = db[comment_collection_title]

    # update numlike in comment collection and likedpostids in user collection
    post_col.update_one({"_id": postid}, {"$inc": {key_post_numlike: -1}})
    post_col.update_one({"_id": postid}, {"$pull": {key_comment_userlike: netid}})
    user_col.update_one({"_id": netid}, {"$pull": {key_user_likedpostids: postid}})