# file = PackageFile(1,2,3,4,5,6)
# sqltoolsa = SqlTool()
# print(sqltoolsa.package_file(file))

# info = PackageInfo(1,2,3,4,5,6)
# sqltoolsa = SqlTool()
# print(sqltoolsa.package_info(info))

# version = PackageVersion('1.2.3','pbce许可','2022-06-27','LOL')
# sqltoolsa = SqlTool()
# print(sqltoolsa.package_version(version))

# dep = {'httpoison': {'app': 'LOL', 'optional': False, 'requirement': '~> 0.9.0'}, 'poison': {'app': 'LOL', 'optional': False, 'requirement': '~> 2.2'}}
# deps = PackageDeps('~> 0.9.0','1', '3', 'LOL', '5', '6', 'LOL',dep)
# sqltoolsa = SqlTool()
# print(sqltoolsa.package_deps(deps))





#
# print(sqltools.insert_type("select * from user"))
# print(sqltools.add_package_version(f"insert into names(name) values('%s')", [['焦长豪1'], ['焦长豪2'], ['焦长豪3']]))
# print(sqltools.insert_info(f"insert into names(name) values('%s')"% '焦长豪'))
# print(sqltools.insert_file(f"-- insert into names(name) values('%s')", ['焦长豪']))
