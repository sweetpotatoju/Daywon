import ftplib
import os
from contextlib import contextmanager
import aioftp
from fastapi import HTTPException, FastAPI
from fastapi.responses import StreamingResponse

from app.core.FTP_SERVER import setting

app = FastAPI()

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

def list_files():
    try:
        with get_ftp_connection() as ftp:
            files = ftp.nlst()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def upload_file_to_ftp(local_file_path, remote_directory):
    try:
        with get_ftp_connection() as ftp:
            ftp.cwd(remote_directory)
            ftp.retrlines('LIST')
            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(local_file_path)}', file)
        os.remove(local_file_path)
        print(f"File {local_file_path} uploaded and removed locally.")
    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def video_from_ftp(filename):
    async with aioftp.Client.context(host=setting.FTP_SERVER, port=setting.FTP_PORT, user=setting.FTP_USERNAME, password=setting.FTP_PASSWORD) as client:
        async with client.download_stream(filename) as stream:
            while True:
                block = await stream.read(1024)  # Read in chunks of 1024 bytes
                if not block:
                    break
                yield block

@app.get("/get_stream_video/{remote_file_path}")
async def get_stream_video(remote_file_path: str):
    video_stream = video_from_ftp(remote_file_path)
    return StreamingResponse(video_stream, media_type="video/mp4")

def read_file_from_ftp(remote_directory):
    try:
        with get_ftp_connection() as ftp:
            file_contents = []
            ftp.retrlines(f'RETR {remote_directory}', file_contents.append)
            return '\n'.join(file_contents)
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")

def read_binary_file_from_ftp(remote_file_path):
    try:
        with get_ftp_connection() as ftp:
            file_contents = bytearray()
            ftp.retrbinary(f'RETR {remote_file_path}', file_contents.extend)
            return bytes(file_contents)
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")
        return None

def download_file_from_ftp(remote_file_path, local_file_path):
    try:
        with get_ftp_connection() as ftp:
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary(f'RETR {remote_file_path}', local_file.write)
        print(f"File {remote_file_path} downloaded to {local_file_path}")
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
        raise HTTPException(status_code=403, detail=f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
        raise HTTPException(status_code=503, detail=f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")
        raise HTTPException(status_code=500, detail=f"FTP error: {e}")
