import os


class DockerRunOptions(object):
    def __init__(self):
        self.options = set()

    def with_gpu(self) -> 'DockerRunOptions':
        self.options.add('--gpus all')
        return self

    def with_privileged(self) -> 'DockerRunOptions':
        self.options.add('--privileged')
        return self

    def with_add_devices(self) -> 'DockerRunOptions':
        self.options.add('-v /dev:/dev')
        self.with_privileged()
        return self

    def with_display(self) -> 'DockerRunOptions':
        display = os.environ.get('DISPLAY')
        self.options.add(f'-e DISPLAY={display}')
        self.options.add('-e QT_X11_NO_MITSHM=1')
        self.options.add('-v /tmp/.X11-unix:/tmp/.X11-unix:ro')
        return self

    def with_shared_memory(self) -> 'DockerRunOptions':
        self.options.add(f'--ipc=host')
        self.options.add('--ulimit memlock=-1')
        self.options.add('--ulimit stack=67108864')
        self.with_add_devices()
        return self

    def build(self):
        return ' '.join(self.options)

