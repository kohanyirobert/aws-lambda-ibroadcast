import os
import boto3
from urllib.parse import unquote_plus
from subprocess import call
from pathlib import Path


def get_bucket_and_key(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    print('bucket', bucket)
    print('key', key)
    return (bucket, key)


def download_from_s3(bucket, key, audiopath):
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucket, key, str(audiopath))


def upload_to_ibroadcast(username, password, work_dir):
    read, write = os.pipe()
    os.write(write, b'U')
    os.close(write)

    call([
        'java',
        '-jar',
        str(Path(os.getcwd()) / 'ibroadcast-uploader.jar'),
        username,
        password,
    ], cwd=str(work_dir), stdin=read)


def handler(event, context):
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    work_dir = Path(os.environ['WORK_DIR'])
    bucket, key = get_bucket_and_key(event)

    audiopath = work_dir / key

    download_from_s3(bucket, key, audiopath)
    upload_to_ibroadcast(username, password, work_dir)

    return None
