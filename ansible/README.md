# X-Road Opmonitor

This ansible playbook configures:
 - A primary (1) - secondary (n) Mongodb cluster.
 - The collector module with a cron job active for every 3 hours (`roles/collector/defaults/main.yml`)
 - The corrector module
 - The analyzer module

The playbook has been tested in GCE using Ubuntu 18.04. Other environments might require modifications to the playbook.

## Prerequisites

* One database server to act as a primary instance
    * No replica set will be configured if only one node is present
* Zero or more database secondary instances
* The server(s) have network access to master ssh port (tcp/22)
* The server(s) have network access to default MongoDB port (default: tcp/5433)

All the servers in a cluster should have the same operating system (Ubuntu 18.04 or RHEL 7).

#### Set up the keys file for MongoDB replication connections

Create a random key file to be used for internal authentication between the database module cluster manager.

1. Generate the key file
```
openssl rand -base64 756 > <path-to-keyfile>
chmod 400 <path-to-keyfile>
```

2. Reference the keyfile path (on the host) inside `vars_file/database.yml`
```
keyfile: <path-to-keyfile>
```

#### Set the database users's password

The databas module configures the all the users and roles needed by the other modules. 
You can set the password inside the file  `roles/database/defaults/main.yml` file of each module.
Change those values to use strong password is highly recommended.

```
# file: roles/database/defaults/main.yml
---
root_pwd: "changeit"
backup_pwd: "changeit"
...
```

## Define the X-Road instance configuration
Update the xroad instance name in `group_vars/all/vars.yml`
```
xroad_instance: EE
xroad_central_server: central-server.example.com
xroad_security_server_url: http://security-server.example.com
xroad_member_class: GOV
xroad_member_code: 10001
xroad_subsystem_code: 10001-1
```

## Running the playbook

Remember to back up the servers before proceeding.

```
ansible-playbook -i hosts/hosts.txt opmonitor_init.yml
```

The playbook does the following operations
* Sets up the database module or a database cluster if more than one database host is present