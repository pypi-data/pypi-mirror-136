import docker
import os
def getDockerClient():
    tls_config = docker.tls.TLSConfig(
        client_cert=(os.path.abspath('./.cert/cert.pem'), os.path.abspath('./.cert/key.pem')),
        # verify =False
    )
    client = docker.DockerClient(base_url='https://172.17.0.1:2376', tls=tls_config)
    return client




