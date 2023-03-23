// ==UserScript==
// @name         色图查重插件
// @namespace    esetu
// @version      0.3.2
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

    var default_tool_html = function (orig_img_title, orig_img_url) {
        return `
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
            window.ncnn_vulkan = function (scale) {
                $.post('${SERVER_URL}ncnn_vulkan', data={scale, url: "${orig_img_url}"}).then((result) => {
                    var ncnn_status = $("#ncnn_status")
                    var ncnn_info = $("#ncnn_info")
                    ncnn_status.html('状态: ' + result.msg)
                    ncnn_info.html('')
                    if (result.retcode == 0) {
                        var wait = window.setInterval(function () {
                            $.getJSON('${SERVER_URL}get_ncnn_vulkan_status/' + result.task_id).then((result) => {
                                if (result.retcode == 0) {
                                    ncnn_status.html('状态: ' + result.msg)
                                    if (result?.info) {
                                        window.clearTimeout(wait)
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
    }
    
    // sankakucomplex
    var sankakucomplex = /sankakucomplex.com(\/.+)?\/post\/show\/(\d+)/gm;
    var sankakucomplex_match = sankakucomplex.exec(url);
    if (sankakucomplex_match) {
        console.log('sankakucomplex image page')
        var highres = $("#highres")
        var orig_img_title = highres.html()
        var orig_img_url = 'https:' + highres.attr("href")

        var post_content = $("#post-content")

        post_content.before(default_tool_html(orig_img_title, orig_img_url))

    }

    // yande.re
    var yandere = /yande.re\/post\/show\/(\d+)/gm;
    var yandere_match = yandere.exec(url);

    // konachan
    var konachan = /konachan.com\/post\/show\/(\d+)/gm;
    var konachan_match = konachan.exec(url);

    if (yandere_match || konachan_match) {
        console.log('yande image page')
        var image = $("#image")
        var orig_img_width = image.attr("large_width")
        var orig_img_height = image.attr("large_height")
        var orig_img_url = $("#png").attr("href") || $("#highres").attr("href")
        var orig_img_size_regex = /.+(\(.+)/gm
        var orig_img_size = orig_img_size_regex.exec($("#png").html() || $("#highres").html())[1]
        var orig_img_title = orig_img_width + 'x' + orig_img_height + ' ' + orig_img_size

        image.before(default_tool_html(orig_img_title, orig_img_url))
    }

    // gelbooru
    var gelbooru = /gelbooru.com\/index.php\?page=post(\/.+)?/gm;
    var gelbooru_match = gelbooru.exec(url);

    //danbooru
    var danbooru = /danbooru.donmai.us\/posts\/(\d+)/gm;
    var danbooru_match = danbooru.exec(url);

    // safebooru
    var safebooru = /safebooru.donmai.us\/posts(\/.+)?/gm;
    var safebooru_match = safebooru.exec(url);

    if (gelbooru_match || danbooru_match || safebooru_match) {
        console.log('gelbooru image page')
        var image = $(".image-container")[0]
        var orig_img_width = image.getAttribute("data-width")
        var orig_img_height = image.getAttribute("data-height")
        var orig_img_url = $('[rel="noopener"]').attr('href') || $("#highres").attr('href') || image.getAttribute("data-file-url")
        var orig_img_ext = image.getAttribute("data-file-ext")?.substring(1)
        if (!orig_img_ext) {
            orig_img_ext = orig_img_url.split('.').pop()
        }
        var orig_img_title = orig_img_width + 'x' + orig_img_height + ' (' + orig_img_ext.toUpperCase() + ')'
        $(".image-container").before(default_tool_html(orig_img_title, orig_img_url))
    }

    // rule34
    var rule34 = /rule34.xxx\/index.php\?page=post(\/.+)?/gm;
    var rule34_match = rule34.exec(url);

    // xbooru
    var xbooru = /xbooru.com\/index.php\?page=post(\/.+)?/gm;
    var xbooru_match = xbooru.exec(url);
    
    if (rule34_match || xbooru_match) {
        console.log('rule34 image page')
        var image = $("#image")
        var orig_img_width = image.attr("width")
        var orig_img_height = image.attr("height")
        var orig_img_url = $("[property='og:image']").attr("content") || image.attr("src")
        var orig_img_title = orig_img_width + 'x' + orig_img_height + ' (' + orig_img_url.split('.').pop().toUpperCase().substring(0,3) + ')'
        image.before(default_tool_html(orig_img_title, orig_img_url))
    }
})();