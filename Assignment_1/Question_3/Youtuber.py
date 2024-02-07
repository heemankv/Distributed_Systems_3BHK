import pika, sys, json, os
from dotenv import load_dotenv

class Youtuber:
    def __init__(self, name):        
        self.name = name     
        
        # Set up queues and exchanges
        credentials = pika.PlainCredentials(os.getenv('PIKA_USERNAME'), os.getenv('PIKA_PASSWORD'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('EXTERNAL_IP'), credentials=credentials))
        self.channel = self.connection.channel()   

        # Declaring the exchange
        # TODO: Check if this can be removed
        # self.channel.exchange_declare(exchange='youtube_exchange', exchange_type='direct', auto_delete=True)

    def publishVideo(self, videoName):
        # Sends the video to the youtubeServer
        # The YouTube server adds a new YouTuber if the name appears for the first time else; it adds the video to the existing YouTuber.
        message = json.dumps({'youtuber': self.name, 'video': video_name})

        # Publishes the video to the youtuber_upload queue through the exchange
        self.channel.basic_publish(exchange='youtube_exchange', routing_key='youtuber_upload', body=message)

        print(f"SUCCESS: {videoName} by {self.name} recieved by Youtube Server")
    
    def close_connection(self):
        self.connection.close()
    
if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) < 3:
        print("Usage: python Youtuber.py [YoutuberName] [VideoName]")
    else:
        youtuber_name = sys.argv[1]
        video_name = " ".join(sys.argv[2:])
        youtuber = Youtuber(youtuber_name)
        youtuber.publishVideo(video_name)
        
        youtuber.close_connection()