def devbutton(version):
    if version == 'develop':
        button = [
            [
                KeyboardButton(text='Develop')
            ]
        ]
    else:
        button = []
    return button
