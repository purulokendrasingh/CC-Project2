import os
import urllib.parse
import boto3
import face_recognition
import pandas as pd
from subprocess import check_call
import pickle

def create_path(path):
  if not os.path.exists(path):
    try:
      os.makedirs(path)
    except Exception as e:
      print(e)

# AWS Credentials (Should be removed and use IAM roles and environment variables instead)
AWS_ACCESS_KEY = "AKIAS7MBQITZFVSNQGG4"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
table_name = "Students"

# AWS Clients (configured with hardcoded credentials)
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)
dynamodb = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_REGION)

# Constants for bucket names
input_bucket = "inputbucket-cc2"
output_bucket = "outputbucket-cc2"
cur_path = os.getcwd()

print("Starting")

def open_encoding(filename):
    with open(filename, "rb") as file:
        data = pickle.load(file)
    return data


def video_from_s3(bucket, object_name):
    s3.download_file(bucket, object_name, f"/tmp/{object_name}")


def extract_frame_from_video(video_path, frame_path):
    # Using subprocess to call ffmpeg safely
    check_call(['ffmpeg', '-i', video_path, '-frames:v', '1', '-r', '1', frame_path])


def face_recognition_handler(event, context):
    print("In the face recognition")
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    inp_path = f"/tmp/{key}"
    out_path = f"/tmp/{key.split('.')[0]}.jpeg"

    try:
        video_from_s3(input_bucket, key)
        extract_frame_from_video(inp_path, out_path)
        print("done extracting the frame")
        unknown_image = face_recognition.load_image_file(out_path)
        print("done loading image file")
        unknown_encoding = face_recognition.face_encodings(unknown_image)
        print("done finding face encodings")

        if unknown_encoding:
            unknown_encoding = unknown_encoding[0]
            # create_path(os.path.join(cur_path, "encoding"))
            given_encodings = open_encoding(os.path.join(cur_path, "encoding"))
            results = face_recognition.compare_faces(given_encodings['encoding'], unknown_encoding)
            print("if unknown encodings")

            if True in results:
                print("got results")
                match_index = results.index(True)
                name = given_encodings['name'][match_index]
                name = str(name)
                print("querying the DDB table")
                output = table_query(name)
                print("done querying the table")
                output_list = [output['name']['S'], output['major']['S'], output['year']['S']]
                key = key.split(".")[0]

                pd.DataFrame(output_list).T.to_csv(f"/tmp/{key}.csv", index=False, header=False)
                s3.upload_file(f"/tmp/{key}.csv", output_bucket, f"{key}.csv")
                print("Done uploading to S3")
            else:
                name = "Unknown"
        else:
            name = "No faces found"

        return name

    except Exception as e:
        print(e)
        raise e
    finally:
        # Cleanup temporary files
        clean_up_files([inp_path, out_path, f"/tmp/{key}.csv"])


def clean_up_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)


def table_query(name):
    result = dynamodb.get_item(TableName=table_name, Key={'name': {'S': name}})
    return result['Item'] if 'Item' in result else None
