# OLAP Benchmark
## Feature
// TODO

## Prerequisites
- Git 2.29.1 and above
- AWS Client 1.19.69 and above
- Python 3.6.8 and above with the following packages installed:
  - awscli 1.18.105 and above
  - boto3 1.17.69 and above
  - pyYAML 5.4.1 and above
  - PyHive 0.6.4 and above
  - matplotlib 3.3.4 and above
  - numpy 1.19.5 and above

## Quick Start
### Configure AWS Client
You need an AWS account to run the benchmark on Amazon AWS. After the account creation, you need to get a `AWS Access Key ID` and a `AWS Secret Access Key`. Enter `IAM` service on the AWS console. Choose `Users` option in `Access Management` panel. Then, click `Create access key` button to get a `AWS Access Key ID`. You will also got the `Secret Access Key` here. Keep it in a safe place.

Configure your AWS Client with the following command:

```
aws configure
```

You need to input your `AWS Access Key ID` and `AWS Secret Access Key` here. You could also choose a region to set up your cluster on AWS.

### Create a cluster
Download this Benchmark with a git command:

```
git clone https://github.com/PasaLab/OLAPBenchmark.git
cd OLAPBenchmark
mkdir log
```

You need to input your username and password of GitHub to download it.

AWS uses a **EC2 key pair** to keep and manage clusters. Enter `EC2` dashboard and choose `Key Pairs` option in `Network & Security` panel. Then, click `Create key pair` button. Enter your key pair name and use `.pem` format. You will get a `.pem` file to download. Download the file into the project under the `./cloud` directory. You have to keep this file private in order to use it. For linux-base systems, run the following command:

```
chmod 600 ./cloud/*.pem
```

For new users to Amazon AWS, you must test if your account can create a cluster. Enter the `EMR` dashboard and click `create cluster` button. Use your EC2 key pair in `Security and access` option. Then, click `create cluster`. Now you need to wait for the cluster to launch. During the process here, you need to note the following security settings:
- Your subnet ID
- Your security groups for Master
- Your security groups for Core

After recording these settings, you could shut down the test cluster.

Configure the above-mentioned security-related settings in `./cloud/ec2-attributes.json`. You need to configure your `SubnetId`, `KeyName`, `EmrManagedSlaveSecurityGroup` and `EmrManagedMasterSecurityGroup` here.

Then, create a cluster for the benchmark.

```
python3 ./prepare.py
```

The application will monitor the process of cluster creation. After the end of the application, users can see the info of the created nodes of the cluster in `./cloud/instances.csv`. Here, you can see the public and privete DNS addresses of all nodes in the cluster. The first line refers to the master nodes, and slave nodes are in the following lines.

### Set up your cluster
Connect to the nodes of the cluster with the `.pem` key file and public DNS address, like:
```
ssh -i "./cloud/YOURKEYNAME.pem" hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com
```

After confirmation, you are connected to the EMR node. Now you can create the environment needed for benchmark testing.

For master nodes, run the following commands:
```
cd ~
sudo yum -y install git
sudo python3 -m pip install boto3 pyhive
sudo python3 -m pip install --upgrade pyyaml
sudo chmod -R 777 /tmp
git clone https://github.com/gregrahn/tpch-kit
cd ~/tpch-kit/dbgen
make
cd ~
sudo yum -y install collectd
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# for spark-sql users
sudo python3 -m pip install pyspark
# for kylin users
sudo python3 -m pip install requests
# for presto users
sudo python3 -m pip install presto-python-client

git clone https://github.com/PasaLab/OLAPBenchmark

cd OLAPBenchmark
mkdir log
```

For slave nodes, run the following command:
```
cd ~
sudo yum -y install git
sudo yum -y install collectd
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

The cluster is installed with Spark-SQL and Presto by default. If the user wants to install and test other engines, the user has to run their own commands. Take Apache Kylin 3.1 as an example:

```
wget https://downloads.apache.org/kylin/apache-kylin-3.1.2/apache-kylin-3.1.2-bin-hbase1x.tar.gz
tar -zxvf apache-kylin-3.1.2-bin-hbase1x.tar.gz
mv apache-kylin-3.1.2-bin-hbase1x kylin
export KYLIN_HOME=/home/hadoop/kylin
export HIVE_HOME=/usr/lib/hive
export HIVE_CONF_DIR=/usr/lib/hive/conf
export PATH=$PATH:$KYLIN_HOME/bin:$HIVE_HOME/bin
cd kylin
mkdir ext
cp /usr/lib/hive/lib/hive-metastore-2.3.6-amzn-1.jar ext
export hive_dependency=$HIVE_HOME/conf:$HIVE_HOME/lib/*:$HIVE_HOME/lib/hive-hcatalog-core.jar
vim bin/kylin.sh
# Modify line 54 to: export HBASE_CLASSPATH_PREFIX=${KYLIN_HOME}/conf:${KYLIN_HOME}/lib/*:${KYLIN_HOME}/ext/*:${hive_dependency}:${HBASE_CLASSPATH_PREFIX}

./bin/check-env.sh
/home/hadoop/kylin/bin/kylin.sh start
```

### Configuration
With the built environment, you need to perform some configuration to run tests. All configurations are in `./config` directory on the master node.

#### Choose your template
`./config/config.yaml` defines the templates to be used for the benchmark. For example:
```
engine: spark-sql/kylin/presto
workload: tpc-h
test_plan: one-pass/one-pass-concurrent/one-offline-multi-online
metrics: all/time
```

#### Your engine
All engine-related configurations are in `./config/engines` directory. For the engine the user selected, the according file can be edited. Take SparkSQL as an example, users can edit the name of the session, and put system-level configurations here. To integrate SparkSQL with Hive well on cloud, the following settings are necessary:
```
  hive.metastore.uris: thrift://ip-a-b-c-d.YOURREGION.compute.internal:9083
  spark.sql.warehouse.dir: hdfs://ip-a-b-c-d.YOURREGION.compute.internal:8020/user/hive/warehouse
```
Here, internal DNS address of the master node is needed. It can be found in `./cloud/instances.csv`.

For the Presto engine, internal DNS address of the master node is necessary. The following configurations are correct:
```
  host: ip-a-b-c-d.ap-southeast-1.compute.internal
  port: 8889
```

Some engines have their own way of configuring. Therefore, users need to follow the instructions to configure from developers of that engine.

#### Your workloads
Your workloads-related configurations are in `./config/workloads` directory. A valid host address, and a desirable database name for hive-based operations, are mandatory:
```
  host: ip-a-b-c-d.ap-southeast-1.compute.internal
  database: tpch
```

For new users, another major focus is on enabling and disabling the steps in execution. There are three switches controlling whether to run these steps:
- `generate`: Whether to generate data locally and update the generated data to S3.
- `create`: Whether to create data tables into the dataset of the cluster. If data tables have been created, this option should be switched off.
- `load`: Whether to load data from S3. If the data has been loaded once and no new data is created, this option should be switched off.

Advanced users can change the SQLs of the workload as well as the commands of generating, loading data and creating data tables.

#### Your test plan
Test-plan-related configurations are located in `./config/testplans` directory. For new users, they do not need to edit test plan files specifically.

Advanced users can add and remove stages, changing the name, description, concurrency, commands (for offline stages) and queries (for online stages) in the `.yaml` file.

#### Your metrics
Metric-related configurations are in `./config/metrics` directory. New users could use one of the files directly.

Advanced users can change the metrics to be calculated as well as the way to generate the total cost score with the calculated values above with weight. All formulae should follow the grammar rules of python's `eval` function.

This benchmark uses cloud watch service to get metric data. The configuration of `CWAgent` on AWS machines can be edited in `./cloud/cwaconfig.json`. You can reference `CWAgent` documents on AWS to configure this file.

#### Copy your configuration to other machines
Switch to your machine, use `scp` command to send configured project to your machine:

```
# in your benchmark directory
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/OLAPBenchmark/config ./
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/OLAPBenchmark/cloud/cwaconfig.json ./cloud/
```
Public DNS address of the master node of the cluster is needed.

Then, send these files to slave nodes of the cluster.
```
# in your benchmark directory
cd ..
scp -i ./OLAPBenchmark/cloud/YOURPEM.pem -r ./OLAPBenchmark hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/
```
Public DNS addresses of the slave nodes of the cluster is needed.

### Generate the workloads
Use the following command to generate the workloads:
```
# on master node
cd ~/OLAPBenchmark
python3 main.py generate
```

### Monitor and execution
Launch `CWAgent` on all machines of the cluster:
```
# on all machines of the cluster
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/hadoop/OLAPBenchmark/cloud/cwaconfig.json
```

Then, launch the benchmark on the master node:
```
# on master node
cd ~/OLAPBenchmark
python3 main.py run
```
The user needs to remember the time when the benchmark starts and finishes.

After execution, stop `CWAgent` on all machines:
```
# on all machines of the cluster
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop
```

### Download metrics and calculate score
Metrics contains three parts. `online_time` and `offline_time` are timestamps of all commands and queries, which are stored in the benchmark after execution. Other metrics are saved in `CWAgent`, which needs to collect by calling the cloud watch service.

Users could use `scp` command to download those timestamps to your machine:
```
# in your benchmark directory
mkdir metrics
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/OLAPBenchmark/offline_times ./metrics/
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/OLAPBenchmark/online_times ./metrics/
```

Other metrics can be collected when running the calculation script. It will also be saved in `./metrics/metric`.

You have known the start and finish time of the application. With that two timestamps, run the following commands to get the cost score:
```
python3 ./monitor.py j-YOURCLUSTERID START_TIME FINISH_TIME
```
Your cluster ID is available in `./log/benchmark.log` of your local machine. If you have downloaded the metric file of `CWAgent` in `./metrics/metric`, you can run
```
python3 ./monitor.py -1 START_TIME FINISH_TIME
```
instead to avoid the time limit of collecting metrics on `CWAgent`.

The benchmark will give you the final score on the screen. Since the benchmark finished, now you can stop the cluster and release all resources.
```
aws emr terminate-clusters --cluster-ids j-YOURCLUSTERID
```
Your cluster ID is available in your command given above.

## Benchmark Demo
// TODO

## Contributing
// TODO

## Open Source License
// TODO
