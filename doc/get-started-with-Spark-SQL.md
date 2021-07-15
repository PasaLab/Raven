# Get Started with Spark-SQL
## Installation
Amazon AWS clusters have already installed Spark-SQL as part of `Spark` application. To install Spark-SQL in your cluster, you only need to make sure you have installed `Spark` application, see [applications to install](./how-to-configure-instances-of-a-cluster.md).

## Cluster Environment
To build up the cluster environment, you need prepare for necessary packages for benchmark execution. On the master node, run the following commands:
```shell
cd ~
sudo yum -y install git cyrus-sasl-devel.x86_64
sudo python3 -m pip install boto3 sasl thrift thrift-sasl pyhive pyspark
sudo python3 -m pip install --upgrade pyyaml
sudo chmod -R 777 /tmp
```

After that, clone our benchmark to the instance:
```shell
git clone https://github.com/PasaLab/OLAPBenchmark
```
To clone the benchmark, we need your GitHub account and password here.

## Configuration
The configuration file is in `./config/engines/spark-sql.yaml`. Users can edit the name of the session, and put system-level configurations here. To integrate SparkSQL with Hive well on cloud, the following settings are necessary:
```yaml
  hive.metastore.uris: thrift://ip-a-b-c-d.YOURREGION.compute.internal:9083
  spark.sql.warehouse.dir: hdfs://ip-a-b-c-d.YOURREGION.compute.internal:8020/user/hive/warehouse
```
Here, you need the internal DNS address of the master node, which can be found in `./cloud/instances`.