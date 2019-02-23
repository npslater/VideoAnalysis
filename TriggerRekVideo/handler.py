from boto3.session import Session
import os
import json

def get_video(event):
    body = json.loads(event['Records'][0]['body'])
    message = json.loads(body['Message'])
    video = {
        'S3Object': {
            'Bucket': message['Records'][0]['s3']['bucket']['name'],
            'Name': message['Records'][0]['s3']['object']['key']
        }
    }
    return video

#TODO: Add error handling
def lambda_handler(event, context):
    print('Event: {}'.format(json.dumps(event)))
    notification = {
        'SNSTopicArn': os.environ['SNS_TOPIC_ARN'],
        'RoleArn': os.environ['REK_EXEC_ROLE_ARN']
    }
    video = get_video(event)
    rek = Session().client(service_name='rekognition')
    celeb_rec_job_id = rek.start_celebrity_recognition(
        Video=video,
        NotificationChannel = notification)['JobId']
    label_job_id = rek.start_label_detection(
        Video=video,
        NotificationChannel = notification)['JobId']
    content_mod_job_id = rek.start_content_moderation(
        Video=video,
        NotificationChannel = notification)['JobId']
    return {
        'celebrity_recognition_job_id': celeb_rec_job_id,
        'label_detection_job_id': label_job_id,
        'content_moderation_job_id': content_mod_job_id
    }