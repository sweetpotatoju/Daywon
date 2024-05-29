import ftplib
import os
from contextlib import contextmanager
import setting


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
            print(f"Trying to change directory to {remote_directory}")
            ftp.cwd(remote_directory)
            print(f"Changed directory to {remote_directory}")

            # 디렉토리 목록 확인
            print("Directory listing:")
            ftp.retrlines('LIST')

            # 파일 업로드
            with open(local_file_path, 'rb') as file:
                print(f"Trying to upload file: {local_file_path}")
                ftp.storbinary(f'STOR {os.path.basename(local_file_path)}', file)
                print(f"Uploaded {local_file_path} to FTP server.")
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")
