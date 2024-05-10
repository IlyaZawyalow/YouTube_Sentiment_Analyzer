from googleapiclient.discovery import build
import time
import re
from typing import Dict, Any, Union
from loguru import logger
import pika

KEY = 'AIzaSyDAUsif0K6XxybhWdmQ3XgNGzonyJB-63w'

class Worker:

    def __init__(self, developerKey: str):
        self.developerKey = developerKey
        self.service = build('youtube', 'v3', developerKey=self.developerKey)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=pika.PlainCredentials('rmuser', 'rmpassword')))
        self.channel = self.connection.channel()

    def create_queue(self, video_id: str) -> None:
        self.channel.queue_declare(queue=video_id)
        
    def publish_to_queue(self, video_id: str, comment_text: str):
        self.channel.basic_publish(exchange='',
                                   routing_key=video_id,
                                   body=comment_text)
        logger.info(f'Добавил comment_text в очередь {comment_text}')
        
    def api_response(self, video_id: str, PageToken: str=None) -> Dict[str, Any]:
        resource_data = self.service.commentThreads().list(videoId=video_id, part='id, snippet, replies',
                                                           maxResults=100, pageToken=PageToken).execute()
        return resource_data

    def add_data_in_queue(self, data, video_id: str):
        for i in data['items']:
            comment_text = i['snippet']['topLevelComment']['snippet']['textOriginal']
            self.publish_to_queue(video_id, comment_text)
            if 'replies' in i:
                for j in i['replies']['comments']:
                    subcomment_text = j['snippet']['textOriginal']
                    self.publish_to_queue(video_id, subcomment_text)

    def run(self, video_id: str):
        try:
            self.create_queue(video_id)
            r = self.api_response(video_id)
            self.add_data_in_queue(r, video_id)
            time.sleep(1)
            while 'nextPageToken' in r:
                r = self.api_response(video_id, r['nextPageToken'])
                self.add_data_in_queue(r, video_id)
        except Exception as e:
            logger.error(f'Ошибка при выполнении работы Worker: {e}')
        finally:
            self.connection.close()

if __name__ == '__main__':
    video_link = 'https://www.youtube.com/watch?v=jA9CpUSaSN4'
    w = Worker(KEY)
    w.run(video_id='jA9CpUSaSN4')
