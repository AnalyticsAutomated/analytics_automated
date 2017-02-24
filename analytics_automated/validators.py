import imghdr


def gif(file_data):
    if 'gif' in imghdr.what('', file_data):
        return True
    else:
        return False


def png(file_data):
    print(file_data)
    if 'png' in imghdr.what('', file_data):
        return True
    else:
        return False


def jpeg(file_data):
    if 'jpeg' in imghdr.what('', file_data):
        return True
    else:
        return False
