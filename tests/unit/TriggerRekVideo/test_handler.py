import pytest
import json
import os
import boto3

from unittest.mock import patch
from unittest.mock import MagicMock,Mock
from TriggerRekVideo import handler
from boto3.session import Session

class TestHandler:

    def setup(self):
        self.analyses = [
            'start_celebrity_recognition',
            'start_label_detection',
            'start_content_moderation'
        ]
        self.rekClient = Mock(spec=self.analyses)
        self.rekClient.start_celebrity_recognition = MagicMock(return_value={'JobId': 1})
        self.rekClient.start_label_detection = MagicMock(return_value={'JobId': 2})
        self.rekClient.start_content_moderation = MagicMock(return_value={'JobId': 3})

        with open(os.path.join(os.getcwd(), 'tests', 'unit', 'TriggerRekVideo', 'event.json')) as f:
            self.event = json.loads(f.read())

        self.RoleArn = 'arn:Role:Mock'
        self.TopicArn = 'arn:Topic:Mock'
        self.notification = {
            'SNSTopicArn': self.TopicArn,
            'RoleArn': self.RoleArn
        }
        os.environ['REK_EXEC_ROLE_ARN'] = self.RoleArn
        os.environ['SNS_TOPIC_ARN'] = self.TopicArn

    def test_get_video(self):
        video = handler.get_video(self.event)
        assert(video['S3Object']['Bucket'] == 'videoanalysis-127436723527')
        assert(video['S3Object']['Name'] == 'week4_1.mp4')

    def test_lambda_function(self):
        with patch.object(Session, 'client', return_value=self.rekClient) as mock_method:
            response = handler.lambda_handler(self.event, '')
            assert(response['celebrity_recognition_job_id'] is not None)
            assert(response['celebrity_recognition_job_id'] == 1)
            assert(response['label_detection_job_id'] is not None)
            assert(response['label_detection_job_id'] == 2)
            assert(response['content_moderation_job_id'] is not None)
            assert(response['content_moderation_job_id'] == 3)
            mock_method.assert_called_once_with(service_name='rekognition')
            video = handler.get_video(self.event)
            self.rekClient.start_celebrity_recognition.assert_called_once_with(
                Video=video,
                NotificationChannel = self.notification
            )
            self.rekClient.start_label_detection.assert_called_once_with(
                Video=video,
                NotificationChannel=self.notification)
            self.rekClient.start_content_moderation.assert_called_once_with(
                Video=video,
                NotificationChannel=self.notification)