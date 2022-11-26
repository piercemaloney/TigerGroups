"use strict";

let request = null;

function handleResponse(response) {
  $("#posts_view").html(response);
}

function new_comment(post_id) {
  console.log("new comment for post id: " + post_id);
  let url = "/new_comment";
  let text_area_id = "#" + "comment_content_" + post_id;
  let content = $(text_area_id).val();
  console.log("new comment: content: " + content);

  if (request != null) request.abort();

  request = $.ajax({
    type: "POST",
    data: {
      post_id: post_id,
      content: content,
    },
    url: url,
    success: function () {
      $(text_area_id).val("");
      get_comments(post_id);
    },
  });
}

function handle_get_comments_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#" + post_id).html(data);
}

function get_comments(post_id) {
  let url = "/get_comments?post_id=" + post_id;
  console.log("getting comment with post_id = " + post_id);
  if (request != null) request.abort();
  request = $.ajax({
    type: "GET",
    url: url,
    success: function (data) {
      handle_get_comments_response(data, post_id);
    },
  });
}

function new_post_submit() {
  console.log("submitting new post for group_id: " + state.current_group_id);
}

let state = { current_group_id: "636344bcd77f507de97e277e" };

function getPosts(id) {
  let url = "/get_posts?groupid=" + id;

  if (request != null) request.abort();
  request = $.ajax({
    type: "GET",
    url: url,
    success: handleResponse,
  });

  console.log("Get posts with groupid: " + id);
}

function handle_like_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#" + post_id).html(data);
}

function likePost(post_id) {
  let url = "/like_post";

  if (request != null) request.abort();
  request = $.ajax({
    type: "POST",
    data: {
      post_id: post_id,
    },
    url: url,
    success: handle_like_response,
  });
}

function setup() {
  getPosts("636344bcd77f507de97e277e"); // default post
}

$("document").ready(setup);
