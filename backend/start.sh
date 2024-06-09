#!/bin/bash
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/
echo "TESSDATA_PREFIX is set to $TESSDATA_PREFIX"
uvicorn main:app --reload
