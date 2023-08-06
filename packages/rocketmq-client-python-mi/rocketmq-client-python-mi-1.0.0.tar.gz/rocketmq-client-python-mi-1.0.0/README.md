# rocketmq-client-python

[![License](https://img.shields.io/badge/license-Apache%202-4EB1BA.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![Build Status](https://travis-ci.org/apache/rocketmq-client-python.svg?branch=master)](https://travis-ci.org/apache/rocketmq-client-python)
[![codecov](https://codecov.io/gh/apache/rocketmq-client-python/branch/ctypes/graph/badge.svg)](https://codecov.io/gh/apache/rocketmq-client-python/branch/ctypes)
[![PyPI](https://img.shields.io/pypi/v/rocketmq-client-python.svg)](https://pypi.org/project/rocketmq-client-python)
[![GitHub release](https://img.shields.io/badge/release-download-default.svg)](https://github.com/apache/rocketmq-client-python/releases)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/apache/rocketmq-client-python.svg)](http://isitmaintained.com/project/apache/rocketmq-client-python "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/apache/rocketmq-client-python.svg)](http://isitmaintained.com/project/apache/rocketmq-client-python "Percentage of issues still open")
![Twitter Follow](https://img.shields.io/twitter/follow/ApacheRocketMQ?style=social)

RocketMQ Python client, based on [rocketmq-client-cpp](https://github.com/apache/rocketmq-client-cpp), supports Linux and macOS
## Prerequisites

### Install `librocketmq`
rocketmq-client-python is a lightweight wrapper around [rocketmq-client-cpp](https://github.com/apache/rocketmq-client-cpp), so you need install 
`librocketmq` first.

#### Download by binary release.

- debian
    ```bash
        wget https://git.n.xiaomi.com/streaming/rocketmq-client-cpp/uploads/45ffa8c069174d3936e89258ce874140/rocketmq-client-cpp-2.2.0.amd64.deb
        sudo dpkg -i rocketmq-client-cpp-2.2.0.amd64.deb
    ```

## Installation

```bash
pip install rocketmq-client-python-mi
```

## Usage

### Producer

```python
from rocketmq.client import Producer, Message

producer = Producer('PID-XXX')
producer.set_name_server_address('127.0.0.1:9876')
producer.start()

msg = Message('YOUR-TOPIC')
msg.set_keys('XXX')
msg.set_tags('XXX')
msg.set_body('XXXX')
ret = producer.send_sync(msg)
print(ret.status, ret.msg_id, ret.offset)
producer.shutdown()
```

### PushConsumer

```python
import time

from rocketmq.client import PushConsumer, ConsumeStatus


def callback(msg):
    print(msg.id, msg.body)
    return ConsumeStatus.CONSUME_SUCCESS


consumer = PushConsumer('CID_XXX')
consumer.set_name_server_address('127.0.0.1:9876')
consumer.subscribe('YOUR-TOPIC', callback)
consumer.start()

while True:
    time.sleep(3600)

consumer.shutdown()

```

## License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html) Copyright (C) Apache Software Foundation
