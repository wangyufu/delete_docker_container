# coding=utf-8
import StringIO
import datetime
import json
import subprocess

# 查看本机是否有僵尸进程

# docker ps -a --format "table {{.ID}},{{.CreatedAt}}" --filter 'exited=0'

res = subprocess.Popen("docker ps -a --format 'table {{.ID}}' --filter 'exited=0'",
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
err = res.stderr.read()
if err:
    print 'Failed to check the container list'
else:
    back_msg = res.stdout.read()

delete_days_ago = 7
text = StringIO.StringIO(back_msg)
docker_list = []
delete_container = []

while True:
    s = text.readline()
    if s == '':
        break
    elif s == 'CONTAINER ID\n':
        continue
    tmp = s.split(',')
    # print tmp
    docker_list.append(s.strip())

# print docker_list


for row in docker_list:
    res = subprocess.Popen("docker inspect %s" % row,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    err = res.stderr.read()
    if err:
        print 'inspect %s container failure' % row
        continue
    else:
        container_msg = res.stdout.read()
        container_msg_json_obj = json.loads(container_msg)
        FinishedAt = container_msg_json_obj[0]['State']['FinishedAt'][0:10]
        time_obj = FinishedAt.split('-')
        finished_datetime = datetime.datetime(
            int(time_obj[0]),
            int(time_obj[1]),
            int(time_obj[2]),
        )
        not_running_time = datetime.datetime.now() - finished_datetime
        if len(str(not_running_time).split(',')) == 2:
            if int(str(not_running_time).split()[0]) > delete_days_ago:
                delete_container.append(row)

# print delete_container

res_end = subprocess.Popen("docker rm %s" % ' '.join(delete_container),
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
err_end = res.stderr.read()
if err_end:
    back_msg_end = err
else:
    back_msg_end = 0

print back_msg_end
