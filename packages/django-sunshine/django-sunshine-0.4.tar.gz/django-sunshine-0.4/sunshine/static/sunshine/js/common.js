function ssajax(url, data, errorHandler){
    if (data === null || data === undefined){
        data = {}
   }
    if (!("csrfmiddlewaretoken" in data)){
        var csrf = $("meta[name='csrf-token']").attr('content');
        if (csrf.length) {
            data['csrfmiddlewaretoken'] = csrf;
        }
    }
    if (errorHandler === null || errorHandler === undefined){
        errorHandler = logError;
    }
    return $.ajax({url: url,
                   method: 'POST',
                   data: data,
                   dataType: 'jsonp'}).fail(errorHandler);
}

function logError(jqxhr){
    console.log("Server error", jqxhr);
}
