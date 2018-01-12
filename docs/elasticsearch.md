
| [![Republic of Estonia Information System Authority](img/ria_100_en.png)](https://www.ria.ee/en/) [![X-ROAD](img/xroad_100_en.png)](https://www.ria.ee/en/x-road.html) | ![European Union / European Regional Development Fund / Investing in your future](img/eu_rdf_100_en.png "Documents that are tagged with EU/SF logos must keep the logos until 1.11.2022. If it has not stated otherwise in the documentation. If new documentation is created  using EU/SF resources the logos must be tagged appropriately so that the deadline for logos could be found.") |
| :-------------------------------------------------- | -------------------------: |

# Elasticsearch Setup and Configuration

**NB!** This document status as of January 2018 is as Draft, In progress ...

## Setup

### Install Elasticsearch

Get java from Oracle (8 or newer)

```
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get -y install oracle-java8-installer
java -version
```

Get Elasticsearch

```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.4.0.deb 

sudo dpkg -i elasticsearch-5.4.0.deb

sudo apt-get install -f

sudo update-rc.d elasticsearch defaults
```



## Configuration

### Data and Log files

* configuration files in /etc/elasticsearch
* log files in /var/log/elasticsearch


### Limit Elasticsearch to run localhost

sudo vim /etc/elasticsearch/elasticsearch.yml

```
network.host: localhost
```


## Install Kibana


```
wget https://artifacts.elastic.co/downloads/kibana/kibana-5.4.0-amd64.deb

sudo dpkg -i kibana-5.4.0-amd64.deb

sudo apt-get install -f
```
