from io import StringIO

from fastapi import UploadFile


def decode_file(input_file: UploadFile):
    file_bytes = input_file.file.read()
    buffer = StringIO(file_bytes.decode('utf-8'))
    content = buffer.read()
    buffer.close()
    input_file.file.close()
    return content

