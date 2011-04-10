macro('entry', lambda h, idx:
    [
        format_date(h.mtime), ', ', format_size(h.size), ' ',
        a ( href=url(file_path, ['history', ('see', idx)])) ['see']
            if see != idx else 'seeing', ' ',
        [
            input ( type='radio', name='new', value=str(idx), checked='checked' if not new else None),
            ' (current version)',
        ] if not idx else [
            input ( type='radio', name='old', value=str(idx), checked='checked' if old == idx else None),
            test(idx != len(history)) and input ( type='radio', name='new', value=str(idx),
                checked='checked' if new == idx else None),
        ],
    ]
),
inherits ( 'global' ) [
    override ('title') [ 'History of ', file_name ],
    override ( 'content' ) [
        h1 [ 'History of "', file_name, '"' ],
        test ('history_file' in globals()) and div (id='preview') [
            h2 [ file_name, ' at ', format_date(history_file.mtime) ],
            include ('display_file'),
        ],
        test ('diff_content' in globals()) and pre (id='diff') [diff_content],
        form (method='post', action=url(file_path, ['history'])) [
            ul [
                li [ entry(file, 0) ],
                [li [ entry(h, idx + 1) ] for idx, h in enumerate(history)]
            ],
            input (type='submit', value='Show differences'),
        ],
    ],
    override ( 'menu' ) [
        a (href=url(file_path)) [ 'Back' ],
    ]
]
