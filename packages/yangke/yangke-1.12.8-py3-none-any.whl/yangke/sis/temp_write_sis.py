import dll_file
import sys
dbp_api = dll_file.DllMode(ip="172.22.191.211", user="admin", passwd_str="admin", port="12085")
if len(sys.argv) == 1:
    print("缺少命令行参数，need cmd parameters")
json_str = sys.argv[1]
tags_values = eval(json_str)
tags = list(tags_values.keys())
values = list(tags_values.values())
dbp_api.write_snapshot_double(tags=tags, values=values)
print("写入SIS成功")