# on master
sudo yum -y install git
sudo python3 -m pip install boto3
sudo python3 -m pip install pyspark
sudo python3 -m pip install requests
sudo python3 -m pip install --upgrade pyyaml
sudo chmod -R 777 /tmp
git clone https://github.com/gregrahn/tpch-kit
cd ~/tpch-kit/dbgen
make
cd ~
git clone https://github.com/PasaLab/OLAPBenchmark

# on slaves
sudo yum -y install git
git clone https://github.com/PasaLab/OLAPBenchmark

# on all machines
sudo yum -y install collectd
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# on master
cd ~/OLAPBenchmark
mkdir log
python3 main.py generate

# on all machines
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/hadoop/OLAPBenchmark/cloud/cwaconfig.json

# on master
cd ~/OLAPBenchmark
python3 main.py run

# on all machines
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop

# kylin engine
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
./bin/check-env.sh

/home/hadoop/kylin/bin/kylin.sh start

/home/hadoop/kylin/bin/kylin.sh stop
