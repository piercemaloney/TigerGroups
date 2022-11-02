#-----------------------------------------------------------------------

### DATABASE ###
# - database strings

#-----------------------------------------------------------------------

# Connection Information
database_name = "TigerGroups"
uri = ("mongodb+srv://testuser:1234@cluster0.jgjzgja.mongodb"
       ".net/?retryWrites=true&w=majority")

#-----------------------------------------------------------------------

# Collection Titles
user_collection_title = "user"
comment_collection_title = "comment"
post_collection_title = "post"
group_collection_title = "group"

#-----------------------------------------------------------------------

# User Collection's Keys
key_user_commentids = "commentids"
key_user_groupids = "groupids"
key_user_postids = "postids"
key_user_likedcommentids = "likedcommentids"
key_user_likedpostids = "likedpostids"

# Comment Collection's Keys
key_comment_numlike = "numlike" 
key_comment_content = "content"
key_comment_user = "user"
key_comment_userlike = "userlike"

# Post Collection's Keys
key_post_commentids = "commentids"
key_post_title = "title"
key_post_numlike = "numlike"
key_post_body = "body"
key_post_user = "user"
key_post_userlike = "userlike"

# Group Collection's Keys
key_group_netids = "netids"
key_group_postids = "postids" 
key_group_moderatorids = "moderatorids"
key_group_name = "name"
key_group_description = "description"  
key_group_color = "color"