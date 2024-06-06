import ftplib
import os
from contextlib import contextmanager
from app.core.FTP_SERVER import setting


def connect_to_ftp(server, port, username, password):
    ftp = ftplib.FTP()
    ftp.connect(server, port)
    ftp.login(user=username, passwd=password)
    return ftp


def disconnect_from_ftp(ftp):
    ftp.quit()


@contextmanager
def get_ftp_connection():
    ftp = connect_to_ftp(setting.FTP_SERVER, setting.FTP_PORT, setting.FTP_USERNAME, setting.FTP_PASSWORD)
    try:
        yield ftp
    finally:
        disconnect_from_ftp(ftp)


def upload_file_to_ftp(local_file_path, remote_directory):
    try:
        with get_ftp_connection() as ftp:
            ftp.cwd(remote_directory)
            ftp.retrlines('LIST')
            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(local_file_path)}', file)

        # 업로드가 성공하면 로컬 파일 삭제
        os.remove(local_file_path)
        print(f"File {local_file_path} uploaded and removed locally.")
    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def read_file_from_ftp(remote_directory):
    try:
        with get_ftp_connection() as ftp:
            # 임시로 파일 내용을 저장할 리스트
            file_contents = []
            ftp.retrlines(f'RETR {remote_directory}', file_contents.append)
            return '\n'.join(file_contents)
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")
