function onClickOpen(_id, _progress, _class){
    fetch('/setProgress', {
    // Declare what type of data we're sending
    headers: {
      'Content-Type': 'application/json'
    },
    // Specify the method
    method: 'POST',
    // A JSON payload
    body: JSON.stringify({
        "progress": _progress,
        "class" : _class,
        "_id": _id

    })
    }).then(function (response) { // At this point, Flask has printed our JSON
        return response.text();
    }).then(function (text) {
    
    // Should be 'OK' if everything was successful
        return true;
    });
    
    
}



