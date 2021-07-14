# Get Started with Apache Kylin
## Installation
The cluster is not installed with Apache Kylin by default. To install Kylin in your cluster, you need to download and configure Web UI dependencies first:
```shell
cd ~
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
/home/hadoop/kylin/bin/kylin.sh start
```

Now, build up a tunnel to the remote instance to check if you have launched Kylin properly. For Windows devices, you can use SSH tools like `XShell` to build up a tunnel. For Linux-based devices,
 you can build a tunnel by running the following command on your local machine:
```shell
ssh -i "./cloud/YOURKEYNAME.pem" -N hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com -L 7070:localhost:7070
```

Visit `localhost:7070`, you can see the login page of Kylin. However, Hive is still not runnable here due to lack of hive dependencies. Stop the Kylin instance:

```shell
/home/hadoop/kylin/bin/kylin.sh stop
```

Add hive dependency:
```shell
export hive_dependency=$HIVE_HOME/conf:$HIVE_HOME/lib/*:$HIVE_HOME/lib/hive-hcatalog-core.jar
```

Modify `/home/hadoop/kylin/bin/kylin.sh`, change line 54 into:
```shell
export HBASE_CLASSPATH_PREFIX=${KYLIN_HOME}/conf:${KYLIN_HOME}/lib/*:${KYLIN_HOME}/ext/*:${hive_dependency}:${HBASE_CLASSPATH_PREFIX}
```

Finally, restart the Kylin engine:
```
/home/hadoop/kylin/bin/kylin.sh start
```

Till now, a working Kylin instance is available.

Even though we encountered problems in the installing process, you CANNOT solve two dependency problems together, or those dependency problems would still exist.

## Cluster Environment
To build up the cluster environment, you need prepare for necessary packages for benchmark execution. For the master node, run the following commands:

```shell
cd ~
sudo yum -y install git cyrus-sasl-devel.x86_64
sudo python3 -m pip install boto3 sasl thrift thrift-sasl pyhive requests
sudo python3 -m pip install --upgrade pyyaml
sudo chmod -R 777 /tmp
```

After that, clone our benchmark to the instance:
```shell
cd ~
git clone https://github.com/PasaLab/OLAPBenchmark
```
To clone the benchmark, we need your GitHub account and password here.

## Configuration

Configuration of the Kylin engine are in `$KYLIN_HOME/conf` directory. Users need to follow the instructions from Kylin developers to configure the engine.

## Prepare Kylin Cubes for TPC-H Workload
If you want to use TPC-H as the workload, you can read this part.

Apache Kylin has models to import to run TPC-H queries. You need to get that repository and run `setup-kylin-model.sh` to generate hive data. You SHOULD have Apache Kylin installed before running this script:

```shell
cd ~
git clone https://github.com/Kyligence/kylin-tpch.git
cd kylin-tpch
./setup-kylin-model.sh 2
```

The script also creates a few simple views on top of the original TPC-H tables to allow Kylin pre-calculate some complex measures. The resulted E-R model topology is identical to the original TPC-H model.

After that, enter the web UI and click `System` - `Reload Metadata` to refresh the newly imported `tpch` model. 

After the operations above, you can run the benchmark to utilize kylin cubing as part of offline computation by configuring the test plans like this:
```yaml
  commands:
    - path: /home/hadoop/OLAPBenchmark/lib
      command: python3 ./kylin_cubing.py
```

You need to keep the tunnel connected to keep the session alive.