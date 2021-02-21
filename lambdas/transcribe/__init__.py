import json
import boto3
import os
import uuid
import time

INPUT_BUCKET = os.environ["INPUT_BUCKET"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]
VALID_EXTENSIONS = ["mp4", "mp3", "wav", "flac"]
transcribe = boto3.client("transcribe")

def handle(event, context):
    key = event["Records"][0]["s3"]["object"]["key"]
    extension = key.split(".")[1]
    job_uri = f"https://{INPUT_BUCKET}.s3.amazonaws.com/{key}"
    job_name = str(uuid.uuid4())

    if extension not in VALID_EXTENSIONS:
        raise

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={ "MediaFileUri": job_uri },
        MediaFormat=extension,
        LanguageCode="en-US",
        OutputBucketName=OUTPUT_BUCKET)

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in ["COMPLETED", "FAILED"]:
            break
        time.sleep(2)
    
    return json.dumps(status)
