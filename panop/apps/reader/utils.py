from __future__ import print_function

try:
    from ConfigParser import NoSectionError
except ImportError:
    from configparser import NoSectionError

import jaydebeapi
from py4j.protocol import Py4JJavaError
import pysftp

from django.conf import settings
from django.shortcuts import get_object_or_404

from panop.apps.reader.models import TestRun
import panop.apps.reader.tasks

SETTINGS_DICT = {'informix': {'package': 'com.informix.jdbc.IfxDriver', 'jar': settings.INFORMIX_JAR_PATH},
                 'mysql': {'package': 'com.mysql.jdbc.Driver', 'jar': settings.MYSQL_JAR_PATH},
                 'sqlserver': {'package': 'com.microsoft.sqlserver.jdbc.SQLServerDriver', 'jar': settings.SQLSERVER_JAR_PATH}}

SFTP_UNPROCESSED = "Unprocessed"
SFTP_PROCESSED = "Processed"
SFTP_MISSING = "Missing"


def get_jdbc_cursor(config, component='campaign table'):
    db_type = config.get(component, 'type')
    db_conn = jaydebeapi.connect(SETTINGS_DICT[db_type]['package'],
                                 [
                                     config.get(component, 'host'),
                                     config.get(component, 'user'),
                                     config.get(component, 'password'),
                                 ],
                                 SETTINGS_DICT[db_type]['jar'])

    return db_conn.cursor()


def campaign_central_row_check(test_run, row_number):
    write_log = panop.apps.reader.tasks.write_log
    try:
        config = test_run.campaign.get_config()
        cursor = get_jdbc_cursor(config)
        campaign_table = config.get("campaign table", "table")
        cursor.execute("select * from {0}".format(campaign_table))
    except Py4JJavaError as e:
        print(e)
        print(e.args)
        write_log.delay(test_run.pk, 'campaign central', '(ERROR) Connection failed - {0}'.format(e.args))
        return "Connection failed"
    campaign_table_headers = [x[0] for x in cursor.description]
    polled_data = cursor.fetchall()
    print(campaign_table_headers)
    print(polled_data)

    if len(polled_data) == 0:
        write_log.delay(test_run.pk, 'campaign central', 'Table empty')
        return "Table empty"
    else:
        try:
            rows = test_run.get_data_file_rows(expanded=True, limited=True)
            row = rows[row_number]
            monitor_column = config.get("campaign table", "monitor")
            sql_query = "select {0} from {1} where {2}".format(monitor_column, campaign_table, row_to_where_clause(row))
            print(sql_query)
            cursor.execute(sql_query)
            filtered_data = cursor.fetchall()
            if len(filtered_data) == 0:
                write_log.delay(test_run.pk, 'campaign central', '[{0}|{1}] No matching row'.format(row_number, row))
                return "No matching row"
            write_log.delay(test_run.pk, 'campaign central', '[{0}|{1}] {2}: {3}'.format(row_number,
                                                                                         row,
                                                                                         monitor_column,
                                                                                         filtered_data))
            return "{0}: {1}".format(monitor_column, filtered_data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            write_log.delay(test_run.pk, 'campaign central', '(ERROR) Query failed - {0}'.format(e.args))
            return "Query failed"


def loader_table_query(test_run):
    config = test_run.campaign.get_config()
    # filename = config.get("sftp", "filename")
    try:
        cursor = get_jdbc_cursor(config)
        cursor.execute('select * from campaign_load_batch ORDER BY load_start DESC LIMIT 6')
    except Py4JJavaError:
        return ["Connection failed", ], []
    load_check = cursor.fetchall()
    load_check_headers = [x[0] for x in cursor.description]
    return load_check_headers, load_check


def row_to_where_clause(row):
    print("ROW TO WHERE: " + repr(row))
    return " AND ".join(["{0}='{1}'".format(column.strip().lower(), value.strip()) for column, value in row.items()])


def sftp_query(test_id):
    write_log = panop.apps.reader.tasks.write_log
    test_run = get_object_or_404(TestRun, pk=test_id)
    config = test_run.campaign.get_config()
    try:
        destination_host = config.get('sftp', 'host')
        username = config.get('sftp', 'user')
        password = config.get('sftp', 'password')
        destination_directory = config.get('sftp', 'target')
        filename = config.get('sftp', 'filename')
    except NoSectionError:
        return "N/A"
    with pysftp.Connection(destination_host, username=username, password=password) as sftp:
        try:
            with sftp.cd(destination_directory):
                if filename in sftp.listdir():
                    status = "Unprocessed"
                elif any([f.startswith("WICDONE_" + filename) for f in sftp.listdir()]):
                    status = "Processed"
                else:
                    status = "Missing"
        except IOError:
            status = "Directory missing"
    write_log.delay(test_run.pk, 'sftp', status)
    return status
