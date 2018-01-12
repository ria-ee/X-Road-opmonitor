import logging
import os

appdir = '/srv/app'
# X-Road instances in Estonia: ee-dev, ee-test, EE
x_road_instance = 'sample'

# Anonymizer
anonymizer = {}

anonymizer['field_translations_file'] = 'field_translations.list'
anonymizer['transformers'] = ['default.reduce_request_in_ts_precision', 'default.force_durations_to_integer_range']
anonymizer['threads'] = 1

# MongoDB (anonymizer input) connection parameters
mongo_db = {}

mongo_db['host_address'] = 'opmon'
mongo_db['port'] = 27017
mongo_db['auth_db'] = 'auth_db'
mongo_db['user'] = 'anonymizer_' + x_road_instance
mongo_db['password'] = ''
mongo_db['database_name'] = 'query_db_' + x_road_instance
mongo_db['table_name'] = 'clean_data'

mongo_db['state'] = {
    'database_name': 'anonymizer_state_' + x_road_instance,
    'table_name': 'state'
}

# PostgreSQL connection parameters
postgres = {}

postgres['buffer_size'] = 10000
postgres['host_address'] = 'opmon-opendata'
postgres['port'] = 5432
postgres['database_name'] = 'opendata_' + x_road_instance.lower().replace('-', '_')
postgres['table_name'] = 'logs'
postgres['user'] = 'anonymizer_' + x_road_instance.lower().replace('-', '_')
postgres['readonly_users'] = [
    'interface_' + x_road_instance.lower().replace('-', '_'),
    'networking_' + x_road_instance.lower().replace('-', '_')
]
postgres['password'] = '${PWD_for_anonymizer_x_road_instance}'

# Hiding rules for removing selected entries altogether

hiding_rules = [
    [{'feature': 'clientMemberCode', 'regex': '^(code_1|code_2)$'}],
    [{'feature': 'serviceMemberCode', 'regex': '^(code_1|code_2)$'}]
]

# Substitutions

substitution_rules = [
    {
        'conditions': [
            {'feature': 'clientXRoadInstance', 'regex': '^sample$'},
        ],
        'substitutes': [
            {'feature': 'clientMemberClass', 'value': '#N/A'}
        ]
    },
]

field_data_file = 'field_data.yaml'

# Logging and heartbeat parameters
log = {}

log['path'] = os.path.join('{0}/{1}/logs/'.format(appdir, x_road_instance),
                           'log_opendata-anonymizer_{0}.json'.format(x_road_instance))
log['name'] = 'opendata_module - anonymizer'
log['max_file_size'] = 2 * 1024 * 1024
log['backup_count'] = 10
log['level'] = logging.INFO

heartbeat = {}
heartbeat['dir'] = '{0}/{1}/heartbeat'.format(appdir, x_road_instance)
