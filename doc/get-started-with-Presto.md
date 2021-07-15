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
git clone https://github.com/PasaLab/OLAPBenchmark
```
To clone the benchmark, we need your GitHub account and password here.

## Configuration
For the Presto engine, the following configurations are correct:
```yaml
  host: ip-a-b-c-d.ap-southeast-1.compute.internal
  port: 8889
```
Here, you need the internal DNS address of the master node, which can be found in `./cloud/instances`.