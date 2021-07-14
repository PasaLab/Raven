# How to configure instances of a cluster
## ./cloud/cluster.sh
This file is the command to create a cluster via AWS CLI. It begins with the base command `aws emr create-cluster`. The rest of the text are options of the clusters. You can make changes of them according to your needs. Important options are:

|Option|Default Value|Description|
|---|---|---|
|applications|`Name=Hadoop ...`|Define applications you need to create an EMR cluster*
|ec2-attributes|`file://cloud/ec2-attributes.json`|Attributes of the EC2 instances. See [here](#./cloud/ec2-attributes.json).
|instance-groups|`file://cloud/instance-groups.json`|Configuration for your cluster. See [here](#./cloud/instance-groups.json).
|name|`olap_test`|The name of the cluster
|region|`ap-southeast-1`|Your region to create the cluster|
|release-label|`emr-5.29.0`|Define the version of applications

*: Some engines require specific applications. Please refer to the following table to get the applications to install:

|Engine|Applications to Install|
|---|---|
|Spark-SQL|Name=Hadoop Name=Hive Name=HBase Name=Spark|
|Presto|Name=Hadoop Name=Hive Name=HBase Name=Presto|
|Apache Kylin|Name=Hadoop Name=Hive Name=HBase Name=Zookeeper|

## ./cloud/ec2-attributes.json
This file defines attributes of the EC2 instances, most of whom are security-related.

Assume you have noted the following settings in the previous cluster:
- Your subnet ID
- Your security groups for Master
- Your security groups for Core

Now you can configure the above-mentioned security-related settings in `./cloud/ec2-attributes.json`. You need to configure your `SubnetId`, `KeyName`, `EmrManagedSlaveSecurityGroup` and `EmrManagedMasterSecurityGroup` here.

## ./cloud/instance-groups.json
This file defines configurations of the instances in the cluster. This file is using a JSON format, so you can add and remove instance groups by modifying items in the array. For each instance group, the following configurations are critical:

|Configuration|Default Value for MASTER|Default Value for CORE|Description|
|---|---|---|---|
|InstanceCount|`1`|`2`|Number of instances in this group
|BidPrice|`OnDemandPrice`|`OnDemandPrice`|Defines SPOT charging mechanism
|EbsConfiguration|`{...}`|`{...}`|Defines hard disks of instances
|InstanceType|`m4.large`|`m4.2xlarge`|Defines the instance type