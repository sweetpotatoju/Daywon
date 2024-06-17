import ftplib
import os
from contextlib import asynccontextmanager
import asyncio
import aioftp
from fastapi import HTTPException, FastAPI

from app.core.FTP_SERVER import setting

app = FastAPI()


async def connect_to_ftp(server, port, username, password):
    loop = asyncio.get_event_loop()
    ftp = ftplib.FTP()
    await loop.run_in_executor(None, ftp.connect, server, port)
    await loop.run_in_executor(None, ftp.login, username, password)
    return ftp


async def disconnect_from_ftp(ftp):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, ftp.quit)


@asynccontextmanager
async def get_ftp_connection():
    ftp = await connect_to_ftp(setting.FTP_SERVER, setting.FTP_PORT, setting.FTP_USERNAME, setting.FTP_PASSWORD)
    try:
        yield ftp
    finally:
        await disconnect_from_ftp(ftp)


async def list_files():
    try:
        async with get_ftp_connection() as ftp:
            loop = asyncio.get_event_loop()
            files = await loop.run_in_executor(None, ftp.nlst)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def upload_file_to_ftp(local_file_path, remote_directory):
    try:
        async with get_ftp_connection() as ftp:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, ftp.cwd, remote_directory)
            await loop.run_in_executor(None, ftp.retrlines, 'LIST')
            with open(local_file_path, 'rb') as file:
                await loop.run_in_executor(None, ftp.storbinary, f'STOR {os.path.basename(local_file_path)}', file)
        os.remove(local_file_path)
        print(f"File {local_file_path} uploaded and removed locally.")
    except PermissionError as e:
        print(f"PermissionError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def video_from_ftp(filename):
    async with aioftp.Client.context(host=setting.FTP_SERVER, port=setting.FTP_PORT, user=setting.FTP_USERNAME,
                                     password=setting.FTP_PASSWORD) as client:
        async with client.download_stream(filename) as stream:
            while True:
                block = await stream.read(1024)  # Read in chunks of 1024 bytes
                if not block:
                    break
                yield block


async def read_file_from_ftp(remote_directory):
    try:
        async with get_ftp_connection() as ftp:
            file_contents = []
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, ftp.retrlines, f'RETR {remote_directory}', file_contents.append)
            return '\n'.join(file_contents)
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")


async def read_binary_file_from_ftp(remote_file_path):
    try:
        async with get_ftp_connection() as ftp:
            file_contents = bytearray()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, ftp.retrbinary, f'RETR {remote_file_path}', file_contents.extend)
            return bytes(file_contents)
    except ftplib.error_perm as e:
        print(f"Permission error: {e}")
    except ftplib.error_temp as e:
        print(f"Temporary error: {e}")
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")
        return None


async def download_file_from_ftp(remote_file_path, local_file_path):
    try:
        async with get_ftp_connection() as ftp:
            loop = asyncio.get_event_loop()
            with open(local_file_path, 'wb') as local_file:
                await loop.run_in_executor(None, ftp.retrbinary, f'RETR {remote_file_path}', local_file.write)
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
