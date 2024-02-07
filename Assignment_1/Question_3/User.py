import threading
import pika, sys, json, os
from dotenv import load_dotenv

class User:
    def __init__(self, username):
        self.username = username

        # Set up queues and exchanges
        credentials = pika.PlainCredentials(os.getenv('PIKA_USERNAME'), os.getenv('PIKA_PASSWORD'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('EXTERNAL_IP'), credentials=credentials))
        self.channel = self.connection.channel()   

        # Creating a notif queue
        self.notification_queue = self.channel.queue_declare(queue=username, durable=True).method.queue

        # Declaring the exchanges
        # TODO: Check if this can be removed
        # self.channel.exchange_declare(exchange='youtube_exchange', exchange_type='direct', auto_delete=True)

        self.channel.queue_bind(exchange='notifications_exchange', queue=self.notification_queue, routing_key=f"notification.{username}")

    
    def updateSubscription(self, action, youtuber):
        # Sends the subscription/unsubscription request to the YouTubeServer with the following parameters in the body:                            
        message = json.dumps({
            'user': self.username,
            'youtuber': youtuber,
            'subscribe': True if action == 's' else False
        })

        # Sends the msg to the user_request queue through the exchange
        self.channel.basic_publish(exchange='youtube_exchange', routing_key='user_request', body=message)
        print("SUCCESS: Subscription updated")  

    def send_login_notification(self):
        # Sends the login notif to the user_request queue through the exchange        
        message = json.dumps({'user': self.username})
        self.channel.basic_publish(exchange='youtube_exchange', routing_key='user_request', body=message)
        print(f"SUCCESS: {self.username} logged in")

    def recieveNotification(self):
        # Receives any notifications already in the queue for the users subscriptions and starts receiving real-time notifications for videos uploaded while the user is logged in.        
        def callback(ch, method, properties, body):
            notification = json.loads(body)
            print(f"New Notification: {notification['youtuber']} uploaded {notification['video']}")

        print(f"Listening for notifications for {self.username}. To exit press CTRL+C")
        
        # Consumes the notif queue made for this user
        self.channel.basic_consume(queue=self.notification_queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()

if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python User.py [username] [s/u (optional)] [YoutuberName (optional)]")
    else:
        username = sys.argv[1]
        user = User(username)        
        user.send_login_notification()

        if len(sys.argv) > 3:            
            action = sys.argv[2].lower()  
            if action not in ['s', 'u']:
                print("Action should either be 's' or 'u'")
                exit(0)
            youtuber = sys.argv[3]
            user.updateSubscription(action, youtuber)
        try:
            user.recieveNotification()
        except KeyboardInterrupt:
            user.close_connection()

#TODO: Validate name of youtuber before subbing or unsubbing
    