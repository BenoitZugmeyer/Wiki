inherits ( 'global' ) [
    override ('title') [
        droptags(file_title) if file_title else file_name
    ],
    override ( 'content' ) [
        include ('display_file')
    ],
    override ( 'menu' ) [
        a (href=url(file_path, 'edit')) [ 'Edit' ], ' ︲ ',
        a (href=url(file_path, 'history')) [ 'History' ],
    ]
]
