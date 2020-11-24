var checkout = {};

$(document).ready(function() {
  var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

  $(window).load(function() {
    $messages.mCustomScrollbar();
    insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
  });

  function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
      scrollInertia: 100,
      timeout: 0
    });
  }

  function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
      m = d.getMinutes();
      $('<p class="small ml-3">' + d.getHours() + ':' + m + '</p>').appendTo($('.message:last'));
    }
  }

  function callChatbotApi(message) {
    // params, body, additionalParams
    return sdk.chatbotPost({}, {
      messages: [{
        type: 'unstructured',
        unstructured: {
          text: message
        }
      }]
    }, {});
  }

  function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
      return false;
    }
    d = new Date()
        if (m != d.getMinutes()) {
          m = d.getMinutes();
        }
    $('<div class="media col-md-9 col-xl-7 ml-auto mb-3"><div class="media-body mr-3"><div class="bg-primary rounded p-4 mb-2"><p class="text-sm mb-0 text-white">' + msg + '</p></div><p class="small ml-3">' + d.getHours() + ':' + m + '</p></div><img class="avatar avatar-border-white" src="https://d19m59y37dris4.cloudfront.net/directory/1-6/img/avatar/avatar-10.jpg" alt="user" /></div>').appendTo($('.mCSB_container')).addClass('new');
    $('.message-input').val('');
    updateScrollbar();

    callChatbotApi(msg)
      .then((response) => {
        console.log(response);
        var data = response.data;

        if (data.messages && data.messages.length > 0) {
          console.log('received ' + data.messages.length + ' messages');

          var messages = data.messages;

          for (var message of messages) {
            if (message.type === 'unstructured') {
              insertResponseMessage(message.unstructured.text);
            } else if (message.type === 'structured' && message.structured.type === 'product') {
              var html = '';

              insertResponseMessage(message.structured.text);

              setTimeout(function() {
                html = '<img src="' + message.structured.payload.imageUrl + '" width="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name + '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' + message.structured.payload.clickAction + '()">' +
                  message.structured.payload.buttonLabel + '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
          insertResponseMessage('Oops, something went wrong. Please try again.');
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.');
      });
  }

  $('.message-submit').click(function() {
    insertMessage();
  });

  $(window).on('keydown', function(e) {
    if (e.which == 13) {
      insertMessage();
      return false;
    }
  })

  function insertResponseMessage(content) {
    $('<div class="message loading new"><figure class="avatar"><img src="https://media1.tenor.com/images/672b62d967f8d00d608d22f36c1831db/tenor.gif" width="25px" height="25px" /></figure><span></span></div>').appendTo($('.mCSB_container'));
        updateScrollbar();

    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="media col-md-9 col-xl-7 mb-3"><img class="avatar avatar-border-white" src="https://d19m59y37dris4.cloudfront.net/directory/1-6/img/avatar/avatar-1.jpg" alt="user"><div class="message media-body ml-3"><div class="bg-gray-200 rounded p-4 mb-2"><p class="text-sm mb-0">' + content + '</p><p class="small ml-3">' + d.getHours() + ':' + m + '</p></div></div>').appendTo($('.mCSB_container')).addClass('new');

      updateScrollbar();
      i++;
    }, 500);
  }

});