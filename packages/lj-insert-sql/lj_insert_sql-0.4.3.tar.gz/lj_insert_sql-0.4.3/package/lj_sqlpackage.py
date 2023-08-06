import logging

import requests
from sqltool.mysql_client import MySqlClient

import datetime
import logging
import logging.handlers
import os

from package.utils import LICENSE_URL

LOG_FILE = "lj_sqlpackagelog.log"
logging.basicConfig(filename=LOG_FILE,
                    filemode="w",
                    format="[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d, %(funcName)s] %(message)s",
                    level=logging.INFO)
time_hdls = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=7)
logging.getLogger().addHandler(time_hdls)

'''
hex_package_info
'''


class PackageType():
    """
    :param package_type   唯一标识
    :param name         名称
    :param language     语言
    """

    def __init__(self, package_type, name, language):
        self.package_type = package_type
        self.name = name
        self.language = language


class PackageFile():
    def __init__(self, version, file_name, file_type, file_md5, package_id, package_type):
        self.version = version
        self.file_name = file_name
        self.file_type = file_type
        self.file_md5 = file_md5
        self.package_type = package_type


class PackageInfo():
    def __init__(self, package_name, package_type, description, home_page, repository_url, license_key):
        self.package_name = package_name
        self.description = description
        self.home_page = home_page
        self.repository_url = repository_url
        self.package_type = package_type
        self.license_key = license_key


class PackageVersion():
    def __init__(self, package_name, package_type, version, publish_time, license_key):
        self.version = version
        self.publish_time = publish_time
        self.package_name = package_name
        self.license_key = license_key

        self.package_type = package_type


class PackageDeps():
    def __init__(self, package_name, package_type, version, lj_dependency_version_expression=None):
        self.lj_dependency_version_expression = lj_dependency_version_expression
        self.package_name = package_name
        self.package_type = package_type
        self.version = version
        self.requirement = []

    def restructure(self, app, requirement, dependency_type, dependency_version):
        return self.requirement.append({'app': app, 'requirement': requirement, 'dependency_type': dependency_type,
                                        'dependency_version': dependency_version})


class Public():

    def license(self, origin_license):
        verified_license = self.__license_key(document=origin_license) if origin_license else ''
        if not verified_license:
            verified_license = origin_license if not origin_license is None else ''
            if len(verified_license) >= 50 or verified_license.endswith('...'):
                verified_license = ''
            logging.info(f'字段:{["handle_from_field"]} 清洗失败')
            return verified_license
        else:
            return verified_license

    def __license_key(self, document):
        try:
            url = LICENSE_URL
            headers = {
                'Content-Type': 'text/plain'
            }
            res = requests.post(url, data=document, headers=headers)
            print(res.text)
            return res.text
        except:
            return ''


public = Public()


class SqlTool(object):
    def __init__(self, host, port, user, pwd, db, charset):
        self.conn_local = MySqlClient(
            host=host,
            port=port,
            user=user,
            passwd=pwd,
            db=db,
            charset=charset
        )
        self.create_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def package_file(self, file: PackageFile):
        select_file = f"select id from package_file where `file_name`='%s' and `version`='%s'" % (
        file.file_name, file.version)
        file_id = self.conn_local.get_one(select_file)
        info_sql = f"select id from package_info where package_name=%s and package_type=%s"
        info_id = self.conn_local.get_one(info_sql)
        if not info_id:
            info_sqls = f"insert into `package_info`(`package_name`, `package_type`, `license`, `license_key`) values('%s', '%s', '%s', '%s')" % (
                file.file_name, file.package_type, '', ''
            )
            self.conn_local.execute(info_sqls)
        info_sql = f"select id from package_info where package_name=%s and package_type=%s"
        info_id = self.conn_local.get_one(info_sql)

        if file_id:
            sql = f"update `package_file` set version='%s', file_name='%s', file_type='%s', file_md5='%s', package_id=%d, " \
                  f"package_type='%s'  where `file_name`='%s' and `version`='%s'" % (
                      file.version, file.file_name, file.file_type, file.file_md5,
                      info_id['id'], file.package_type, file.file_name, file.version)
            return self.conn_local.execute(sql)
        else:
            sql = f"insert into `package_file`(`version`, `file_name`, `file_type`, `file_md5`, `package_id`, `package_type`" \
                  f") values('%s', '%s', '%s', '%s', %d, '%s')" % (
                  file.version, file.file_name, file.file_type, file.file_md5,
                  info_id['id'], file.package_type)
            return self.conn_local.execute(sql)

    def package_info(self, package: PackageInfo):
        """
                如果存在  更新状态
                :param package:
                :return:
        """

        pack_name = f"select id from package_info where package_name='%s' and package_type='%s'" % (
            package.package_name, package.package_type)
        pack_id = self.conn_local.get_one(pack_name)
        if package.license_key:
            verified_license = public.license(package.license_key)
        else:
            verified_license = ''
        if pack_id:
            update_package = f"update package_info set `package_name`='%s', `description`='%s', `home_page`='%s', " \
                             f"`repository_url`='%s',`license`='%s', `package_type`='%s', `license_key`= '%s' where `package_name`='%s'" % (
                                 package.package_name, package.description, package.home_page, package.repository_url,
                                 verified_license, package.package_type, package.license_key, package.package_name,
                             )
        else:
            return self.conn_local.insert([{'package_name': package.package_name, 'description': package.description,
                                            'home_page': package.home_page, 'repository_url': package.repository_url,
                                            'license': verified_license, 'package_type': package.package_type,
                                            'license_key': package.license_key}],
                                          table_name='package_info',
                                          field_list=['package_name', 'description', 'home_page', 'repository_url',
                                                      'license',
                                                      'package_type', 'license_key'])

    def package_version(self, version: PackageVersion):

        info_sql = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (version.package_name, version.package_type)
        data = self.conn_local.get_one(info_sql)
        select_version = "select id, package_type from `package_version` where package_name= '%s' and package_type='%s' " \
                         "and `version`='%s'" \
                         % (version.package_name, version.package_type, version.version)
        version_id = self.conn_local.get_one(select_version)
        if not data:
            info_sqls = f"insert into `package_info`(`package_name`, `package_type`, `license`, `license_key`) values('%s', '%s', '%s', '%s')" % (
                version.package_name, version.package_type, '', ''
            )
            self.conn_local.execute(info_sqls)

        info_sql = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (version.package_name, version.package_type)
        data = self.conn_local.get_one(info_sql)
        if version.license_key:
            verified_license = public.license(version.license_key)
        else:
            verified_license = ''

        if version_id:
            update_version = f"update package_version set `version` = '%s', `license` = '%s', `publish_time` = '%s'," \
                             f" `package_name` = '%s', `package_id` = %d, `package_type` = '%s',`license_key`= '%s' where " \
                             f"package_id = '%d' and package_type='%s' and version='%s'" % (
                                 version.version, verified_license, version.publish_time, version.package_name,
                                 int(data['id']),
                                 data['package_type'], version.license_key, data['id'], version.package_type,
                                 version.version
                             )
            return self.conn_local.execute(update_version)
        else:
            return self.conn_local.insert([{'version': version.version, 'license': version.license_key, 'publish_time':
                                            version.publish_time, 'package_name': version.package_name, 'package_id':
                                            int(data['id']), 'package_type': data['package_type'], 'license_key':
                                            verified_license}],
                                          table_name='package_version',
                                          field_list=['version', 'license', 'publish_time', 'package_name',
                                                      'package_id', 'package_type', 'license_key'])


    def package_deps(self, deps: PackageDeps):
        if not deps.requirement:
            logging.error("版本表达式不存在，不入库", deps.requirement)
            return

        info_sql = "select id, package_type, package_name from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (deps.package_name, deps.package_type)
        _data = self.conn_local.get_one(info_sql)

        if not _data:
            deps_add_sql = f"insert into `package_info`(`package_name`, `package_type`) values('%s', '%s')" % (
                deps.package_name, deps.package_type
            )
            self.conn_local.execute(deps_add_sql)

        info_sql = "select id, package_type, package_name from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (deps.package_name, deps.package_type)
        _data = self.conn_local.get_one(info_sql)

        args_list = []

        for require in deps.requirement:
            deps_info = "select id, package_type, package_name  from `package_info` where package_name= '%s' and package_type='%s'" \
                        % (require['app'], deps.package_type)
            deps_id = self.conn_local.get_one(deps_info)
            if not deps_id:
                deps_add_sql = f"insert into `package_info`(`package_name`, `package_type`, `license`, `license_key`) values('%s', '%s', '%s', '%s')" % (
                    deps.package_name, deps.package_type, '', ''
                )
                self.conn_local.execute(deps_add_sql)
            deps_info = "select id, package_type, package_name  from `package_info` where package_name= '%s' and package_type='%s'" \
                        % (require['app'], deps.package_type)
            deps_id = self.conn_local.get_one(deps_info)

            deps_sql = f"select id from package_dependencies where  dependency_package_name='%s' and " \
                       f"dependency_package_id=%d" % (
                           deps_id['package_name'], int(deps_id['id'])
                       )  # and dependency_version= '%s', deps_version_id['version']
            dep = self.conn_local.get_one(deps_sql)
            if dep:
                sql = f"update package_dependencies set dependency_version_expression=%s, lj_dependency_version_expression= %s," \
                      f"dependency_version= %s, dependency_type=%s, package_name=%s, package_version= %s, " \
                      f"dependency_package_name= %s, dependency_package_id=%s, package_id=%s, package_type=%s " \
                      f"where package_id=%s and dependency_package_name=%s and dependency_package_id=%s"
                args_list.append((require['requirement'], '',
                                  require['dependency_version'], require['dependency_type'], _data['package_name'],
                                  deps.version, require['app'],
                                  deps_id['id'], _data['id'], _data['package_type'], int(_data['id']),
                                  deps_id['package_name'], int(deps_id['id'])))
                return self.conn_local.executemany(sql, args=args_list, fail_raise=True)
            else :
                # sql = f"insert into package_dependencies(`dependency_version_expression`, " \
                #       f"`lj_dependency_version_expression`, `dependency_version`, `dependency_type`, `package_name`, `package_version`, " \
                #       f"`dependency_package_name`, `dependency_package_id`, `package_id`, " \
                #       f"`package_type`) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # args_list.append((require['requirement'], '',
                #                   require['dependency_version'], require['dependency_type'], _data['package_name'],
                #                   deps.version, require['app'],
                #                   deps_id['id'], _data['id'], _data['package_type']))
                if not require['dependency_version']:
                    require['dependency_version'] = ''
                return self.conn_local.insert(
                    [{'dependency_version_expression': require['requirement'], 'lj_dependency_version_expression':'',
                      'dependency_version': require['dependency_version'], 'dependency_type': require['dependency_type']
                      , 'package_name':  _data['package_name'], 'package_version': deps.version,
                      'dependency_package_name': require['app'], 'dependency_package_id': deps_id['id'], 'package_id':
                          _data['id'], 'package_type': _data['package_type']

                      }],
                    table_name='package_dependencies',
                    field_list=['dependency_version_expression', 'lj_dependency_version_expression',
                                'dependency_version', 'dependency_type','package_name', 'package_version',
                                'dependency_package_name', 'dependency_package_id', 'package_id', 'package_type'])

    def package_Type(self, types: PackageType):
        type_sql = f"select id from package_type where package_type='%s' and name='%s' and `language`='%s'" % (
            types.package_type, types.name, types.language
        )
        type_id = self.conn_local.get_one(type_sql)
        if type_id:
            sql = f"update package_type set package_type='%s', name='%s', `language`='%s', modify_time='%s' where id=%d" % (
                types.package_type, types.name, types.language, self.create_time, int(type_id['id'])
            )
        else:
            sql = "insert into package_type(`package_type`, `name`, `language`) values('%s', '%s', '%s' )" % (
                types.package_type, types.name, types.language
            )
        return self.conn_local.execute(sql)
