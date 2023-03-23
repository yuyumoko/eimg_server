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
  //////////////////
  // 超分辨率插件
  
    var url = window.location.href;
    
    // sankakucomplex
    var sankakucomplex = /sankakucomplex.com(\/.+)?\/post\/show\/(\d+)/gm;
    var sankakucomplex_match = sankakucomplex.exec(url);
    if (sankakucomplex_match) {
        var highres = $("#highres")
        var orig_img_title = highres.html()
        var orig_img_url = highres.attr("href")

        var post_content = $("#post-content")

        var img_tool_html = `
        <style>
            .post-tools {
                padding: 0px 0px 10px 10px;
            }
            .post-tools button {
                margin-left: 5px;
                color: #ff761c;
            }
            .post-tools button:hover {
                background-color: #ffffe0;
            }
            #ncnn_result {
                padding: 0px 0px 10px 10px;
            }
        </style>
        <script application/javascript>
        $(function() {
            var highres = $("#highres")
            var orig_img_title = highres.html()
            var orig_img_url = 'https:' + highres.attr("href")
            
            window.ncnn_vulkan = function (scale) {
                
                $.post('${SERVER_URL}ncnn_vulkan', data={scale, url: orig_img_url}).then((result) => {
                    if (result.retcode == 0) {
                        var ncnn_status = $("#ncnn_status")
                        ncnn_status.html('状态: ' + result.msg)

                        var wait = window.setInterval(function () {
                            $.getJSON('${SERVER_URL}get_ncnn_vulkan_status/' + result.task_id).then((result) => {
                                if (result.retcode == 0) {
                                    ncnn_status.html('状态: ' + result.msg)
                                    if (result?.info) {
                                        window.clearTimeout(wait)
                                        var ncnn_info = $("#ncnn_info")
                                        ncnn_info.html('文件名: ' + result.info.name + '<br>文件大小: ' + result.info.size + '<br><a href=${SERVER_URL}' + 'ncnn_result_image/' + result.info.name + ' target="_blank">点击查看 ' + result.info.width + 'x' + result.info.height + ' (' + result.info.format + ')' + '</a>')
                                        
                                    }
                                    
                                    
                                }
                            })
                        }, 1000)
                        
                    }
                })
            }
            
        });
        </script>
        <div class="post-tools">
            <a href="${orig_img_url}" target="_blank">原图: ${orig_img_title}</a>
            <button id="ncnn_x2" onclick="window.ncnn_vulkan(2)">超分辨率放大 x2</button>
            <button id="ncnn_x4" onclick="window.ncnn_vulkan(4)">超分辨率放大 x4</button>
            <button id="ncnn_x8" onclick="window.ncnn_vulkan(8)">超分辨率放大 x8</button>
            <button id="ncnn_x16" onclick="window.ncnn_vulkan(2)">超分辨率放大 x16</button>
        </div>
        <div id="ncnn_result">
            <p id="ncnn_status"></p>
            <div id="ncnn_info"></div>
        </div>
        `
        post_content.before(img_tool_html)

    }

    


})();