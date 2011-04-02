macro('entry', lambda h, idx:
    [
        format_date(h.mtime), ', ', format_size(h.size), ' ',
        #a ( href=url(file_path, ['history', 'see', str(idx)])) ['see'], ' ',
        #a ( href=url(file_path, ['history', 'diff', str(idx)])) ['diff'],
        test(idx == 0) and ' (current version)'
    ]
),
inherits ( 'global' ) [
    override ('title') [ 'History of ', file_name ],
    override ( 'content' ) [
        h1 [ 'History of "', file_name, '"' ],
        ul [
            li [ entry(file, 0) ],
            [li [ entry(h, idx + 1) ] for idx, h in enumerate(file.history())]
        ],
    ],
    override ( 'menu' ) [
        a (href=url(file_path)) [ 'Back' ],
    ]
]
