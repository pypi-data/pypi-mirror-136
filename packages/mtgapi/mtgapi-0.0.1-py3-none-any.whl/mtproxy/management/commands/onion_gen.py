from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll
import os
from stem.control import Controller
class Command(BaseCommand):
    help = '生成新的onion域名'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):

        print("备注：须先启动tor")
        with Controller.from_port() as controller:
            controller.authenticate()
            service = controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
            print("Started a new hidden service with the address of %s.onion" % service.service_id)            
            
            print("生成私钥字符：")
            print('%s:%s' % (service.private_key_type, service.private_key))
            # key_file.write('%s:%s' % (service.private_key_type, service.private_key))

        ## 下面为其他范例代码
        # 私钥路径，如果存在则自动使用
        # key_path = os.path.expanduser('~/my_service_key')
        # with Controller.from_port() as controller:
        #     controller.authenticate()
        #     if not os.path.exists(key_path):
        #         service = controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
        #         print("Started a new hidden service with the address of %s.onion" % service.service_id)

        #         with open(key_path, 'w') as key_file:
        #             key_file.write('%s:%s' % (service.private_key_type, service.private_key))
        #     else:
        #         with open(key_path) as key_file:
        #             key_type, key_content = key_file.read().split(':', 1)

        #         service = controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
        #         print("Resumed %s.onion" % service.service_id)

        #     #   raw_input('press any key to shut the service down...')
        #     controller.remove_ephemeral_hidden_service(service.service_id)