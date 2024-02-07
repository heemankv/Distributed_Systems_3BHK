import pika, json

class YoutubeServer:
    def __init__(self):
        # Set up queues and exchanges
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        # Declaring a direct exchange for requests
        self.channel.exchange_declare(exchange='youtube_exchange', exchange_type='direct', auto_delete=True)

        # Declaring a topic exchange for notifications
        self.channel.exchange_declare(exchange='notifications_exchange', exchange_type='topic')

        # Making the 2 queues
        self.channel.queue_declare(queue='user_requests', exclusive=True)
        self.channel.queue_declare(queue='youtuber_uploads', exclusive=True)

        # Binding the queues to the exchange through a direct exchange
        self.channel.queue_bind(exchange='youtube_exchange', queue='user_requests', routing_key='user_request')
        self.channel.queue_bind(exchange='youtube_exchange', queue='youtuber_uploads', routing_key='youtuber_upload')

        self.users = {}   # users = {'user1': {subscriptions: []}}
        self.videos = {}  # videos = {'ytbr1': [], 'ytbr2': []}      

    def start_consuming(self):
        # Defining the callback function to read the routing key and the send the request to the appropriate function
        def callback(ch, method, properties, body):            
            if method.routing_key == 'user_request':
                self.consume_user_requests(body)
            elif method.routing_key == 'youtuber_upload':
                self.consume_youtuber_requests(body)

        # Consume both queues 
        self.channel.basic_consume(queue='user_requests', on_message_callback=callback, auto_ack=True)     
        self.channel.basic_consume(queue='youtuber_uploads', on_message_callback=callback, auto_ack=True)

        print('Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()        
    
    def consume_user_requests(self, body):
        # Reads the request. Adds new user if does not exist. Changes subscription status if reqd else just logs in
        request = json.loads(body)
        username = request['user']

        if username not in self.users:
            self.users[username] = {'subscriptions': []}

        if 'subscribe' in request:
            # TODO: No need to send the username as it is already inside request
            self.handle_subscription(username, request)      
        else:
            print(f"{username} logged in")    
        print(self.users)     

    def handle_subscription(self, username, request):
        # Reads the youtubers name. Creates new user if reqd. 
        # If the request is to subscribe then add the youtuber to the subscriptions of the user
        # Else unsubscribe the youtuber from the user list of subscription
        youtuber = request['youtuber']
        
        # TODO: Redundant if case
        if username not in self.users:
            self.users[username] = {'subscriptions': []}
        
        if request['subscribe']:
            if youtuber not in self.videos:
                print("Youtuber does not exist!!")
            elif youtuber not in self.users[username]['subscriptions']:
                self.users[username]['subscriptions'].append(youtuber)
                print(f"{username} subscribed to {youtuber}")
            else:
                print(f"{username} ALREADY subscribed to {youtuber}")                        
                
        elif not request['subscribe'] and youtuber in self.users[username]['subscriptions']:
            self.users[username]['subscriptions'].remove(youtuber)
            print(f"{username} unsubscribed from {youtuber}")

    def consume_youtuber_requests(self, body):
        # Consumes video upload requests of youtubers. Adds ytbr if not exist else adds videos. Also sends notification to all subbed users        
        data = json.loads(body)
        youtuber, video = data['youtuber'], data['video']
        if youtuber not in self.videos:
            self.videos[youtuber] = []
        self.videos[youtuber].append(video)
        print(f"{youtuber} uploaded {video}")        

        print(self.videos)     
        self.notify_users(youtuber, video)
                
    def notify_users(self, youtuber, video):
        # Notify all users subscribed to this youtuber about the new video. It keeps the message in the queues of each user        
        for user, data in self.users.items():
            if youtuber in data['subscriptions']:
                message = json.dumps({'youtuber': youtuber, 'video': video})
                routing_key = f"notification.{user}"
                self.channel.basic_publish(exchange='notifications_exchange', routing_key=routing_key, body=message)
                print(f"Queued notification for {user}: {youtuber} uploaded {video}")


if __name__ == '__main__':
    server = YoutubeServer()
    try:
        server.start_consuming()
    except KeyboardInterrupt:
        print()
        print("Ending...")
