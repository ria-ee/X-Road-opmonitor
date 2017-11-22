
| [![Republic of Estonia Information System Authority](docs/img/ria_100_en.png)](https://www.ria.ee/en/) [![X-ROAD](docs/img/xroad_100_en.png)](https://www.ria.ee/en/x-road.html) | ![European Union / European Regional Development Fund / Investing in your future](docs/img/eu_rdf_100_en.png "Documents that are tagged with EU/SF logos must keep the logos until 1.11.2022. If it has not stated otherwise in the documentation. If new documentation is created  using EU/SF resources the logos must be tagged appropriately so that the deadline for logos could be found.") |
| :-------------------------------------------------- | -------------------------: |

# X-Road v6 monitor project

## Introduction

The project maintains X-Road v6 log of service calls (queries). 
Logs are collected and corrected. 
Further analysis about anomalies (possible incidents) is made. 
Usage reports are created and published. 
Logs are anonymized and published as opendata.

Instructions to install all components, as well as all modules source code, can be found at (ACL-protected):

```
https://stash.ria.ee/projects/XTEE6/repos/monitor/browse 
```

## Installation instructions:

The system architecture is described ==> [here](./docs/system_architecture.md) <==.

## Installing/setting up the Mongo Database (MongoDB)

The first thing that should be done is setting up the MongoDB. Elasticsearch is not currently used. 

Instructions on setting up the MongoDB can be found ==> [here](./docs/database_module.md) <==

## Module installation precedence

The modules should be set up in the following order:
 
1. [Collector](./docs/collector_module.md)
2. [Corrector](./docs/corrector_module.md)
3. [Reports](./docs/reports_module.md)
4. [Opendata](./docs/opendata_module.md)
5. [Analyzer](./docs/analysis_module.md)
6. [Networking](./docs/networking_module.md)

## Programming language

All modules, except Networking that is written in **R**, are written in **Python** and tested with version 3.5.2. Other 3.x versions are likely to be compatible, give or take some 3rd party library interfaces.
