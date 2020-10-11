fetch("http://194.67.110.56:5000/api/auth/step_2", {
    "headers": {
        "accept": "*/*",
        "accept-language": "ru,en;q=0.9",
        "content-type": "text/plain;charset=UTF-8"
    },
    "referrer": "http://0.0.0.0:5000/",
    "referrerPolicy": "no-referrer-when-downgrade",
    "body": "{\"user\":\"vahellame\",\"squares\":[[\"yellow\",4],[\"red\",1],[\"red\",2],[\"red\",2]]}",
    "method": "POST",
    "mode": "cors",
    "credentials": "omit"
});