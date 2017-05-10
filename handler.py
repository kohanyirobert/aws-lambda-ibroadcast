import os
import boto3
from urllib.parse import unquote_plus
from subprocess import call
from pathlib import Path
from tempfile import mkdtemp


def get_bucket_and_key(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    print('bucket', bucket)
    print('key', key)
    return (bucket, key)


def get_audiopath(work_dir, key):
    return Path(mkdtemp(dir=str(work_dir))) / key


def download_from_s3(s3, bucket, key, audiopath):
    s3.meta.client.download_file(bucket, key, str(audiopath))


def delete_from_s3(s3, bucket, key):
    s3.Object(bucket, key).delete()


def upload_to_ibroadcast(username, password, audiopath):
    read, write = os.pipe()
    os.write(write, b'U')
    os.close(write)

    call([
        'java',
        '-jar',
        str(Path(os.getcwd()) / 'ibroadcast-uploader.jar'),
        username,
        password,
    ], cwd=audiopath.parent, stdin=read)


def handler(event, context):
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    work_dir = Path(os.environ['WORK_DIR'])

    bucket, key = get_bucket_and_key(event)
    audiopath = get_audiopath(work_dir, key)

    s3 = boto3.resource('s3')
    download_from_s3(s3, bucket, key, audiopath)
    upload_to_ibroadcast(username, password, audiopath)
    delete_from_s3(s3, bucket, key)

    return None
