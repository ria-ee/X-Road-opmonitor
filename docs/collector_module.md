
| [![Republic of Estonia Information System Authority](img/ria_100_en.png)](https://www.ria.ee/en/) [![X-ROAD](img/xroad_100_en.png)](https://www.ria.ee/en/x-road.html) | ![European Union / European Regional Development Fund / Investing in your future](img/eu_rdf_100_en.png "Documents that are tagged with EU/SF logos must keep the logos until 1.11.2022. If it has not stated otherwise in the documentation. If new documentation is created  using EU/SF resources the logos must be tagged appropriately so that the deadline for logos could be found.") |
| :-------------------------------------------------- | -------------------------: |

# X-Road v6 monitor project - Collector Module

## About

The **Collector module** is part of [X-Road v6 monitor project](../README.md), which includes modules of [Database module](database_module.md), Collector module (this document), [Corrector module](corrector_module.md), [Analysis module](analysis_module.md), [Reports module](reports_module.md), [Opendata module](opendata_module.md) and [Networking/Visualizer module](networking_module.md).

The **Collector module** is responsible to retrieve data from X-Road v6 security servers and insert into the database module. The execution of the collector module is performed automatically via a **cron job** task.

It is important to note that it can take up to 7 days for the Collector module to receive X-Road v6 operational data from (all available) security server(s).

Overall system, its users and rights, processes and directories are designed in a way, that all modules can reside in one server (different users but in same group 'opmon') but also in separate servers. 

Overall system is also designed in a way, that allows to monitor data from different X-Road v6 instances (in Estonia `ee-dev`, `ee-test`, `EE`, see also [X-Road v6 environments](https://www.ria.ee/en/x-road-environments.html#v6).

Overall system is also designed in a way, that can be used by X-Road Centre for all X-Road members as well as for Member own monitoring (includes possibilities to monitor also members data exchange partners).

The module source code can be found at:

```
https://github.com/ria-ee/X-Road-opmonitor
```

and can be downloaded into server:

```bash
sudo su - collector
# If HOME not set, set it to /tmp default.
export TMP_DIR=${HOME:=/tmp}
export PROJECT="X-Road-opmonitor"
export PROJECT_URL="https://github.com/ria-ee/${PROJECT}.git"
export SOURCE="${TMP_DIR}/${PROJECT}"
if [ ! -d "${TMP_DIR}/${PROJECT}" ]; then \
    cd ${TMP_DIR}; git clone ${PROJECT_URL}; \
else \
  cd ${SOURCE}; git pull ${PROJECT_URL}; \
fi
```

## Installation

This sections describes the necessary steps to install the **collector module** in a Linux Ubuntu 16.04. To a complete overview of different modules and machines, please refer to the ==> [System Architecture](system_architecture.md) <== documentation.

## Networking

### Outgoing

- The collector module needs http-access to the X-Road CENTRALSERVER to get from global configuration list of members security servers.
- The collector module needs http-access to the current member SECURITY SERVER to get the data is collected.
- The collector module needs access to the Database Module (see ==> [Database_Module](database_module.md) <==).

### Incoming

No incoming connection is needed in the collector module.

## Install required packages

To install the necessary packages, execute the following commands:

```bash
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install pymongo==3.4
sudo pip3 install requests==2.13
sudo pip3 install numpy==1.11
sudo pip3 install tqdm==4.14
```

## Install collector module

The collector module uses the system user **collector** and group **opmon**. To create them, execute:

```bash
sudo useradd --base-dir /opt --create-home --system --shell /bin/bash --gid collector collector
sudo groupadd --force opmon
sudo usermod --append --groups opmon collector
```

Additionally, key-based, password-less accesses betwenn modules are needed:

```bash
#
# Generate keys
#
sudo --user collector ssh-keygen -t rsa
#
# Set reports user and reports server values, also home directory in reports server before usage
# Alternatively, administrative user might be used for that
# Appending public key to a remote file via SSH
#
# export reports_user="reports"; export reports_server="opmon-reports"
sudo --user collector cat /opt/collector/.ssh/id_rsa.pub | \
    ssh ${reports_user}@${reports_server} "cat >> ~reports/.ssh/authorized_keys"
#
# Set networking user and networking server values, also home directory in networking server before usage
# Alternatively, administrative user might be used for that
# Appending public key to a remote file via SSH
#
# export networking_user="networking"; export networking_server="opmon-networking"
sudo --user collector cat /opt/collector/.ssh/id_rsa.pub | \
    ssh ${networking_user}@${networking_server} "cat >> ~networking/.ssh/authorized_keys"
```

The module files should be installed in the APPDIR directory, within a sub-folder named after the desired X-Road instance. 
In this manual, `/srv/app` is used as APPDIR and the `sample` is used as INSTANCE (please change `sample` to map your desired instance).

```bash
export APPDIR="/srv/app"
export INSTANCE="sample"
# Create log and heartbeat directories with group 'opmon' write permission
sudo mkdir --parents ${APPDIR}/${INSTANCE}
sudo mkdir --parents ${APPDIR}/${INSTANCE}/logs
sudo mkdir --parents ${APPDIR}/${INSTANCE}/heartbeat
sudo chown root:opmon ${APPDIR}/${INSTANCE} ${APPDIR}/${INSTANCE}/logs ${APPDIR}/${INSTANCE}/heartbeat
sudo chmod g+w ${APPDIR}/${INSTANCE} ${APPDIR}/${INSTANCE}/logs ${APPDIR}/${INSTANCE}/heartbeat
```

Copy the **collector** code to the install folder and fix the file permissions:

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo cp --recursive --preserve ${SOURCE}/collector_module ${APPDIR}/${INSTANCE}
```

Settings for different X-Road instances have been prepared and can be used:

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo rm ${APPDIR}/${INSTANCE}/collector_module/settings.py
sudo ln --symbolic \
    ${APPDIR}/${INSTANCE}/collector_module/settings_${INSTANCE}.py \
	${APPDIR}/${INSTANCE}/collector_module/settings.py
```

If needed, edit necessary modifications to the settings file using your favorite text editor (here, **vi** is used):

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo vi ${APPDIR}/${INSTANCE}/collector_module/settings.py
```

Correct necessary permissions

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo chown --recursive collector:collector ${APPDIR}/${INSTANCE}/collector_module
sudo chmod --recursive -x+X ${APPDIR}/${INSTANCE}/collector_module
find  ${APPDIR}/${INSTANCE}/collector_module/ -name '*.sh' -type f | sudo xargs chmod u+x
```

## Manual usage

To check collector manually as collector user, execute:

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
cd ${APPDIR}/${INSTANCE}
sudo --user collector ./collector_module/cron_collector.sh update
```

## CRON usage

Add **collector module** as a **cron job** to the **collector** user.

```bash
sudo crontab -e -u collector
```

The **cron job** entry (execute every 3 hours, note that a different value might be needed in production)

```
0 */3 * * * export APPDIR="/srv/app"; export INSTANCE="sample"; cd ${APPDIR}/${INSTANCE}; ./collector_module/cron_collector.sh update >> logs/cron_collector.log
```

To check if the collector module is properly installed in the collector user, execute:

```bash
sudo crontab -l -u collector
```

## Monitoring and Status

### Logging 

The settings for the log file in the settings file are the following:

```python
# --------------------------------------------------------
# General settings
# --------------------------------------------------------
MODULE = "collector"
APPDIR = "/srv/app"
INSTANCE = "sample"
# ...
# --------------------------------------------------------
# Configure logger
# --------------------------------------------------------
# Ensure match with external logrotate settings
LOGGER_NAME = '{0}'.format(MODULE)
LOGGER_PATH = '{0}/{1}/logs/'.format(APPDIR, INSTANCE)
LOGGER_FILE = 'log_{0}_{1}.json'.format(MODULE, INSTANCE)
```

The log file is written to `LOGGER_PATH/LOGGER_FILE`, id est to `${APPDIR}/${INSTANCE}/logs/log_collector_${INSTANCE}.json`.

Every log line includes:

- **"timestamp"**: timestamp in Unix format (epoch)
- **"local_timestamp"**: timestamp in local format '%Y-%m-%d %H:%M:%S %z'
- **"module"**: "collector"
- **"version"**: in form of "v${MINOR}.${MAJOR}"
- **"activity"**: possible valuse "collector_start", "collector_worker", "collector_end"
- **level**: possible values "INFO", "WARNING", "ERROR"
- **msg**: message

In case of "activity": "collector_end", the "msg" includes values separated by comma:

- Total collected: number of Member's Security server from where the logs were collected successfully
- Total error: number of Member's Security server from where the logs were not collected due to error
- Total time: durations in the collection process in time format HH:MM:SS

The **collector module** log handler is compatible with the logrotate utility. To configure log rotation, create the file:

```
sudo vi /etc/logrotate.d/collector_module
```

and add the following content (replace ${APPDIR} `/srv/app` to map your desired application directory and ${INSTANCE} `sample` to map your desired instance; 
check that ${APPDIR}/${INSTANCE}/logs/ matches to `LOGGER_PATH` and 
that ${log_file_name} matches to the name and format of `log_file_name = 'log_{0}_{1}.json'.format(MODULE, INSTANCE)` in `settings.py`):

```
${APPDIR}/${INSTANCE}/logs/${log_file_name} {
    rotate 10
    size 2M
}
```

For further log rotation options, please refer to logrotate manual:

```
man logrotate
```

### Heartbeat

The settings for the heartbeat file in the settings file are the following:

```python
# --------------------------------------------------------
# General settings
# --------------------------------------------------------
MODULE = "collector"
APPDIR = "/srv/app"
INSTANCE = "sample"
# ...
# --------------------------------------------------------
# Heartbeat settings
# --------------------------------------------------------
HEARTBEAT_LOGGER_PATH = '{0}/{1}/heartbeat/'.format(APPDIR, INSTANCE)
HEARTBEAT_FILE = 'heartbeat_{0}_{1}.json'.format(MODULE, INSTANCE)
```

The heartbeat file is written to `HEARTBEAT_LOGGER_PATH/HEARTBEAT_NAME`, id est to `${APPDIR}/${INSTANCE}/heartbeat/heartbeat_collector_${INSTANCE}.json`.

The heartbeat file consists last message of log file and status

- **status**: possible values "FAILED", "SUCCEEDED"

## The external files and additional scripts required for reports and networking modules

External file in subdirectory `${APPDIR}/${INSTANCE}/collector_module/external_files/riha.json` is required for reports generation in [Reports module](reports_module.md) and networking generation on [Networking module](networking_module.md).

Generation of `riha.json` requires additional background file `riha_systems.json`.
RIA system management personell is asked periodically (monthly) to re-generate and update mentioned file in the system according to `https://www.riha.ee/api/v1/systems` as the contact data is not available for anonymous usage but requires authentication. 

Sample queries: 

- Retrieve all systems in RIHA - `https://www.riha.ee/api/v1/systems?topics=%22X-tee%20alams%C3%BCsteem%22&fields=owner,short_name,name,contacts&size=10000`
- Retrieve only X-Road subsystems ('X-tee alamsüsteem') from RIHA - `https://www.riha.ee/api/v1/systems?filter=topics,jilike,%25X-tee%20alams%C3%BCsteem%25&fields=owner,short_name,name,contacts,topics&size=10000`
- Retrieve only X-Road subsystems in use from RIHA -  `https://www.riha.ee/api/v1/systems?filter=topics,jilike,%25X-tee%20alams%C3%BCsteem%25,meta.system_status.status,jilike,%25IN_USE%25&fields=owner,short_name,name,contacts,topics&size=10000`

NB! Parameter `size` in query must exceed value of `totalElements` in response to ensure all data is retrieved from RIHA.

The format of query and response are described in RIHA API Help `https://abi.riha.ee/APIabi` (in Estonian).

### make_riha.sh

Bash script to retrieve subSystem list from X-Road Central Server and complement it with memberName, subsystemName and notification contacts (`subsystems_json_riha.py` and `xrdinfo.py`).

Script requires X-Road Central Server IP / Name as first parameter and must be configured during installation procedure, variable `CENTRAL_SERVER`.

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo vi ${APPDIR}/${INSTANCE}/collector_module/settings.py
```

Script result is saved into file with hardcoded name `riha.json`.

Sample of `${APPDIR}/${INSTANCE}/collector_module/external_files/riha.json`

```json
[
  {
    "subsystem_code": "10000000-name",
    "x_road_instance": "XTEE-CI-XM",
    "member_class": "GOV",
    "subsystem_name": {
      "en": "Company Test X-Road v6 subsystem",
      "et": "Ettevõtte Test X-tee v6 alamsüsteem"
    },
    "member_code": "10000000",
    "email": [
      {
        "name": "Firstname Lastname",
        "email": "firstname.lastname@domain.com"
      }
    ],
    "member_name": "Company Test AS"
  }
]
```

## Generation of riha_$instance.json files and copied into the reports module

The files are currently being generated and copied into the reports module via cron job using SCP.

**Note:** Although the content of `riha.json` is identical for reports and networking module, the generation time in crontab entry must differ to avoid collisions.

```
0 3 * * * export APPDIR="/srv/app"; export INSTANCE="sample"; export reports_user="reports"; export reports_server="opmon-reports"; cd ${APPDIR}/${INSTANCE}/collector_module/external_files && ./make_riha.sh && scp riha.json  ${reports_user}@${reports_server}:${APPDIR}/${INSTANCE}/reports_module/external_files/riha.json
```

## Generation of riha_$instance.json files and copied into the networking module

The files are currently being generated and copied into the networking module via cron job using SCP.

**Note:** Although the content of `riha.json` is identical for reports and networking module, the generation time in crontab entry must differ to avoid collisions.

```
30 3 * * * export APPDIR="/srv/app"; export INSTANCE="sample"; export networking_user="networking"; export networking_server="opmon-networking"; cd ${APPDIR}/${INSTANCE}/collector_module/external_files && ./make_riha.sh && scp riha.json ${networking_user}@${networking_server}:${APPDIR}/${INSTANCE}/networking_module/riha_${INSTANCE}.json
```

## Appendix

NB! Mentioned appendixes below are separate products and do not log their work and do not keep heartbeat similarly as main modules.

### Collecting JSON queries and store into HDD

Collecting JSON queries and store into HDD was not part of the project scope. Nevertheless, sample scripts can be found from directory `${APPDIR}/${INSTANCE}/collector_module/external_files`, files `collector_into_file_cron.sh`, `collector_into_file_list_servers.py` and `collector_into_file_get_opmon.py`. 

Important configuration to set up before usage:

```
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo vi ${APPDIR}/${INSTANCE}/collector_module/external_files/collector_into_file_cron.sh
```

settings:

```bash
# IP or Name of Central Server
CENTRAL_SERVER=""
```

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
sudo vi ${APPDIR}/${INSTANCE}/collector_module/external_files/collector_into_file_get_opmon.py
```

settings:

```
# X-Road instance
INSTANCE = "sample"

# Security server IP or Name used by Central monitoring
SECURITY_SERVER = ""

# Central monitoring subsystem/member (as defined in global configuration)
#
# Message header of Instance Monitoring Client
# MEMBERCLASS is in {GOV, COM, NGO, NEE}
# Sample: MEMBERCLASS = "GOV"
MEMBERCLASS = "GOV"

# MEMBERCODE is registry code of institution
# Sample: MEMBERCODE = "70006317" # RIA, Riigi Infosüsteemi Amet, State Information Agency
MEMBERCODE = "00000001"

# SUBSYSTEMCODE is X-Road subsystem code, to be registered in RIHA, www.riha.ee
# Sample: SUBSYSTEMCODE = "monitoring"
SUBSYSTEMCODE = "Central monitoring client"
```

Usage from command line:

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
cd ${APPDIR}/${INSTANCE}/collector_module/external_files; ./collector_into_file_cron.sh
```

Usage from crontab:
```
5 */6 * * * export APPDIR="/srv/app"; export INSTANCE="sample"; cd ${APPDIR}/${INSTANCE}/collector_module/external_files; ./collector_into_file_cron.sh
```

Timestamps of last log fetched from each X-Road Member Security Server is kept in file `nextRecordsFrom.json` (hardcoded).

Log and cache files generated:

- `collector_into_file_cron.log` - general log, status 0 (success) or 1 (failure)
- `SERVERS_CACHE_NOW` = "${CACHE_DIR}/cache_${CENTRAL_SERVER}_${NOW}.${CACHE_EXT}"
- `SERVERS_CACHE` = "${CACHE_DIR}/cache_${CENTRAL_SERVER}.${CACHE_EXT}" as symbolic link to last $SERVERS_CACHE_NOW}
- `LOG_FILE` = "log_${CENTRAL_SERVER}_${NOW}.${LOG_EXT}"


### Collecting JSON queries from HDD

It is possible to read JSON queries from HDD files produced by `collector_into_file_cron` and send thenm to MongoDB using the command script `collector_from_file`:

```bash
# export APPDIR="/srv/app"; export INSTANCE="sample"
#     # Get arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument('MONGODB_DATABASE', metavar="MONGODB_DATABASE", type=str, help="MongoDB Database")
#     parser.add_argument('MONGODB_USER', metavar="MONGODB_USER", type=str, help="MongoDB Database SUFFIX")
#     parser.add_argument("FILE_PATTERN", help="FILE_PATTERN: string with file name or file pattern")
#     parser.add_argument('--password', dest='mdb_pwd', help='MongoDB Password', default=None)
#     parser.add_argument('--auth', dest='auth_db', help='Authorization Database', default='auth_db')
#     parser.add_argument('--host', dest='mdb_host', help='MongoDB host (default: %(default)s)',
#                         default='127.0.0.1:27017')
#     parser.add_argument('--confirm', dest='confirmation', help='Skip confirmation step, if True', default="False")
#
# Path to the logs. Leave empty for current directory
# NB! Number of log lines in each file "${LOG_PATH}/${INSTANCE}.*.*.log*" is suggested to be limited with 
#   100 000 lines per 1Gb RAM available
export LOG_PATH="./${INSTANCE}/`date '+%Y/%m/%d'`"
export MONGODB_SERVER=`grep "^MONGODB_SERVER = " ${APPDIR}/${INSTANCE}/collector_module/settings.py | cut -d'=' -f2 | sed -e "s/ //g" | sed -e "s/\"//g"`
# Please note, that PASSWORD is now available in user settings during current session and 
# will be also available in ~/.bash_history. To avoid that, we do not suggest such usage
export PASSWORD=`grep "^MONGODB_PWD = " ${APPDIR}/${INSTANCE}/collector_module/settings.py | cut -d'=' -f2 | sed -e "s/ //g" | sed -e "s/\"//g"`
#
for file in `ls ${LOG_PATH}/${INSTANCE}.*.*.log*` ; do \
    sudo --user collector /usr/bin/python3 ${APPDIR}/${INSTANCE}/collector_module/external_files/collector_from_file.py \
	query_db_${INSTANCE} collector_${INSTANCE} $file \
	--password ${PASSWORD} --auth auth_db --host ${MONGODB_SERVER}:27017 --confirm True ; done
```
