inherits ('global') [
    override ('title') [ 'Error' ],
    override ('content') [
        h1 [ 'Error' ],
        message,
        test (exception) and pre (class_='error') [ exception ]
    ]
]
