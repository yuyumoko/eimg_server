// ==UserScript==
// @name         色图查重插件
// @namespace    esetu
// @version      0.3
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
// @match        *://*.iwara.tv/*
// @exclude      *://staging.iwara.tv/*
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// @run-at       document-end
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  var SERVER_URL = "http://127.0.0.1:7768/"


  var check_md5 = function (md5, element) {
      $.getJSON(SERVER_URL + 'check_md5/' + md5).then((result)=>{
          if(result.retcode == 0) {
              $(element).css("backgroundColor", "darkred")
              // .append(`<a href="file://${result.file}" target="_blank" style="float: left;word-break: break-all;">${result.file}</a>`)
          }
      })
  }

  var handler_arr = function (arr, callback) {
      for (var i = 0; i < arr.length; i++) {
          var src = $("img", arr[i]).attr("src");
          check_md5(callback(src), arr[i])
      }
  }

  var url2md5 = function (url) {
      var tmp = url.split("/");
      var filename = tmp[tmp.length - 1].split("?")[0].replace(/\..+/, "");
      var regex = /thumbnail_(\w+)/gm;
      var md5 = regex.exec(filename)
      return md5 ? md5[1] : filename
  }

  var gelbooru_hanlder = function (arr) { 
      console.log('gelbooru_hanlder')
      handler_arr(arr, function (src) {
          var regex = /thumbnail_(\w+)/gm;
          var md5 = regex.exec(src)
          if (md5) {
              return md5[1]
          }
      })
  }

  var sankakucomplex_handler = function (arr) {
      console.log('sankakucomplex_handler')
      handler_arr(arr, url2md5)
  }

  var danbooru_handler = function (arr) {
      console.log('danbooru_handler')
      handler_arr(arr, url2md5)
  }

  var gelbooru_list = $(".thumbnail-preview");
  var sankakucomplex_list = $(".thumb")
  var danbooru_list = $('.post-preview')

  if (gelbooru_list?.length) {
      gelbooru_hanlder(gelbooru_list)
  } else if (sankakucomplex_list?.length) {
      sankakucomplex_handler(sankakucomplex_list)
  } else if (danbooru_list?.length) {
      danbooru_handler(danbooru_list)
  }
  

})();