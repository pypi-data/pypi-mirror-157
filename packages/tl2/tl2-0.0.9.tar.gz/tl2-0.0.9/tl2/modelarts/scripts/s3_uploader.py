# encoding: utf-8
# Author: Tao yuheng(t50018193).
import logging
import os
import sys
import copy
import base64
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import request
import json
import time
import queue
import threading
import platform
from xml.dom.minidom import parseString as parseXmlString
from xml import etree
from xml.etree.ElementTree import ElementTree
from collections import defaultdict

import requests


os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

logging.basicConfig(level=logging.ERROR, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

endpoint = "http://roma.huawei.com"
api = "/csb/rest/s3/bucket/endpoint"

parser = argparse.ArgumentParser(description='Parameters of CSB-OBS',
                                 formatter_class=
                                 argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--show_speed", action='store_true',
                    help="To display the current upload speed, <psutil> is required")
parser.add_argument("--bucket_path", type=str, required=True,
                    help="The default value of bucket path")
parser.add_argument('--region', type=str, required=True,
                    help='region of bucket.')
parser.add_argument('--bucket_name', type=str, required=True,
                    help='Please input you bucket_name.')
parser.add_argument('--app_token', type=str, required=True,
                    help='appToken of CSB.')
parser.add_argument('--local_folder_absolute_path', type=str, required=True,
                    help='local_folder_absolute_path')
parser.add_argument('--buffer_size', type=int, default=65536,
                    help='The default value of buffer_size is 65536.')
parser.add_argument("--retry_times", type=int, default=3,
                    help='The default value of retry times.')
parser.add_argument('--big_file', type=int, default=100*1024*1024,
                    help='The default value of big file is 100M.')
parser.add_argument('--thread_num', type=int, default=12,
                    help='The default value of thread.')
parser.add_argument("--package_size", type=int, default=50*1024*1024,
                    help='The default value of package is 50M.')
parser.add_argument('--vendor', type=str, default="HEC",
                    help='vendor of bucket.')
parser.add_argument("--fail_json_storage_path", type=str, default="./fail.json",
                    help="The default value of fail.json storage path")
result, _ = parser.parse_known_args()
args = copy.deepcopy(result)

cond = threading.Condition()

print_lock = threading.Lock()
file_lock = threading.Lock()
upload_queue = queue.Queue()
big_file_upload_queue = queue.Queue()
range_queue = queue.Queue()
big_file_ls = []
file_count = 0
uploaded_count = 0
big_file_process_count = 0
big_file_process_total = 0
error_count = 0

current_speed = ""
start_count_speed = True

session = requests.Session()

is_file = False

if os.path.isfile(args.local_folder_absolute_path):
    is_file = True


args.local_folder_absolute_path = args.local_folder_absolute_path.replace("\\", "/")
args.father_path_name = args.local_folder_absolute_path[args.local_folder_absolute_path.rfind("/")+1:]

retry_map = defaultdict(int)
error_map = dict()


# 1. get endpoint
def get_file_server_endpoint():
    try:
        url = endpoint + api
        param = "?" + "bucketid=" + args.bucket_name + "&token=" \
                + args.app_token + "&vendor=" + args.vendor + "&region=" + args.region
        req = request.Request(url=url + param)
        res = request.urlopen(req)
        result = res.read().decode(encoding='utf-8')
        result_dict = json.loads(result)
        if result_dict["success"]:
            return result_dict["result"]
        else:
            raise Exception(result_dict["msg"])
    except Exception as e:
        import traceback
        traceback.print_exc()


# 1. bucket_auth
def bucket_auth():
    bucket_auth_endpoint = args.csb_file_server + '/rest/boto3/s3/bucket-auth?vendor=' + args.vendor + '&region=' + args.region + '&bucketid=' + args.bucket_name + '&apptoken=' + args.app_token
    req = request.Request(url=bucket_auth_endpoint)
    res = request.urlopen(req)
    result = res.read().decode(encoding='utf-8')
    result_dict = json.loads(result)
    if not result_dict["success"]:
        raise Exception(result_dict["msg"])


def human_size(size, dot=3):
    return str(round(size / pow(1024, 3), dot)) + ' GB'


def do_upload_queue():
    if not is_file:
        for (rootDir, dirNames, filenames) in os.walk(args.local_folder_absolute_path):
            for filename in filenames:
                local_object_name = os.path.join(rootDir, filename).replace("\\", "/")
                size = os.path.getsize(local_object_name)
                object_name = args.bucket_path + args.father_path_name +  local_object_name.replace(args.local_folder_absolute_path, "").replace("\\", "/")
                upload_content = {
                    "local_object_name": local_object_name,
                    "object_name": object_name,
                    "size": size
                }
                if size > args.big_file:
                    big_file_upload_queue.put(upload_content)
                else:
                    upload_queue.put(upload_content)
    else:
        file_name = args.local_folder_absolute_path[args.local_folder_absolute_path.rfind("/")+1:]
        object_name = args.bucket_path + file_name
        size = os.path.getsize(args.local_folder_absolute_path)
        upload_content = {
            "local_object_name": args.local_folder_absolute_path,
            "object_name": object_name,
            "size": size
        }
        if size > args.big_file:
            big_file_upload_queue.put(upload_content)
        else:
            upload_queue.put(upload_content)


# _ get-object
def put_object(upload_content: dict):
    global error_count

    local_object_name = upload_content["local_object_name"]
    object_name = upload_content["object_name"]

    b64_object_name = base64.urlsafe_b64encode(object_name.encode()).decode()
    path = f"/rest/boto3/s3/{args.vendor}/{args.region}/{args.app_token}/{args.bucket_name}/{b64_object_name}"

    try:
        headers = {
            "Content-Type": "application/json",
            "csb-token": args.app_token,
            'Connection': 'close'
        }

        with open(local_object_name, "rb") as f:
            session.put(args.csb_file_server+path, data=f.read(), headers=headers)

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_count += 1
        put_object(upload_content)


# 3.1 do_get
def do_put():
    global file_count
    global uploaded_count
    global start_count_speed
    while upload_queue.qsize() > 0:
        try:
            upload_content = upload_queue.get(timeout=3)
        except Exception:
            break

        try:
            put_object(upload_content)
            uploaded_count += 1
            with print_lock:
                print("\r", end="")
                print("Upload progress: {}/{} - {}%: ".format(uploaded_count, file_count,
                                                                int((uploaded_count / file_count) * 100)),
                      "▋" * (int(uploaded_count / file_count * 50)) + current_speed, end="")
                sys.stdout.flush()
        except Exception:
            import traceback
            traceback.print_exc()
            retry_map[str(upload_content)] += 1

            if retry_map[str(upload_content)] > args.retry_times:
                # log
                print(f"{upload_content} try {args.retry_times} times failed")
                retry_map[str(upload_content)] = traceback.format_exc()
                continue
            upload_queue.put(upload_content)
    start_count_speed = False


def print_split():
    print("\n\n--------------------------\n")


def check_retry():
    global error_count
    print(f"error_count =  {error_count}")
    if error_map:
        with open(args.fail_json_storage_path, "w", encoding="utf-8") as f:
            json.dump(error_map, f)
        print(f"{len(error_map)} files upload failed, written in {args.fail_json_storage_path}")
    else:
        print("all files upload completed!")
    if "Windows" in platform.platform():
        set_display_required(False)


def check_platform():
    if "Windows" in platform.platform():
        print("检测到使用Windows系统，在Windows系统下，该脚本会阻止系统休眠，以确保上传能够完成。", end='')
        set_display_required(True)
        print_split()


def set_display_required(continuous: bool):
    import ctypes
    ES_CON = 0x80000000
    ES_DIS = 0x00000002
    if continuous:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_DIS | ES_CON)
    else:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_DIS)


def create_range_upload_task(object_name):
    object_key = base64.urlsafe_b64encode(object_name.encode(encoding="utf-8"))
    object_key = str(object_key, encoding="utf-8")
    path = f"/rest/boto3/s3/{args.vendor}/{args.region}/{args.app_token}/{args.bucket_name}/{object_key}?uploads=uploads"
    headers = {
        "Content-Type": "text/plain"
    }
    resp = session.post(args.csb_file_server + path, headers=headers)
    result_dict = parseXmlString(resp.content.decode(encoding="utf-8"))
    upload_id = result_dict.getElementsByTagName("UploadId")[0].childNodes[0].data

    return upload_id, object_key


def range_put(tag_list, object_name, upload_id, h_size, file_io):
    global big_file_process_count
    global start_count_speed
    object_key = base64.urlsafe_b64encode(object_name.encode(encoding="utf-8"))
    object_key = str(object_key, encoding="utf-8")
    headers = {
        "Content-Type": "text/plain",
        "Connection": "keep-alive"
    }

    while range_queue.qsize() > 0:
        range_content = range_queue.get()
        start = range_content[0]
        end = range_content[1]
        part_number = range_content[2]
        path = f"/rest/boto3/s3/{args.vendor}/{args.region}/{args.app_token}/{args.bucket_name}/{object_key}?" \
               f"partNumber={part_number}&uploadId={upload_id}"
        try:
            with file_lock:
                file_io.seek(start)
                # 这里一定要记得加 1
                resp = session.put(args.csb_file_server + path, data=file_io.read(end-start+1), headers=headers)
            if resp.status_code != 200:
                print(resp.text)
                raise Exception("Upload failed")
            tag_content = {
                "part_number": str(part_number),
                "etag": resp.headers["ETag"]
            }
            tag_list.append(tag_content)
            big_file_process_count += 1
            with print_lock:
                if big_file_process_count > big_file_process_total:
                    big_file_process_count = big_file_process_total
                print("\r", end="")
                print("Uploading <{}> size: {}: {}/{} - {}%: ".format(object_name, h_size,
                                                                      big_file_process_count, big_file_process_total,
                                                                int((big_file_process_count / big_file_process_total) * 100)),
                      "▋" * (int(big_file_process_count / big_file_process_total * 50)) + current_speed, end="")
                sys.stdout.flush()
        except Exception:
            import traceback
            traceback.print_exc()
            key = object_name + "@" + str(range_content)
            retry_map[key] += 1

            if retry_map[key] > args.retry_times:
                logging.error(f"{key} try {args.retry_times} times failed")
                error_map[key] = traceback.format_exc()
                continue
            range_queue.put(range_content)
            range_put(tag_list, object_name, upload_id, h_size, file_io)
    start_count_speed = False


def merge_range_put(tag_list, object_key, upload_id):
    global error_count
    path = f"/rest/boto3/s3/{args.vendor}/{args.region}/{args.app_token}/{args.bucket_name}/{object_key}?" \
           f"uploadId={upload_id}"
    headers = {
        "Content-Type": "text/plain"
    }
    data = parse2xml(tag_list)
    resp = session.post(args.csb_file_server + path, headers=headers, data=data)

    if resp.status_code != 200:
        try:
            request_id = resp.headers["RequestId"]
        except Exception:
            request_id = "request_id is None"
        error_count += 1
        error_map[request_id + "@" + object_key] = str(resp.headers)


def parse2xml(tag_list: list):
    root = etree.ElementTree.Element("CompleteMultipartUpload")

    for tag in tag_list:
        part = etree.ElementTree.SubElement(root, "Part")
        part_number = etree.ElementTree.SubElement(part, "PartNumber")
        part_number.text = tag["part_number"]
        etag = etree.ElementTree.SubElement(part, "ETag")
        etag.text = tag["etag"]

    return etree.ElementTree.tostring(root)


def do_range_put(pool: ThreadPoolExecutor):
    global big_file_process_count
    global big_file_process_total
    global start_count_speed
    while big_file_upload_queue.qsize() > 0:
        big_file_process_count = 0
        upload_content = big_file_upload_queue.get()
        local_object_name = upload_content["local_object_name"]
        object_name = upload_content["object_name"]
        total_size = upload_content["size"]
        # 动态调节包的大小，防止文件过大（超过500G） 段超过10000
        if total_size > args.package_size * 9500:
            real_package_size = total_size // 9500
        else:
            real_package_size = args.package_size
        range_list = [[i if i == 0 else i + 1, i + real_package_size]
                      for i in range(0, total_size + 1, real_package_size)]
        index = 1
        if range_list[-1][0] > total_size:
            del range_list[-1]
        if range_list[-1][1] > total_size:
            range_list[-1][1] = total_size
        for r in range_list:
            r.append(index)
            index += 1
        big_file_process_total = len(range_list)

        for r in range_list:
            range_queue.put(r)

        upload_id, object_key = create_range_upload_task(object_name)
        file_io = open(local_object_name, "rb")
        tag_list = []
        start_count_speed = True
        thread_count_current_speed = pool.submit(get_delta)
        ls_thread = [pool.submit(range_put, tag_list, object_name, upload_id, human_size(total_size), file_io)
                     for _ in range(args.thread_num)]
        ls_thread.append(thread_count_current_speed)
        for task in as_completed(ls_thread):
            try:
                task.result()
            except Exception as e:
                raise e
        file_io.close()
        merge_range_put(tag_list, object_key, upload_id)
        print_split()


def multi_thread_main():
    global file_count

    sys.stdout.write('begin uploading small file ...\n')
    args.csb_file_server = get_file_server_endpoint()
    bucket_auth()
    full_thread_num = args.thread_num + 4
    do_upload_queue()
    file_count = upload_queue.qsize()  # 上传文件总数
    pool = ThreadPoolExecutor(max_workers=full_thread_num, thread_name_prefix="Python Uploader")

    ls_thread = []
    thread_count_current_speed = pool.submit(get_delta)
    ls_thread.append(thread_count_current_speed)
    for i in range(args.thread_num):
        ls_thread.append(pool.submit(do_put))
    tic = time.time()
    for thread in ls_thread:
        thread.result()

    for task in as_completed(ls_thread):
        try:
            task.result()
        except Exception as e:
            raise e

    toc = time.time()
    seconds = toc - tic
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print("\nsmall file upload completed, cost time : {:0>d} h {:0>2d} m {:0>2d} s".format(int(h), int(m), int(s)))

    sys.stdout.write(f'begin uploading {big_file_upload_queue.qsize()} big files ...\n')

    tic = time.time()
    do_range_put(pool)
    toc = time.time()
    seconds = toc - tic
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print("big file upload completed, cost time : {:0>d} h {:0>2d} m {:0>2d} s".format(int(h), int(m), int(s)))


def get_delta():
    if args.show_speed:
        import psutil
        global current_speed
        while start_count_speed:
            before = psutil.net_io_counters().bytes_sent
            time.sleep(1)
            now = psutil.net_io_counters().bytes_sent
            delta = (now-before) / (1024 * 1024 * 1)
            current_speed = "  {:.3f} MB/s".format(delta)


if __name__ == '__main__':
    r"""
    pip install requests psutil
    
    python -m tl2.modelarts.scripts.s3_uploader --local_folder_absolute_path=C:\Users\z50017127\code\tl2_lib --bucket_path=ZhouPeng/codes/ --app_token=0482fc70-f97c-49f4-878e-2eee5fe788e3 --region=cn-north-4 --bucket_name=bucket-3690 --show_speed   
                    
    """
    # print('test')
    check_platform()
    multi_thread_main()
    check_retry()




