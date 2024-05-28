from ftplib import FTP


def connect_to_ftp(server: str, username: str, password: str) -> FTP:
    ftp = FTP(server)
    ftp.login(user=username, passwd=password)
    return ftp


def upload_file_to_ftp(ftp: FTP, file_path: str, remote_path: str):
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_path}', file)


def download_file_from_ftp(ftp: FTP, remote_path: str, local_path: str):
    with open(local_path, 'wb') as file:
        ftp.retrbinary(f'RETR {remote_path}', file.write)


def list_files_on_ftp(ftp: FTP, directory: str):
    files = []
    ftp.retrlines(f'LIST {directory}', files.append)
    return files


def disconnect_from_ftp(ftp: FTP):
    ftp.quit()
