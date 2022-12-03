"use strict";

let request = null;
let post_id_del = "";
let user_id_rem = "";

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

//-------------------------

function delete_post(post_id) {
  console.log("delete_post for post id: " + post_id);
  let url = "/delete_post";
  if (request != null) request.abort();
  request = $.ajax({
    type: "POST",
    data: {
      post_id: post_id,
      group_id: getCookie("groupid"),
    },
    url: url,
    success: function () {
      $(posts_view).val("");
      getPosts(getCookie("groupid"));
    },
  });
}

//-------------------------

function delete_comment(comment__id, post_id) {
  console.log("delete_comment for comment id: " + comment__id);
  let url = "/delete_comment";

  if (request != null) request.abort();

  request = $.ajax({
    type: "POST",
    data: {
      post_id: post_id,
      comment_id: comment__id,
      group_id: getCookie("groupid"),
    },
    url: url,
    success: function () {
      $(comment__id).val("");
      get_comments(post_id);
    },
  });
}

//-------------------------

function remove_user_from_group(netid) {
  console.log("remove user from group: " + netid);
  let url = "/remove_user";

  if (request != null) request.abort();

  request = $.ajax({
    type: "POST",
    data: {
      netid: netid,
      group_id: getCookie("groupid"),
    },
    url: url,
    success: function () {
      $(posts_view).val("");
      getPosts(getCookie("groupid"));
    },
  });
}

//-------------------------

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

function handle_get_comments_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#" + post_id).html(data);
}

//-------------------------

function getPosts(id) {
  console.log("get posts with group_id:" + id);
  let url = "/get_posts?groupid=" + id;
  document.cookie = "groupid=" + id;

  if (request != null) request.abort();
  request = $.ajax({
    type: "GET",
    url: url,
    success: handleResponse,
  });
}

function handleResponse(response) {
  $("#posts_view").html(response);
}

//-------------------------

function setDeleteConfirmationPost(post_id) {
  console.log(post_id);
  post_id_del = post_id;
}

function setRemoveConfirmationUser(user_id) {
  console.log(user_id);
  user_id_rem = user_id;
}

//-------------------------

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

function handle_like_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#" + post_id).html(data);
}
//-------------------------

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function setup() {
  let id = getCookie("groupid");
  getPosts(id); // default post
}

$("document").ready(setup);
