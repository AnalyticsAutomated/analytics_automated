import imghdr


def gif(file_data):
    if 'gif' in imghdr.what(file_data):
        return True
    else:
        return False


def png(file_data):
    if 'png' in imghdr.what(file_data):
        return True
    else:
        return False


def jpg(file_data):
    if 'jpg' in imghdr.what(file_data):
        return True
    else:
        return False
