import logging

from sqltool.mysql_client import MySqlClient

import datetime
import logging
import logging.handlers
import os

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


class PackageFile():
    def __init__(self, version, file_name, file_type, file_md5, package_id, package_type):
        self.version = version
        self.file_name = file_name
        self.file_type = file_type
        self.file_md5 = file_md5
        self.package_id = package_id
        self.package_type = package_type


class PackageInfo():
    def __init__(self, package_name, package_type, description, home_page, repository_url, license):
        self.package_name = package_name
        self.description = description
        self.home_page = home_page
        self.repository_url = repository_url
        self.license = license
        self.package_type = package_type

class PackageVersion():
    def __init__(self, package_name, package_type, version, license, publish_time, license_key):
        self.version = version
        self.license = license
        self.publish_time = publish_time
        self.package_name = package_name
        self.license_key = license_key

        self.package_type = package_type


class PackageDeps():
    def __init__(self, package_name, package_type, lj_dependency_version_expression, dependency_type):
        self.lj_dependency_version_expression = lj_dependency_version_expression
        self.dependency_type = dependency_type
        self.package_name = package_name
        self.package_type = package_type
        self.requirement = []

    def restructure(self, app, requirement):
        return self.requirement.append({'app':app, 'requirement': requirement})


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
        select_file = f"select id from package_file where `file_name`='%s' and `version`='%s'" % (file.file_name, file.version)
        file_id = self.conn_local.get_one(select_file)
        if file_id:
            sql = f"update `package_file` set version='%s', file_name='%s', file_type='%s', file_md5='%s', package_id=%d, " \
                  f"package_type='%s'  where `file_name`='%s' and `version`='%s'" % (
                      file.version, file.file_name, file.file_type, file.file_md5,
                      file.package_id, file.package_type, file.file_name, file.version)
            return self.conn_local.execute(sql)
        else:
            sql = f"insert into `package_file`(`version`, `file_name`, `file_type`, `file_md5`, `package_id`, `package_type`" \
                  f") values('%s', '%s', '%s', '%s', %d, '%s')"%(file.version, file.file_name, file.file_type, file.file_md5,
                                                            file.package_id, file.package_type)
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
        if pack_id:
            update_package = f"update package_info set `package_name`='%s', `description`='%s', `home_page`='%s', " \
                             f"`repository_url`='%s',`license`='%s', `package_type`='%s' where `package_name`='%s'" % (
                                 package.package_name, package.description, package.home_page, package.repository_url,
                                 package.license, package.package_type, package.package_name,
                             )
            return self.conn_local.execute(update_package)
        else:
            sql = f"insert into `package_info`(`package_name`, `description` ,`home_page` ,`repository_url` ," \
                  "`license` ,`package_type`) values('%s', '%s', '%s', '%s', '%s', '%s')" \
                  % (package.package_name, package.description, package.home_page, package.repository_url,
                     package.license, package.package_type)
            return self.conn_local.execute(sql)

    def package_version(self, version: PackageVersion):
        info_sql = "select id, package_type from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (version.package_name, version.package_type)
        data = self.conn_local.get_one(info_sql)
        select_version = "select id, package_type from `package_version` where package_name= '%s' and package_type='%s'" \
                         % (version.package_name, version.package_type)
        version_id = self.conn_local.get_one(select_version)
        if data:
            if version_id:
                update_version = f"update package_version set `version` = '%s', `license` = '%s', `publish_time` = '%s'," \
                                 f" `package_name` = '%s', `package_id` = %d, `package_type` = '%s',license_key= '%s' where " \
                                 f"package_name = '%s' and package_type='%s'" % (
                                     version.version, version.license, version.publish_time, version.package_name,
                                     int(data['id']),
                                     data['package_type'], version.package_name, version.package_type, version.license_key
                                 )
                return self.conn_local.execute(update_version)
            else:
                sql = "insert into `package_version`(`version`, `license`, `publish_time`, `package_name`, " \
                      "`package_id`, `package_type`, 'license_key') values" "('%s', '%s', '%s', '%s', %d, '%s', '%s')" % \
                      (version.version, version.license, version.publish_time,
                       version.package_name, int(data['id']), data['package_type'], version.license_key)
                return self.conn_local.execute(sql)
        else:
            logging.info("查询info信息不存在，", select_version)

    def package_deps(self, deps: PackageDeps):
        info_sql = "select id, package_type, package_name from `package_info` where package_name= '%s' and package_type='%s'" \
                   % (deps.package_name, deps.package_type)
        _data = self.conn_local.get_one(info_sql)
        version_sql = "select id, package_type, version from `package_version` where package_name= '%s' and package_type='%s'" \
                      % (deps.package_name, deps.package_type)
        version_id = self.conn_local.get_one(version_sql)
        if not _data or not version_id:
            logging.error("查询信息不存在", info_sql, version_sql)
            return

        if not deps.requirement:
            logging.error("版本表达式不存在，不入库", deps.requirement)
            return
        args_list = []

        for require in deps.requirement:
            deps_info = "select id, package_type, package_name  from `package_info` where package_name= '%s' and package_type='%s'" \
                        % (require['app'], deps.package_type)
            deps_id = self.conn_local.get_one(deps_info)
            deps_version = "select id, version from `package_version` where package_name= '%s' and package_type='%s' order by publish_time desc" \
                           % (require['app'], deps.package_type)
            deps_version_id = self.conn_local.get_one(deps_version)
            if not deps_id and not deps_version_id:
                logging.error("没有依赖的包以及版本", deps.requirement)
                return
            deps_sql = f"select id from package_dependencies where dependency_package_name='%s'"%(
                deps_id['package_name']
            ) # and dependency_version= '%s', deps_version_id['version']
            dep = self.conn_local.get_one(deps_sql)
            if dep:
                sql = f"update package_dependencies set dependency_version_expression=%s, lj_dependency_version_expression= %s," \
                      f"dependency_version= %s, dependency_type=%s, package_name=%s, package_version= %s, " \
                      f"dependency_package_name= %s, dependency_package_id=%s, package_id=%s, package_type=%s " \
                      f"where dependency_package_name=%s"
                args_list.append((require['requirement'], '',
                                  '', deps.dependency_type, _data['package_name'],
                                  version_id['version'], require['app'],
                                  deps_id['id'], _data['id'], _data['package_type'], deps_id['package_name']))
            else:
                sql = f"insert into package_dependencies(`dependency_version_expression`, " \
                  f"`lj_dependency_version_expression`, `dependency_version`, `dependency_type`, `package_name`, `package_version`, " \
                  f"`dependency_package_name`, `dependency_package_id`, `package_id`, " \
                  f"`package_type`) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                args_list.append((require['requirement'], '',
                                  '', deps.dependency_type, _data['package_name'],
                                  version_id['version'], require['app'],
                                  deps_id['id'], _data['id'], _data['package_type']))
        return self.conn_local.executemany(sql, args=args_list, fail_raise=True)


