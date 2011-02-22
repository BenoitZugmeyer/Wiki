inherits ( 'global' ) [
    override ('title') [ 'Editing ', file_name ],
    override ( 'content' ) [
        h1 [ file_name ],
        form (id='editform', method='post', action=urlescape(file_path)+'.edit') [
            textarea (name='content') [ file_content ],
            input ( type='submit', value='Submit' ),
        ],
    ],
    override ( 'menu' ) [
        a (href=urlescape(file_path)) [ 'Back' ],
    ]
]
