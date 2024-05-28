from app.core.FTP_SERVER.FTP_client import connect_to_ftp, upload_file_to_ftp, download_file_from_ftp, \
    list_files_on_ftp, disconnect_from_ftp
from app.core.FTP_SERVER.setting import FTP_SERVER, FTP_USERNAME, FTP_PASSWORD


def main():
    # FTP 서버에 연결
    ftp = connect_to_ftp(FTP_SERVER, FTP_USERNAME, FTP_PASSWORD)

    try:
        # 로컬 파일을 FTP 서버에 업로드
        local_file_path = 'path/to/local/file.txt'
        remote_file_path = 'remote/file.txt'
        upload_file_to_ftp(ftp, local_file_path, remote_file_path)

        # # FTP 서버에서 로컬로 파일 다운로드
        # download_local_path = 'path/to/download/file.txt'
        # download_file_from_ftp(ftp, remote_file_path, download_local_path)

        # FTP 서버의 파일 목록 조회
        files = list_files_on_ftp(ftp, 'video')
        print("Files on FTP server:")
        for file in files:
            print(file)
    finally:
        # FTP 서버 연결 종료
        disconnect_from_ftp(ftp)


if __name__ == "__main__":
    main()