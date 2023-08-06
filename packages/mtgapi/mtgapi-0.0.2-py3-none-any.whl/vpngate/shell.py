

##
## 运行系统命令
##
import subprocess, shlex
import logging

logger = logging.getLogger(__name__)
def run(cmd):    
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=False)
    p.wait()
    #只当作文本处理，二进制不管了。
    outputtext = p.stdout.read().decode()
    # if p.returncode != 0:
    #     raise Exception("执行命令失败,返回值:{},命令:{}".format(p.returncode,cmd))
    # else:
    logger.debug("执行系统命令：{}\n返回值：{},输出：{}".format(cmd,p.returncode,outputtext))
    return outputtext