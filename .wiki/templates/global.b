
html (lang='en') [
    head [
        meta (charset='UTF-8'),
        title [ slot('title'), ' - Plop' ],
        link (rel="stylesheet", type="text/css", media="screen", href="/.static/screen.css"),
        slot('head'),
    ],
    body [
        slot('menu'),
        slot('content'),
    ]
]
