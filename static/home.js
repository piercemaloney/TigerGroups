"use strict";

let request = null;
let post_id_del = "";
let user_id_rem = "";
let comment_on = false;

//-------------------------

$(".btn-close").click(function () {
  $(".warning").css("visibility", "hidden");
});

//-------------------------

function edit_description(des) {
  console.log("des");
  $("#EditDes textarea").text(des);
}

function change_description() {
  let description = $("#EditDes textarea").val();
  console.log(description);
  let url = "/change_description";

  if (description === "") {
    $(".warning").css("visibility", "visible");
  } else {
    request = $.ajax({
      type: "POST",
      data: {
        group_id: getCookie("groupid"),
        des: description,
      },
      url: url,
      success: function () {
        $("#EditDes").modal("toggle");
        getPosts(getCookie("groupid"));
      },
    });
  }
}

//-------------------------

function new_comment(post_id) {
  console.log("new comment for post id: " + post_id);
  let url = "/new_comment";
  let content = $("#new_comment_id").val();
  console.log("new comment: content: " + content);

  if (content === "") {
    $(".warning").css("visibility", "visible");
  } else {
    if (request != null) request.abort();
    request = $.ajax({
      type: "POST",
      data: {
        post_id: post_id,
        content: content,
      },
      url: url,
      success: function () {
        $("#AddComment input").val("");
        $("#AddComment").modal("toggle");
        $("#new_comment_id").val("");
        comment_on = false;
        get_comments(post_id);
      },
    });
  }
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

function delete_comment(comment_id, post_id) {
  console.log("delete_comment for comment id: " + comment_id);
  let url = "/delete_comment";

  if (request != null) request.abort();

  request = $.ajax({
    type: "POST",
    data: {
      post_id: post_id,
      comment_id: comment_id,
      group_id: getCookie("groupid"),
    },
    url: url,
    success: function () {
      $(comment_id).val("");
      comment_on = false;
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

function make_user_moderator(netid) {
  console.log("making user moderator: " + netid);
  let url = "/make_user_moderator";

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

function make_user_normal(netid) {
  console.log("making user normal: " + netid);
  let url = "/make_user_normal";

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
  if (comment_on) {
    comment_on = false;
    $("#" + post_id).empty();
  } else {
    let url = "/get_comments?post_id=" + post_id;
    if (request != null) request.abort();
    request = $.ajax({
      type: "GET",
      url: url,
      success: function (data) {
        handle_get_comments_response(data, post_id);
        comment_on = true;
      },
    });
  }
}

function handle_get_comments_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#" + post_id).html(data);
}

//-------------------------

function getPosts(id) {
  console.log("get posts with group_id:" + id);
  let url = "/get_posts?groupid=" + id;
  $("#" + getCookie("groupid")).removeClass("border-3");
  document.cookie = "groupid=" + id;
  $("#" + id).addClass("border-3");

  if (request != null) request.abort();
  request = $.ajax({
    type: "GET",
    url: url,
    success: handleResponse,
    error: function () {
      document.cookie = "groupid=638585e9048ae719be1cba4c";
      location.reload();
    },
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
    success: function (data){
      handle_like_response(data, post_id)
    },
  });
}

function handle_like_response(data, post_id) {
  console.log("got reponse post_id= " + post_id);
  $("#num_like"+post_id).html(data+" likes");
}

//-------------------------

function newPost() {
  let title = $("#post-title").val();
  let body = $("#post-body").val();
  let url = "/new_post";

  if (body === "" || title === "") {
    $(".warning").css("visibility", "visible");
  } else {
    if (request != null) request.abort();
    request = $.ajax({
      type: "POST",
      data: {
        title: title,
        body: body,
        group_id: getCookie("groupid"),
      },
      url: url,
      success: function () {
        $("#NewPost input").val("");
        $("#NewPost textarea").val("");
        $("#NewPost").modal("toggle");
        $(".warning").css("visibility", "hidden");
        setup();
      },
    });
  }
}
//-------------------------

function newUser() {
  let new_user = $("#new_user_id").val();
  let url = "/add_user";

  if (request != null) request.abort();
  request = $.ajax({
    type: "POST",
    data: {
      new_user: new_user,
      group_id: getCookie("groupid"),
    },
    url: url,
    success: function () {
      $("#AddUser input").val("");
      $("#AddUser").modal("toggle");
      $(".warning").css("visibility", "hidden");
      setup();
    },
    error: function (error) {
      $("#warning_user").text(error.responseText);
      $("#warning_user").css("visibility", "visible");
      console.log(error.responseText);
    },
  });
}

//-------------------------

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function setup() {
  let id = getCookie("groupid");
  console.log("id");
  console.log("yoyoyo");
  getPosts(id); // default post
}

$("document").ready(setup);
