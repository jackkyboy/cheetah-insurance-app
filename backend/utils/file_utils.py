def allowed_file(filename, allowed_extensions):
    """
    ตรวจสอบนามสกุลไฟล์
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
