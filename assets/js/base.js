function error(data) {
    const message = $('<div class="alert alert-danger alert-message" style="display: none;">');
    const close = $('<button type="button" class="close" data-dismiss="alert">&times</button>');
    message.append(close);
    message.append(data);
    message.appendTo($('body')).fadeIn(400).delay(3000).fadeOut(400);
}

function success(data) {
    const message = $('<div class="alert alert-success alert-message" style="display: none;">');
    const close = $('<button type="button" class="close" data-dismiss="alert">&times</button>');
    message.append(close);
    message.append(data);
    message.appendTo($('body')).fadeIn(200).delay(1000).fadeOut(300);
}