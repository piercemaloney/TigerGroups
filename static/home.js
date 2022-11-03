'use strict';

function handleResponse(response) 
{
  $('#posts_view').html(response);
}

function new_post_submit(){
  
  console.log("submitting new post for group_id: "+state.current_group_id)
}

let state = {"current_group_id": "636344bcd77f507de97e277e"}
let request = null;
function getPosts(id) 
{
  let url = "/get_posts?groupid="+id

  if (request != null)
    request.abort();
  request = $.ajax(
    { 
      type:"GET",
      url:url,
      success:handleResponse,
    }
  );

  console.log("Get posts with groupid: "+id)
}


function setup()
{
  getPosts("636344bcd77f507de97e277e") // default post
}

$('document').ready(setup);
