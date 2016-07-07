$('#id_type').change(function(e){
    var form = $('#party-edit-form');
    var url = form.attr('action');
    var fData = form.serialize();
    var tokens = fData.split('&');
    var str = [];
    var crsftoken = '';
    for(var token in tokens){
        var kv = tokens[token].split('=');
        var k = kv[0];
        if (k.startsWith('attributes')){
            continue;
        }
        if (k == 'csrfmiddlewaretoken'){
            csrftoken = kv[1];
            continue;
        }
        var v = kv[1];
        str.push(k + '=' + v)
    }
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        url: url,
        data: str.join('&'),
        cache: false,
        contentType: 'application/x-www-form-urlencoded',
        type: 'POST',
        success: function(data){
            // location.reload();
        }
    });
});
