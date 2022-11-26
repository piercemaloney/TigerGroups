#-----------------------------------------------------------------------

### TEST ###

#-----------------------------------------------------------------------

from database.post_methods import *
from database.moderator_methods import *
from database.get_methods import *
from database.strings import uri
from pymongo import MongoClient

#-----------------------------------------------------------------------

def test():
    client = MongoClient(uri)

    def print_collections(client, commentids, postid, groupid):
        print(get_comments(client, commentids))
        print("")
        print(get_post(client, postid))
        print("")
        print(get_group(client, groupid))
        print("")
        print(get_user_infos(client, ['user1', 'user2', 'user3']))
        print("")
        print("__________")
        print("")

    # create user1, 2, 3
    insert_user(client, 'user1')
    insert_user(client, 'user2')
    insert_user(client, 'user3')
    # user1 creates group
    groupid = insert_group(client, 'user1', 'Princeton University', "World's no. 1 University", 'orange')
    # user1 adds user2 and user3 to the group
    add_user_to_group(client, groupid, 'user2')
    add_user_to_group(client, groupid, 'user3')
    # user2 posts
    postid = insert_post(client, 'user2', groupid, 'Princeton Students', 'What are Princeton Students like?')
    # user1 and user3 comments
    commentids = []
    commentids.append(insert_comment(client, 'user1', postid, 'Smart'))
    commentids.append(insert_comment(client, 'user3', postid, 'Over-worked'))
    # makes user2 moderator
    promote_to_moderator(client, groupid, 'user2')
    # demote user1 from being moderator
    demote_from_moderator(client, groupid, 'user1')
    print_collections(client, commentids, postid, groupid)

    # delete group
    delete_group(client, groupid)
    print_collections(client, commentids, postid, groupid)
    # remove users
    db = client[database_name]
    user_col = db[user_collection_title]
    user_col.delete_many({"_id": {"$in": ['user1', 'user2', 'user3']}})
    print_collections(client, commentids, postid, groupid)

if __name__ == "__main__":
    test()   