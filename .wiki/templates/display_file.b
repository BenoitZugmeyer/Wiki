div (class_='content') [
    h1 (class_='title') [ xml(file_title) if file_title else file_name ],
    test(file_subtitle) and h2 (class_='subtitle') [ xml(file_subtitle) ],
    div (class_='body') [
        xml(file_content) if file_exists else 'File does not exists',
    ],
]
