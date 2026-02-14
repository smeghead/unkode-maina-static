var unkode_icon_org = '<div class="unkode-icon nuclear-icon" title="臭ったらクリック!"></div>';
var unkode_icon = '<div class="unkode-icon" data-smell_id="$id" dta-screen_name="$screen_name" title="$screen_name"></div>';

$(function(){
  var remove_smell = function(){
    var smell = $(this);
    var smell_id = smell.data('smell_id');
    
    $('#remove-smell').unbind('click').click(function(){
      var body = $('body');
      var scroll_pos = body.scrollTop();
      $.ajax({
        url: '/smell_remove/' + smell_id,
        type: 'post',
        success: function(data){
          smell.remove();
          $('#modal-remove-smell').modal('hide');
          body.scrollTop(scroll_pos);
        },
        error: function(xhr){
          alert(xhr.responseText);
        }
      });
    });
    $('#modal-remove-smell').modal();
    return;

  };

  var max_height = 0;
  if ($('#mobile').val() == "1") {
    $('.hero-unit h1').css('font-size', '20pt');
    $('.famous-sentence').css('width', '100%');
    $('#top-carousel .item')
      .show();
  } else {
    $('.carousel-control').show();
    $('#top-carousel .item').css('padding', '3px 50px').map(function(){
      max_height = Math.max($(this).height(), max_height);
    });

    $('#top-carousel').height(max_height).carousel();

    $('#signout').click(function(){
      $('#signout-form').submit();
    });
  }

  $('.register-link').click(function(){
    if (!screen_name) {
      $('#needs-auth-modal').modal();
      return false;
    }
    return true;
  });

  $('.sidebar-nav li').each(function(){
    var li = $(this);
    var url_match = li.data('url_match');
    if (!url_match) return;
    if (document.location.pathname.match(url_match)) {
      li.addClass('active');
    } else {
      li.removeClass('active');
    }
  });

  PR.prettyPrint();
  var lines = $('li.L0,li.L1,li.L2,li.L3,li.L4,li.L5,li.L6,li.L7,li.L8,li.L9');
  lines.append($('<span class="right">' + unkode_icon_org + '</span><br clear="all"/>'));
  
  if (typeof(smell_json) != 'undefined') {
    var smell_infos = $(JSON.parse(smell_json));
    lines.each(function(){
      var li = $(this);
      var line = lines.index(li);
      var smells = smell_infos.filter(function(){
        return this.line == line;
      });

      for (var i = 0; i < smells.length; i++) {
        var smell = smells[i];
        console.log(smell);
        var unk = $(unkode_icon
            .replace(/\$screen_name/g, smell.author.screen_name)
            .replace(/\$id/g, smell.id));
        if (screen_name == smell.author.screen_name) {
          unk.css('cursor', 'pointer').click(remove_smell);
        }
        $('.nuclear-icon', li).after(unk);
      }
    });
  }
  
  $('.nuclear-icon')
    .mouseover(function(){$(this).parents('li').addClass('selected-row');})
    .mouseout(function(){$(this).parents('li').removeClass('selected-row');});
  $('.nuclear-icon').click(function(){
    if (!screen_name) {
      $('#needs-auth-modal').modal();
      return;
    }
    var icon = $(this);
    var lis = $('li', icon.parents('ol'));
    var li = icon.parents('li');
    var id = $('#code-info').data('id');
    var line = lis.index(li);

    var body = $('body');
    var default_cursor = body.css('cursor');
    body.css('cursor', 'wait');
    try {
      $.ajax({
        url: '/smell/' + id + '/' + line,
        type: 'post',
        dataType: 'json',
        success: function(data){
          console.log(data);
          var unk = $(unkode_icon
              .replace(/\$screen_name/g, screen_name)
              .replace(/\$id/g, data.id));
          unk.css('cursor', 'pointer').click(remove_smell);
          icon.after(unk);
        },
        error: function(xhr){
          alert(xhr.responseText);
        }
      });
    } finally {
      body.css('cursor', default_cursor);
    }
  });

  //toggle unko icons.
  var toggle_button = $('<div class="unko-toggle-button hide" data-display="block" data-visible="ウンコを非表示" data-hide="ウンコを表示"></div>');
  toggle_button.click(function(){
    $('.unkode-icon').toggle();
    display_unko = !display_unko;
  });
  var display_unko = true;
  var get_width = function(elem){
    return new Number(elem.css('width').replace(/[a-z]/gi, ''));
  };
  var timer;
  $('.view .prettyprint')
    .append(toggle_button)
    .mouseover(function(){
      var pre = $(this);
      var position = pre.position();
      toggle_button
        .text(toggle_button.data(display_unko ? 'visible' : 'hide'))
        .css('top', position.top - 30)
        .css('left', position.left + get_width(pre) - get_width(toggle_button) - 50)
        .removeClass('hide');
      if (typeof(timer) == 'undefined') {
        timer = setTimeout(function(){
          toggle_button.addClass('hide');
          timer = undefined;
        }, 5000);
      }
    });

  $('#preview').click(function(){
    var preview_div = $('#preview-div');
    if (preview_div.is(':visible')) {
      preview_div.hide();
      $('#comment').unbind('change');
      return;
    }
    preview_div.show();
    var update_preview = function(){
      $.ajax({
        url: '/comment_preview',
        type: 'post',
        dataType: 'json',
        data: {comment: $('#comment').val()},
        success: function(data){
          if (data.result != 'ok') {
            alert(data.error);
            return;
          }
          preview_div.html(data.html);
        },
        error: function(xhr){
          alert(xhr.responseText);
        }
      });
    };
    update_preview();
    $('#comment').change(update_preview);
  });

  $('#more-code').click(function(){
    var button = $(this);
    $.ajax({
      url: '/more_code',
      data: {
        type: $('#type').data('value'),
        page: button.data('page') + 1
      },
      success: function(data){
        if (data.no_more) {
          button.hide();
        }
        button.data('page', button.data('page') + 1);
        $(data.codes).each(function(){
          var code = $('#tmpl-code').tmpl(this).appendTo('#codes');
        });
        twttr.widgets.load();
        prettyPrint();
      },
      error: function(xhr){
        alert(xhr.responseText);
      }
    });
  });

  var already_submited = false;

  $('#comment').focus(function(){$('#comment-action').show('fast');});
  $('#comment-form').submit(function(){
    if (!already_submited) {
      already_submited = true;
      return true;
    }
    return false;
  });

  //ウンコードの登録
  $('#code-register-form').submit(function(){
    if (!already_submited) {
      already_submited = true;
      return true;
    }
    return false;
  });
  //ウンコードの削除
  $('#remove-code').click(function(){
    $('#remove-code-form').submit();
  });
  $('#remove-code-button').click(function(){
    $('#modal-remove-code').modal();
  });
  //コメントの削除
  $('#remove-comment').click(function(){
    var comment_id = $(this).data('comment_id');
    $.ajax({
      type: 'post',
      url: '/remove_comment/' + comment_id,
      success: function(){
        $('#comment-' + comment_id).hide('fast');
        $('#modal-remove-comment').modal('hide');
      },
      error: function(xhr){
        alert(xhr.responseText);
      }
    });
  });
  $('.remove-comment-button').click(function(){
    $('#remove-comment').data('comment_id', $(this).data('comment_id'));
    $('#modal-remove-comment').modal();
  });

  $('.rss-icon').click(function(){
    $('#modal-rss').modal();
    $('#rss-feed').select();
    return false;
  });

  //未読タイトルのマーク
  if (typeof(localStorage) != 'undefined') {
    var readsString = localStorage.getItem('reads');
    var reads = [];
    if (readsString) {
      reads = JSON.parse(readsString);
    }
    $('a.title').each(function(){
      var link = $(this).attr('href');
      var id = link && link.replace(/^\/view\/([^\/\?\#]+).*/, '$1');
      if ($(reads).filter(function(){return this == id;}).size() > 0) {
        return;
      }
      $(this).parent().children(':first-child').before($('<span class="unread" title="未読ウンコード">*</span>'));
    });
    //既読にする
    var id = $('#code-info').data('id');
    if (id) {
      reads.push(id);
      localStorage.setItem('reads', JSON.stringify(reads));
    }
  }
});
// # vim: set ts=2 sw=2 sts=2 expandtab fenc=utf-8:
