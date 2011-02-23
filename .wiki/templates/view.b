inherits ( 'global' ) [
    override ('title') [
        droptags(file_title) if file_title else file_name
    ],
    override ( 'content' ) [
        include ('display_file')
    ],
    override ( 'menu' ) [
        a (href=urlescape(file_path) + '.edit') [ 'Edit' ],
    ]
]