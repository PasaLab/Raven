# Implementing TPC-H Workload
## Using TPC-H kit for dataset generation
Here, we use open-sourced tpch-kit by gregrahn to generate the workload. Run the following commands:
```shell
cd ~
sudo yum -y install git
git clone https://github.com/gregrahn/tpch-kit
cd ~/tpch-kit/dbgen
make
```
Now, you can see an executable package in `/home/hadoop/tpch-kit` directory. The benchmark can find and execute this kit automatically.

## Configuration
You can configure this workload at `./config/workloads/tpch.yaml`.

### Set your host address and database name
A valid host address, and a desirable database name for hive-based operations, are mandatory:
```yaml
  host: localhost
  database: tpch
```

### Manage switches of workload generation
For new users, another major focus is on enabling and disabling the steps in execution. There are three switches controlling whether to run these steps:
- `generate`: Whether to generate data locally and update the generated data to S3.
- `create`: Whether to create data tables into the dataset of the cluster. If data tables have been created, this option should be switched off.
- `load`: Whether to load data from S3. If the data has been loaded once and no new data is created, this option should be switched off.

### Manage query SQLs
Advanced users can change the SQLs of the workload as well as the commands of generating, loading data and creating data tables. For different engines, we have different descriptions of query SQLs with the same meaning. Users can choose desirable SQLs from either `tpch-standard.yaml` or `tpch-for-kylin.yaml`.