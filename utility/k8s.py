# -*- coding=utf-8 -*-
# Copyright 2018 Alex Ma

"""
:author Alex Ma (machao@qutoutiao.net)
:date 2018/10/15 

"""
import os
import threading
from utility.log import log
from kubernetes import client
from kubernetes.stream import stream

# from kubernetes.client import *
# from kubernetes.client.rest import ApiException


class KubernetesAPI(object):

    def __init__(self, api_host, ssl_ca_cert, key_file, cert_file):
        kub_conf = client.Configuration()
        kub_conf.host = api_host
        kub_conf.ssl_ca_cert = ssl_ca_cert
        kub_conf.cert_file = cert_file
        kub_conf.key_file = key_file

        self.api_client = client.ApiClient(configuration=kub_conf)
        self.client_core_v1 = client.CoreV1Api(api_client=self.api_client)
        self.client_apps_v1 = client.AppsV1Api(api_client=self.api_client)
        self.client_extensions_v1 = client.ExtensionsV1beta1Api(
            api_client=self.api_client)

        self.api_dict = {}

    def __getattr__(self, item):
        if item in self.api_dict:
            return self.api_dict[item]
        if hasattr(client, item) and callable(getattr(client, item)):
            self.api_dict[item] = getattr(client, item)(
                api_client=self.api_client)
            return self.api_dict[item]


class K8SClient(KubernetesAPI):

    def __init__(self, api_host, ssl_ca_cert, key_file, cert_file):
        super(K8SClient, self).__init__(
            api_host, ssl_ca_cert, key_file, cert_file)

    @staticmethod
    def gen_ca():
        ssl_ca_cert = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '_credentials/dev/kubernetes_dev_ca_cert')
        key_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '_credentials/dev/kubernetes_dev_key')
        cert_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '_credentials/dev/kubernetes_dev_cert')

        return ssl_ca_cert, key_file, cert_file

    def terminal_start(self, namespace, pod_name, container):
        command = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']

        # namespace = 'qtt-ops-qa'
        # pod_name = 'stack-webapp-50-d95c996d7-bq9jl'
        # container = 'stack-webapp-50'

        container_stream = stream(
            self.client_core_v1.connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=namespace,
            container=container,
            command=command,
            stderr=True, stdin=True,
            stdout=True, tty=True,
            _preload_content=False
        )

        return container_stream


class K8SStreamThread(threading.Thread):

    def __init__(self, ws, container_stream):
        super(K8SStreamThread, self).__init__()
        self.ws = ws
        self.stream = container_stream

    def run(self):
        while not self.ws.closed:

            if not self.stream.is_open():
                log.info('container stream closed')
                self.ws.close()

            try:
                if self.stream.peek_stdout():
                    stdout = self.stream.read_stdout()
                    self.ws.send(stdout)

                if self.stream.peek_stderr():
                    stderr = self.stream.read_stderr()
                    self.ws.send(stderr)
            except Exception as err:
                log.error('container stream err: {}'.format(err))
                self.ws.close()
                break
