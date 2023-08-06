from time import sleep
from django.core.management.base import BaseCommand, CommandError
import os
from stem.control import Controller
import stem
import stem.process
from stem.util import term
from mtproxy import models

SOCKS_PORT=9050
class Command(BaseCommand):
    help = '根据配置启动本站点的隐藏域名'
    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)
    def handle(self, *args, **options):
        # siteConfig = models.SiteConfig.objects.get(site_name="main")
        # print("从站点配置中获取onion私钥 {siteConfig.onion_key}")
        # with Controller.from_port() as controller:
        #     controller.authenticate()         
        #     key_type, key_content = siteConfig.onion_key.split(':', 1)
        #     service = controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
        #     print("Resumed %s.onion" % service.service_id)

        def print_bootstrap_lines(line):
            # if "Bootstrapped " in line:
            if line and len(line) > 0:
                print(term.format("Tor:", term.Attr.BOLD), end="")
                print(term.format(line, term.Color.BLUE))
                

        tor_process = stem.process.launch_tor_with_config(
            config = {
                'SocksPort': str(SOCKS_PORT),
                # 'ExitNodes': '{ru}',
                'VirtualAddrNetworkIPv4': "10.192.0.0/10",
                "AutomapHostsOnResolve": "1",
                "AvoidDiskWrites": "1",
                "SocksPort": f"0.0.0.0:{SOCKS_PORT}",
                "TransPort": "127.0.0.1:9040",
                "DNSPort": "127.0.0.1:5353",
                "CookieAuthentication":"1",
                "ControlPort": "0.0.0.0:9051",
                "HashedControlPassword": "16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF"
            },
            init_msg_handler = print_bootstrap_lines,
        )

        print(term.format("\nTor ready \n", term.Attr.BOLD))
        # print(term.format(query("https://www.atagar.com/echo.php"), term.Color.BLUE))


        with Controller.from_port() as controller:
            controller.authenticate()     
            site_configs = models.Onion.objects.filter(tag="default")
            for item in site_configs:
                print(f"处理：{item}")
                key_type, key_content = item.private_key.split(':', 1)
                # create_ephemeral_hidden_service({80: 80, 443: '173.194.33.133:443'})
                service = controller.create_ephemeral_hidden_service(
                    {item.service_port: f"{item.target_host}:{item.target_port}"}, 
                    key_type = key_type, 
                    key_content = key_content, 
                    await_publication = True)
                print(f"成功启动隐藏域名： http://{service.service_id}.onion:{item.service_port}")

                print("获取列表(以帮助排查问题)")
                items = controller.list_ephemeral_hidden_services()
                print(items)
            # 不知道为什么程序退出，域名就无效了。
            # 可能是因为with语句 让controller自动释放资源。
            while True:
                sleep(1000)

