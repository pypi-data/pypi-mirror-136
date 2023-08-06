from celery import Celery
import subprocess
app = Celery('tasks', broker='pyamqp://admin:feihuo321@localhost//', backend='redis://:feihuo321@localhost')

@app.task
def add(x, y):
    return x + y

@app.task
def process_out(bashScript:str, timeout:int):
    print(f"准备执行脚本 {bashScript}")
    return {"stdout":"__stdoud", "stderr":"__stderr","code":0}