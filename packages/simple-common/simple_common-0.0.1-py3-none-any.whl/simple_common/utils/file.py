import os


def save_file(file_path, content):
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(file_path, 'w') as file:
        file.write(content)
