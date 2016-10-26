def devbutton(version):
    if version == 'develop':
        button = [
            [
                KeyboardButton(text='Develop version.')
            ]
        ]
    else:
        button = []
    return button
