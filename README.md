# K8S web terminal 
A light K8S web terminal demo.

The demo refer to personal blog https://blog.csdn.net/duxiangwushirenfei/article/details/83341574.

Please visit link given to get detail.

# Optimize

1, CPU Occupation

Refer to issue: https://github.com/wushirenfei/k8s-web-terminal/issues/1, 
it'll consistently occupy server cup resource, when read data from container by using `while True`.

This will be resolve by use IO multiplexing just as epoll or select.

You can get container connection socket object in Stream object by `stream.sock.sock`, for example use `select` implement async read listen.

```python

class NewK8sThread(threading.Thread):
    
    def __init__(self, ws, stream):
        super(NewK8sThread, self).__init__()
        self.ws = ws
        self.stream = stream
        self.selector = select.epoll()
    
    
    def read(self):
        self.selector.register(self.stream.sock.sock.fileno(), 
                               selectors.EVENT_READ, 
                               self.readable)
    
    def readable(self):
        self.selector.unregister(self.stream.sock.sock.fileno())
        data = self.stream.read_stdout()
        self.ws.send(data)
    
    def run(self):
        self.read()
    
``` 

Above `NewK8sThread` just a pseudocode demo cannot run immediately.

