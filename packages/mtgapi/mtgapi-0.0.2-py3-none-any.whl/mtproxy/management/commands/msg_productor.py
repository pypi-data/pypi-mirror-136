from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll
import pika
import time
import random
class Command(BaseCommand):
    help = '消息生产者'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        print("消息生产者")
        while True:
            self.product_msg()
            time.sleep(3)

    def product_msg(self):
        num = random.randint(0,99999999)
        msg={"num": num}

        credentials = pika.PlainCredentials(username="admin", password="feihuo321")
        # connection = pika.BlockingConnection()
        connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='127.0.0.1', port=5672, virtual_host='/', credentials=credentials))
        
        channel = connection.channel()
        msg:str = "Test message "+ str(num)
        print(f"产生消息 {msg}" )
        channel.basic_publish(exchange='test', routing_key='test',
                            body=msg)
        connection.close()