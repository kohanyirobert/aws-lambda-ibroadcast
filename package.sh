#! /bin/sh
rm -vf package-*.zip
zip -r package-$(basename $(pwd))-$(cat VERSION).zip VERSION ibroadcast-uploader.jar handler.py
