# Raven

## 目录

- [背景](#背景)
- [安装](#安装)
- [使用说明](#使用说明)
    - [配置 AWS 客户端](#配置-AWS-客户端)
    - [创建集群](#创建集群)
    - [配置集群](#配置集群)
    - [生成工作负载](#生成工作负载)
    - [监控和执行](#监控和执行)
    - [下载指标和计算得分](#下载指标和计算得分)
- [示例](#示例)
- [使用许可](#使用许可)

## 背景

在大数据和云计算时代，大量企业选择在公有云平台（例如亚马逊云、阿里云等）上搭建数据仓库，并使用 OLAP 技术实现的高效数据分析。

如何以较低的成本、较高的效率进行数据分析，加速数据决策，对提高企业竞争力具有重要意义。

与此同时，业界出现了种类繁多的 OLAP 技术（例如 Spark-SQL、Presto、Apache Kylin 等），企业在进行技术选型时，需要对不同 OLAP 技术的性能和成本作出评估。

本项目则是一套针对云上 OLAP 技术进行性能成本评估的基准测试工具。

## 安装

Python 版本：`3.6+`。 

使用如下命令安装你所需的 Python 环境：

```bash
$ pip install -r requirements.txt
```

## 使用说明

### 配置 AWS 客户端

你需要申请一个 AWS 账户以便在 Amazon AWS 上运行该基准测试。

在创建账户之后，你需要获取 AWS 访问密钥ID： `AWS Access Key ID` 和 AWS 访问私钥：`AWS Secret Access Key`。

使用如下命令配置你的 AWS 客户端：

```bash
aws configure
```

然后你需要键入你的 `AWS Access Key ID` 和 `AWS Secret Access Key`，此外，你也可以指定 AWS 区域。

### 创建集群

使用如下命令下载本仓库并切换工作目录到该仓库下：

```bash
$ git clone https://github.com/PasaLab/Raven.git
$ cd Raven
```

AWS 使用 EC2 密钥对来管理集群。进入 EC2 仪表盘、点击 `Network & Security` 中的  `Key Pairs` 选项卡。然后，点击 `Create key pair` 按钮。键入你的密钥对名称并选择 `.pem` 格式。你将会自动下载一个后缀名为 `.pem`  的文件，将其放在项目的 `./cloud` 目录下。你需要将该设为私有然后再使用它。

在 linux 上运行如下命令：

```bash
$ chmod 600 ./cloud/*.pem
```

对于 Amazon AWS 的新用户，你需要测试你的账号是否具有创建集群的权限。进入 `EMR` 仪表盘，点击 `create cluster` 按钮。现在你需要等待集群启动，在词过程中，你需要记住如下安全设定：

- 子网 ID
- 主节点（master）所属安全组
- 工作节点（core）所属安全组

你需要为你的集群实例和应用来安装，请参考[如何配置集群实例](./doc/how-to-configure-instances-of-a-cluster.md)。

执行如下命令为基准测试创建所需集群：

```bash
python3 ./prepare.py
```

该脚本将会监控集群创建过程，在脚本执行结束后，你可以在 `./cloud/instances` 文件中查看集群的节点信息。

## 配置集群

通过使用 `.pem` 密钥文件和公开 DNS 地址远程登陆到集群节点上：

```bash
ssh -i ./cloud/KEYNAME.pem hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com
```

命令也存储在 `./cloud/instances` 中。

#### 部署引擎

现在你可以创建运行基准测试所需的集群环境。不同的引擎具有不同的配置步骤，查看下面的说明文档来部署引擎：

| 引擎         | 说明文档                                                     |
| ------------ | ------------------------------------------------------------ |
| Spark-SQL    | [Get started with Spark-SQL](./doc/get-started-with-Spark-SQL.md) |
| Presto       | [Get started with Presto](./doc/get-started-with-Presto.md)  |
| Apache Kylin | [Get started with Apache Kylin](./doc/get-started-with-Apache-Kylin.md) |

#### 准备工作负载

你需要安装如下步骤来配置工作负载，请查看下面的说明文档：

| 工作负载 | 说明文档                                                   |
| -------- | ---------------------------------------------------------- |
| TPC-H    | [实现 TPC-H 工作负载](./doc/implementing-tpch-workload.md) |

#### 测试计划

测试计划相关的配置文件存储在 `.config/testplans` 文件中，新用户不需要专门修改测试计划相关文件。

高级用户可以 `.yaml` 配置文件中添加和移除阶段（stage），修改名称、描述、并发度，命令（离线阶段）和查询（在线阶段）。

#### 指标

本基准测试工具使用 `CWAgent` 在查询执行期间监控有关指标。

你需要在集群所有实例上执行如下命令来安装 `CWAgent`：

```bash
$ sudo yum -y install collectd
$ wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
$ sudo rpm -U ./amazon-cloudwatch-agent.rpm
```

与指标相关的配置文件在 `./config/metrics` 目录中，新用户可以直接使用其中一个文件。

本基准测试工具使用 `Amazon CloudWatch` 服务来获取指标数据，相应的配置文件位于 `./cloud/cwaconfig.json`，你可以参考 AWS 上的 `CWAgent` 文档来配置此文件。

#### 通用配置

基于上述构建的环境，你需要修一些配置项来运行基准测试，所有配置都在主节点上的 `./config` 目录中。`config/config.yaml` 定义了用于基准测试的模板，例如：

```yaml
engine: spark-sql/kylin/presto
workload: tpc-h
test_plan: one-pass/one-pass-concurrent/one-offline-multi-online
metrics: all/time
```

#### 分发配置

切换到你的本地机器，使用 `scp` 命令分发你的配置到所有集群节点中：

```bash
# in your benchmark directory
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/config ./
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/cloud/cwaconfig.json ./cloud/
```

### 生成工作负载

在 master 节点上执行如下命令来生成工作负载：

```bash
# on master node
$ cd ~/Raven
$ python3 main.py generate
```

### 监控和执行

1. 在集群所有节点上使用如下命令安装 `CWAgent`：

    ```bash
    # on all machines of the cluster
    $ sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/hadoop/Raven/cloud/cwaconfig.json
    ```

2. 在 master 节点上启动基准测试：

    ```bash
    # on master node
    $ cd ~/Raven
    $ python3 main.py run
    ```

    用户需要记住基准测试启动和结束的时间。

3. 在执行结束之后，停止所有节点上运行的 `CWAgent`：

    ```bash
    # on all machines of the cluster
    $ sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop
    ```

### 下载指标和计算得分

指标包含三个部分，`online_time` 和 `offline_time` 是命令和查询的时间戳，由基准测试框架存储。

其他的指标存储在 `CWAgent` 上，需要调用相应的云服务来获取。

用户可以使用 `scp` 命令将指标下载至本地：

```bash
# in your benchmark directory
mkdir metrics
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/offline_times ./metrics/
scp -i ./cloud/YOURPEM.pem -r hadoop@ec2-a-b-c-d.YOURREGION.compute.amazonaws.com:~/Raven/online_times ./metrics/
```

其他的指标可以通过运行计算脚本来获取，计算出来的指标存储在 `$RAVEN/metrics/metric` 中。

你已经知道基准测试开始和结束的时间，基于这两个时间戳，运行如下命令获得成本得分：

```bash
$ python3 ./monitor.py j-YOURCLUSTERID
```

其中你的集群 ID 存储在本地 `./log/benchmark.log` 日志文件中。

如果你已经下载了 `CWAgent` 的指标文件 `./metrics/metric`，你也可以运行如下命令以避免收集 `CWAgent` 上的时间限制：

```bash
$ python3 ./monitor.py -1 START_TIME FINISH_TIME
```

基准测试框架将会在控制台输出最终得分。

在基准测试结束之后，你可以关闭集群并释放所有资源：

```bash
$ aws emr terminate-clusters --cluster-ids j-YOURCLUSTERID
```

## 示例

[![Demo](http://img.videocc.net/uimage/0/09626a691b/d/09626a691bfcd2ed7b4c6e8fc80a4c7d_0.jpg)](http://go.plvideo.cn/front/video/preview?vid=09626a691bfcd2ed7b4c6e8fc80a4c7d_0)

## 开源许可

Raven 基于 Apache 2.0 协议开源，详细信息见 [LICENSE](LICENSE)。
