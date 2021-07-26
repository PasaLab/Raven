# Get Started with Apache Kylin
## Installation
The cluster is not installed with Apache Kylin by default. To install Kylin in your cluster, you need to download it first:
```shell
cd ~
wget https://downloads.apache.org/kylin/apache-kylin-3.1.2/apache-kylin-3.1.2-bin-hbase1x.tar.gz
tar -zxvf apache-kylin-3.1.2-bin-hbase1x.tar.gz
mv apache-kylin-3.1.2-bin-hbase1x kylin
```

Then, you need to configure it to run on AWS.

### Solve dependency conflicts
Configure `conf/kylin_job_conf.xml` and add the following property:
```xml
    <property>
        <name>hbase.zookeeper.quorum</name>
        <value>localhost</value>
    </property>
```

Adding the following contents to `~/.bashrc`:
```shell
export HIVE_HOME=/usr/lib/hive
export HADOOP_HOME=/usr/lib/hadoop
export HBASE_HOME=/usr/lib/hbase
export SPARK_HOME=/usr/lib/spark
export KYLIN_HOME=/home/hadoop/kylin
export HCAT_HOME=/usr/lib/hive-hcatalog
export KYLIN_CONF_HOME=$KYLIN_HOME/conf
export tomcat_root=$KYLIN_HOME/tomcat
export hive_dependency=$HIVE_HOME/conf:$HIVE_HOME/lib/*:$HIVE_HOME/lib/hive-hcatalog-core.jar:/usr/share/aws/hmclient/lib/*:$SPARK_HOME/jars/*:$HBASE_HOME/lib/*.jar:$HBASE_HOME/*.jar:$HIVE_HOME/lib/hive-exec-2.3.6-amzn-2.jar,$HIVE_HOME/lib/hive-metastore.jar,$HIVE_HOME/lib/hive-metastore-2.3.6-amzn-2.jar,$HIVE_HOME/lib/hive-exec.jar,$HIVE_HOME/lib/hive-hcatalog-core-2.3.6-amzn-2.jar
export PATH=$KYLIN_HOME/bin:$PATH
```

Make the changes take effect:
```shell
source ~/.bashrc
```

Configure Hive jar dependencies:
```shell
sudo mv $HIVE_HOME/lib/jackson-datatype-joda-2.4.6.jar $HIVE_HOME/lib/jackson-datatype-joda-2.4.6.jar.backup
```

Edit `./bin/kylin.sh`:
```shell
export HBASE_CLASSPATH_PREFIX=${tomcat_root}/bin/bootstrap.jar:${tomcat_root}/bin/tomcat-juli.jar:${tomcat_root}/lib/*:$hive_dependency:$HBASE_CLASSPATH_PREFIX
```

Configure in `./conf/kylin.properties`:
```shell
kylin.engine.spark-conf.spark.yarn.archive=PATH_TO_SPARK_LIB
```

Replace conflicting jar files them with correct ones and upload it to hdfs:
```shell
rm -rf $KYLIN_HOME/spark_jars
mkdir $KYLIN_HOME/spark_jars
cp /usr/lib/spark/jars/*.jar $KYLIN_HOME/spark_jars
cp -f /usr/lib/hbase/lib/*.jar $KYLIN_HOME/spark_jars
rm -f $KYLIN_HOME/spark_jars/netty-3.9.9.Final.jar 
rm -f $KYLIN_HOME/spark_jars/netty-all-4.1.8.Final.jar
jar cv0f spark-libs.jar -C $KYLIN_HOME/spark_jars .
hadoop fs -mkdir /kylin
hadoop fs -mkdir /kylin/package
hadoop fs -put spark-libs.jar /kylin/package/
```
By now, you have solved dependency conflicts of Kylin on an EMR cluster.

### Start a Kylin instance
Now, launch Kylin:
```shell
$KYLIN_HOME/bin/kylin.sh start
```

You can build up a tunnel to the remote instance to check if you have launched Kylin properly. For Windows devices, you can use SSH tools like `XShell` to build up a tunnel. For Linux-based devices,
 you can build a tunnel by running the following command on your local machine:
```shell
ssh -i "./cloud/YOURKEYNAME.pem" -N hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com -L 7070:localhost:7070
```

Visit `localhost:7070`, you can see the login page of Kylin. Till now, a working Kylin instance is available.

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
```

The script also creates a few simple views on top of the original TPC-H tables to allow Kylin pre-calculate some complex measures. The resulted E-R model topology is identical to the original TPC-H model.

After that, enter the web UI and click `System` - `Reload Metadata` to refresh the newly imported `tpch` model. 

After the operations above, you can run the benchmark to utilize kylin cubing as part of offline computation by configuring the test plans like this:
```yaml
  commands:
    - path: /home/hadoop/kylin-tpch
      command: sh ./setup-kylin-model.sh 1
    - path: /home/hadoop/OLAPBenchmark/lib
      command: python3 ./kylin_cubing.py
```

Attention:
1. Kylin requires database name in a format of `tpch_flat_orc_*`, * refers to the scale of TPC-H datasets. You also need to configure the scale size in the second command, like `sh ./setup-kylin-model.sh *`.
2. You need to keep the tunnel connected to keep the session alive.
