<h1 align = "center">Diss</h3>
<h3 align="center">DIstributed Submission System</h3>

<div align="center">


[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![made-with-kafka](https://img.shields.io/badge/Made%20with-Kafka-blue)](https://kafka.apache.org/)
<br>



</div>

------------------------------------------

> Leverages the distributed nature of Apache Kafka to allow users to submit their code to a master that distributes work to workers. It offloads the responsibility of fault tolerance, distribution and scalabililty to Kafka.

------------------------------------------

<br><br>

<div align="center">
    <h3>Configuring the master<h3>
</div>

#### <u>Starting zookeeper </u>

1. Install [zookeeper](https://zookeeper.apache.org/releases.html) and navigate to the directory

```
$ cd /home/aditya/Downloads/kafka/apache-zookeeper-3.6.0-bin
```

2. Add config file:

```
$ vim conf/zoo.cfg

tickTime=2000
dataDir=/var/lib/zookeeper
clientPort=2181

:wq
```

#### <u>Starting Kafka</u>

1. Install [Kafka](https://www.apache.org/dyn/closer.cgi?path=/kafka/2.5.0/kafka_2.12-2.5.0.tgz)

2. Start zookeeper

```
$ bin/zookeeper-server-start.sh config/zookeeper.properties
```

3. Start Kafka

```
$ bin/kafka-server-start.sh config/server.properties
```

