# Raven

## Table of Contents

- [Background](#background)
- [Install](#Install)
- [Usage](#usage)
    - [Configure AWS Client](#configure-aws-client)
    - [Create a cluster](#create-a-cluster)
    - [Set up your cluster](#set-up-your-cluster)
    - [Generate the workloads](#generate-the-workloads)
    - [Monitor and execution](#monitor-and-execution)
    - [Download metrics and calculate score](#download-metrics-and-calculate-score)
- [Example](#example)
- [License](#License)

## Background

In the era of big data and cloud computing, a large number of companies choose to build data warehouses on public cloud platforms (such as Amazon Cloud, Alibaba Cloud, etc.) and use OLAP technology to perform efficient data analysis.

How to conduct data analysis with lower cost and higher efficiency and speed up data decision-making is of great significance to improving the competitiveness of enterprises.

At the same time, a wide variety of OLAP technologies have emerged in the industry (such as Spark-SQL, Presto, Apache Kylin, etc.). When selecting technologies, companies need to evaluate the performance and cost of different OLAP technologies.

This project is a bemchmark framework for performance cost evaluation of OLAP technology on the cloud.

## Install

Install python requirements with the following command.

```bash
$ pip install -r requirements.txt
```

## Usage

### Configure AWS Client

You need an AWS account to run the benchmark on Amazon AWS. After the account creation, you need to get a `AWS Access Key ID` and a `AWS Secret Access Key`. Enter `IAM` service on the AWS console. Choose `Users` option in `Access Management` panel. Then, click `Create access key` button to get a `AWS Access Key ID`. You will also got the `Secret Access Key` here. Keep it in a safe place.

Configure your AWS Client with the following command:

```shell
aws configure
```

You need to input your `AWS Access Key ID` and `AWS Secret Access Key` here. You could also choose a region to set up your cluster on AWS.

### Create a cluster

Download this Benchmark with a git command:

```shell
git clone https://github.com/PasaLab/Raven.git

cd Raven
```

You need to input your username and password of GitHub to download it.

AWS uses a **EC2 key pair** to keep and manage clusters. Enter `EC2` dashboard and choose `Key Pairs` option in `Network & Security` panel. Then, click `Create key pair` button. Enter your key pair name and use `.pem` format. You will get a `.pem` file to download. Download the file into the project under the `./cloud` directory. You have to keep this file private in order to use it. For linux-base systems, run the following command:

```shell
chmod 600 ./cloud/*.pem
```

For new users to Amazon AWS, you must test if your account can create a cluster. Enter the `EMR` dashboard and click `create cluster` button. Use your EC2 key pair in `Security and access` option. Then, click `create cluster`. Now you need to wait for the cluster to launch. During the process here, you need to note the following security settings:
- Your subnet ID
- Your security groups for Master
- Your security groups for Core

After recording these settings, you could shut down the test cluster.

You need to configure instances and applications to install for your cluster, please refer to [this instruction](./doc/how-to-configure-instances-of-a-cluster.md). Then, create a cluster for the benchmark:

```shell
python3 ./prepare.py
```

The application will monitor the process of cluster creation. After the end of the application, users can see the info of the created nodes of the cluster in `./cloud/instances`. Here, you can see the public and privete DNS addresses of all nodes in the cluster. The first line refers to the master nodes, and slave nodes are in the following lines.

### Set up your cluster

Connect to the nodes of the cluster with the `.pem` key file and public DNS address, like:
```shell
ssh -i "./cloud/YOURKEYNAME.pem" hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com
```

This command is also available in `./cloud/instances`.

#### Build your engine

Now you can create the environment needed for benchmark testing. Different engines have different environment set-up procedures. Please follow the instructions below:

|Engine Name|Instruction|
|---|---|
|Spark-SQL|[Get started with Spark-SQL](./doc/get-started-with-Spark-SQL.md)|
|Presto|[Get started with Presto](./doc/get-started-with-Presto.md)|
|Apache Kylin|[Get started with Apache Kylin](./doc/get-started-with-Apache-Kylin.md)|

#### Prepare for the workload

You need to go through different procedures to set up your workload. Please follow the instructions below:

|Workload Name|Instruction|
|---|---|
|TPC-H|[Implementing TPC-H workload](./doc/implementing-tpch-workload.md)|

#### Your test plan

Test-plan-related configurations are located in `./config/testplans` directory. For new users, they do not need to edit test plan files specifically.

Advanced users can add and remove stages, changing the name, description, concurrency, commands (for offline stages) and queries (for online stages) in the `.yaml` file.

#### Your metrics

This benchmark uses CWAgent to monitor metrics during the execution of queries. To make `CWAgent` available on AWS clusters, you need to install it on all instances of the cluster. Run the following commands in all instances of the cluster:

```shell
sudo yum -y install collectd
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

Metric-related configurations are in `./config/metrics` directory. New users could use one of the files directly.

Advanced users can change the metrics to be calculated as well as the way to generate the total cost score with the calculated values above with weight. All formulae should follow the grammar rules of python's `eval` function.

This benchmark uses cloud watch service to get metric data. The configuration of `CWAgent` on AWS machines can be edited in `./cloud/cwaconfig.json`. You can reference `CWAgent` documents on AWS to configure this file.

#### General Configuration

With the built environment, you need to perform some configuration to run tests. All configurations are in `./config` directory on the master node.

`./config/config.yaml` defines the templates to be used for the benchmark. For example:
```yaml
engine: spark-sql/kylin/presto
workload: tpc-h
test_plan: one-pass/one-pass-concurrent/one-offline-multi-online
metrics: all/time
```

#### Copy your configuration to other machines

Switch to your machine, use `scp` command to send configured project to your machine:

```shell
# in your benchmark directory
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/config ./
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/cloud/cwaconfig.json ./cloud/
```
Public DNS address of the master node of the cluster is needed.

Then, send these files to slave nodes of the cluster.
```shell
# in your benchmark directory
cd ..
scp -i ./Raven/cloud/YOURPEM.pem -r ./Raven hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/
```
Public DNS addresses of the slave nodes of the cluster is needed.

### Generate the workloads

Use the following command to generate the workloads:
```shell
# on master node
cd ~/Raven
python3 main.py generate
```

### Monitor and execution

Launch `CWAgent` on all machines of the cluster:
```shell
# on all machines of the cluster
$ sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/hadoop/Raven/cloud/cwaconfig.json
```

Then, launch the benchmark on the master node:
```shell
# on master node
$ cd ~/Raven
$ python3 main.py run
```
The user needs to remember the time when the benchmark starts and finishes.

After execution, stop `CWAgent` on all machines:
```shell
# on all machines of the cluster
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop
```

### Download metrics and calculate score

Metrics contains three parts. `online_time` and `offline_time` are timestamps of all commands and queries, which are stored in the benchmark after execution. Other metrics are saved in `CWAgent`, which needs to collect by calling the cloud watch service.

Users could use `scp` command to download those timestamps to your machine:
```shell
# in your benchmark directory
mkdir metrics
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/offline_times ./metrics/
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/online_times ./metrics/
```

Other metrics can be collected when running the calculation script. It will also be saved in `./metrics/metric`.

You have known the start and finish time of the application. With that two timestamps, run the following commands to get the cost score:
```shell
python3 ./monitor.py j-YOURCLUSTERID
```
Your cluster ID is available in `./log/benchmark.log` of your local machine. If you have downloaded the metric file of `CWAgent` in `./metrics/metric`, you can run
```shell
python3 ./monitor.py -1 START_TIME FINISH_TIME
```
instead to avoid the time limit of collecting metrics on `CWAgent`.

The benchmark will give you the final score on the screen. Since the benchmark finished, now you can stop the cluster and release all resources.
```shell
aws emr terminate-clusters --cluster-ids j-YOURCLUSTERID
```
Your cluster ID is available in your command given above.

## Example

[![Demo](http://img.videocc.net/uimage/0/09626a691b/d/09626a691bfcd2ed7b4c6e8fc80a4c7d_0.jpg)](http://go.plvideo.cn/front/video/preview?vid=09626a691bfcd2ed7b4c6e8fc80a4c7d_0)

## License

Raven is under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.