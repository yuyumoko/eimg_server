// ==UserScript==
// @name         色图查重插件
// @namespace    esetu
// @version      0.2
// @description  根据本地图片标记重复的图片背景红色
// @author       erinilis
// @include      *://yande.re/*
// @include      *://konachan.com/*
// @include      *://gelbooru.com/index.php?page=post*
// @include      *://danbooru.donmai.us/*
// @include      *://chan.sankakucomplex.com/*
// @include      *://idol.sankakucomplex.com/*
// @include      *://rule34.xxx/index.php?page=post*
// @include      *://xbooru.com/index.php*
// @include      *://safebooru.donmai.us/posts*
// @include      *://*.wjcodes.com/index.php*
// @match        *://*.iwara.tv/*
// @exclude      *://staging.iwara.tv/*
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @run-at       document-end
// @grant        none
// ==/UserScript==

(function () {
  "use strict";
  var gelbooru_list = $(".thumbnail-preview");
  var sankakucomplex_list = $(".thumb")
  var danbooru_list = $('.post-preview')
  var wjcodes = $('#main-list a')

  var SERVER_URL = "http://127.0.0.1:7768/"

  var arr = gelbooru_list.length ? gelbooru_list : sankakucomplex_list;
  if(!arr.length && danbooru_list.length) {
    arr = danbooru_list
  }
  if(!arr.length && wjcodes.length) {
    arr = wjcodes
  }

  for (let i = 0, len = arr.length; i < len; i++) {
    var src = $("img", arr[i]).attr("src");
    if(wjcodes.length) {
      src = $("img", arr[i]).attr("data-original");
    }

    var gelbooru_regex = /thumbnail_(\w+)/gm;
    var gelbooru = gelbooru_regex.exec(src)
    var md5 = "";
    if (gelbooru) {
      md5 = gelbooru[1];
    } else {
      var tmp = src.split("/");
      md5 = tmp[tmp.length - 1].split("?")[0].replace(/\..+/, "");
    }
    if(!md5) {
      console.log('获取md5失败 : ' + src)
    }
    $.getJSON(SERVER_URL + 'check_md5/' + md5).then((result)=>{
        if(result.retcode == 0) {
            console.log(result.file, arr[i]);
            $(arr[i]).css("backgroundColor", "darkred")
                // .append(`<a href="file://${result.file}" target="_blank" style="float: left;word-break: break-all;">${result.file}</a>`)
        }
    })

  }
  // iwara
  var iwara_list = $('.field-item.even a')
  if (iwara_list.length > 0) {
    for (let i = 0, len = iwara_list.length; i < len; i++) {
        try {
            var id = iwara_list[i].href.match(/videos\/(\w+)/)[1]
            $.getJSON(SERVER_URL + 'check_md5/' + id).then((result)=>{
                if(result.retcode == 0) {
                    //console.log(result.file, iwara_list[i]);
                    $(iwara_list[i]).parents('.views-column').css("backgroundColor", "darkred");
                }
            })
        }
        catch(err) {
            console.log(err);
        }
    }
  }

})();