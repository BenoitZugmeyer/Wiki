inherits ( 'global' ) [
    override ('title') [ 'Editing ', file_name ],
    override ( 'content' ) [
        h1 [ 'Edition of "', file_name, '"' ],
        test (file_content is not None) and div (id='preview') [
            include ('display_file'),
        ],
        form (id='editform', method='post', action=url(file_path, 'edit')) [
            textarea (name='content') [ content or '' ],
            input ( type='submit', name='preview', value='Preview' ),
            input ( type='submit', value='Submit' ),
        ],
    ],
    override ( 'menu' ) [
        a (href=url(file_path)) [ 'Back' ],
    ]
]
