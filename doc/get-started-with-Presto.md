# Get Started with Presto
## Installation
Amazon AWS clusters have already installed Presto as an application. To install Presto in your cluster, you only need to make sure you have installed `Presto` application, see [applications to install](./how-to-configure-instances-of-a-cluster.md).

## Cluster Environment
To build up the cluster environment, you need prepare for necessary packages for benchmark execution. On the master node, run the following commands:
```shell
cd ~
sudo yum -y install git cyrus-sasl-devel.x86_64
sudo python3 -m pip install boto3 sasl thrift thrift-sasl pyhive presto-python-client
sudo python3 -m pip install --upgrade pyyaml
sudo chmod -R 777 /tmp
```

After that, clone our benchmark to the instance:
```shell
git clone https://github.com/PasaLab/Raven
```
To clone the benchmark, we need your GitHub account and password here.

## Configuration
The configuration file is in `./config/engines/presto.yaml`. Users can put system-level configurations here.
