
import sys
import argparse
import subprocess
import os
import requests
from . import process_code_template
from . import downloader
import json
import shutil
import platform
import stat

class System:
    def __init__(self, **attrs):

        self.attrs = attrs
        for k in attrs:
            setattr(self, k, attrs[k])

    def __getitem__(self, key):
        return self.attrs[key]

    def __iter__(self):
        return iter(self.attrs)

def get_python_link_name(pydll_path, os_name):
    if os_name == "linux":
        for so in os.listdir(pydll_path):
            if so.startswith("libpython") and not so.endswith(".so") and so.find(".so") != -1:
                basename = os.path.basename(so[3:so.find(".so")])
                full_path = os.path.join(pydll_path, so)
                return basename, full_path
    return None, None

def python_version_lite():
    import sys
    return ".".join(sys.version.split(".")[:2])

def get_system():

    os_name = platform.system().lower()
    python_version = python_version_lite()
    kiwi_root = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    cpp_packages_root = os.path.join(kiwi_root, "cpp-packages")
    pydll_path = os.path.join(sys.exec_prefix, "lib")
    pydll_link_name, pydll_full_path = get_python_link_name(pydll_path, os_name)

    return System(
        KIWIURL_ROOT = "http://zifuture.com:1556/fs/{key}",
        KIWI_ROOT = kiwi_root,
        KIWIPKG_ROOT = cpp_packages_root,
        PYTHON_VERSION = python_version,
        PYTHON_LINK_NAME = pydll_link_name,
        PYTHON_INCLUDE = f"{sys.exec_prefix}/include/{pydll_link_name}",
        PYTHON_LIB_DIR = f"{pydll_path}",
        CACHE_ROOT = os.path.expanduser('~/.cache/kiwi')
    )

def set_exec_permission(directory, print_info=False):
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)

        # and os.path.splitext(full_path)[1] == ""
        if os.path.isfile(full_path):
            if print_info:
                print(f"Set execute permission: {full_path}")

            os.chmod(full_path, stat.S_IRWXU)


def create_symlink_directory(directory, print_info=False):

    files = os.listdir(directory)
    for file in files:
        if file.startswith("lib") and file.find(".so") != -1 and not file.endswith(".so"):
            source = os.path.join(directory, file)
            link_name = file[:file.find(".so")] + ".so"
            if link_name.find("-") != -1:
                p = link_name.find("-")
                e = link_name.find(".", p)
                if e != -1:
                    link_name = link_name[:p] + link_name[e:]
            link_path = os.path.join(directory, link_name)

            if os.path.exists(link_path):
                os.remove(link_path)

            if print_info:
                print(f"Create symlink {link_path}")
            os.symlink(os.path.abspath(source), os.path.abspath(link_path))


def set_permission_and_symlink_directory(directory, print_info=False):

    basename = os.path.basename(directory).lower()

    if basename == "bin":
        set_exec_permission(directory, print_info)
    elif basename in ["lib", "lib64", "lib32", "so"]:
        create_symlink_directory(directory, print_info)

    for d, ds, fs in os.walk(directory):
        for itemd in ds:
            item_lower_name = itemd.lower()
            if item_lower_name == "bin":
                set_exec_permission(os.path.join(d, itemd), print_info)
            elif item_lower_name in ["lib", "lib64", "lib32", "so"]:
                create_symlink_directory(os.path.join(d, itemd), print_info)


def get_variable_template():
    variable_template = []
    for k in system:
        variable_template.append([k, system[k]])

    keyfile = downloader.get_cache_path("config.txt")
    if os.path.exists(keyfile):
        with open(keyfile, "r") as f:
            configs = json.loads(f.read())
        
        for k in configs:
            variable_template.append([k, configs[k]])

    return variable_template

system = get_system()
downloader.system = system

def do_info(args):

    print("Variables: ")
    for key, value in get_variable_template():
        print(f"  {key} = {value}")
    return 0

def do_local_cpp_pkg(args):
    files = []
    if os.path.exists(system.KIWIPKG_ROOT):
        files = os.listdir(system.KIWIPKG_ROOT)

    found_package = []
    for file in files:
        path = os.path.join(system.KIWIPKG_ROOT, file)
        if os.path.isdir(path):
            found_package.append([file, path])

    print(f"Found {len(found_package)} local cpp-packges")
    for i, (name, path) in enumerate(found_package):
        print(f"{i+1}. {name}          directory: {path}")
    return 0


def install_package(name, save_to, verbose=True):

    url = f"{system.KIWIURL_ROOT}/cpp-packages/{name}.zip"
    file = os.path.join(system.CACHE_ROOT, "cpp-packages", f"{name}.zip")
    ok, md5 = downloader.download_and_verify_md5_saveto_file(url, file)
    if not ok:
        print(f"Failed to fetch cpp package {name}")
        return 1

    package_root = os.path.join(save_to, name)
    if os.path.isdir(package_root):
        print(f"Remove old package files {package_root}")
        import shutil
        shutil.rmtree(package_root)

    print(f"Extract package {name} to {package_root}")
    downloader.extract_zip_to(file, save_to, verbose)

    set_permission_and_symlink_directory(package_root, verbose)
    print(f"Install {name} to {save_to}, Success!")
    return 0


def install_from_pkg_name(name, save_to):

    if save_to is not None:
        save_to = save_to.strip()

    if save_to is None or len(save_to) == 0:
        save_to = system.KIWIPKG_ROOT
    return install_package(name, save_to, verbose=True)


def install_from_requirement(file):
    
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip().replace("\r", "").replace("\n", "")

    lines = [line for line in lines if len(line) > 0]
    for line in lines:
        if line[0] == "#":
            continue

        code = 1
        name = ""
        save_to = system.KIWIPKG_ROOT

        p = line.find(";")
        if p == -1:
            name = line
        else:
            name = line[:p].strip()
            save_to = line[p+1:].strip()
            if len(save_to) == 0:
                save_to = system.KIWIPKG_ROOT
            elif save_to[0] == "@":
                if len(save_to) > 1:
                    var_name = save_to[1:]
                    if var_name not in system.attrs:
                        print(f"Can not find variable [{var_name}] in requiresment")
                        code = 1
                        break
                    save_to = system[var_name]

        code = install_package(name, save_to, verbose=False)
        if code != 0:
            break

    if code != 0:
        print("Failed to install from requiresment")
    return code


def do_get_cpp_pkg(args):

    if os.path.isfile(args.name):
        install_from_requirement(args.name)
    else:
        install_from_pkg_name(args.name, args.save)


def do_get_data(args):

    save_to = "."
    if args.save is not None and len(args.save.strip()) > 0:
        save_to = args.save.strip()

    name = args.name
    url = f"{system.KIWIURL_ROOT}/datas/{name}.zip"
    file = os.path.join(system.CACHE_ROOT, "datas", f"{name}.zip")
    ok, md5 = downloader.download_and_verify_md5_saveto_file(url, file)
    if not ok:
        print(f"Failed to fetch data {name}")
        return 1

    package_root = os.path.join(save_to, name)
    print(f"Extract package {name} to {package_root}")
    downloader.extract_zip_to(file, save_to, True)
    return 0


def get_inv_variable_template():
    variable_template = get_variable_template()
    for i in range(len(variable_template)):
        if variable_template[i][0] == "PYTHON_VERSION":
            del variable_template[i]
            break

    variable_template = sorted(variable_template, key=lambda x:len(x[1]), reverse=True)
    return variable_template

def do_get_templ(args):
    if args.saveto is None:
        args.saveto = args.template

    if os.path.isdir(args.saveto):
        while True:
            opt = input(f"{args.saveto} has exists, overwrite? (Y=yes, N=no): default [Y]:").lower()
            if opt == "": opt = "y"
            if opt != "y" and opt != "n":
                continue
                
            if opt == "n":
                print("Operation cancel.")
                return 0
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return 1

    url = f"{system.KIWIURL_ROOT}/code_template/{args.template}.zip"
    cache_zip = os.path.join(system.CACHE_ROOT, "code_template", f"{args.template}.zip")
    if not args.download and os.path.exists(cache_zip):
        print(f"Use cache {cache_zip}")
    elif not downloader.download_to_file(url, cache_zip):
        print(f"Template '{args.template}' not found")
        return 1

    print(f"Extract to {args.saveto} . ")
    namelist = downloader.extract_zip_to(cache_zip, args.saveto)

    if not args.raw:
        print("Replace project variable")
        variable_template = get_variable_template()
        process_code_template.process_code_template(args.saveto, namelist, variable_template)

    print("Done!")
    return 0

def remove_tree_keep_father(path):
    files = os.listdir(path)
    for file in files:
        full_path = os.path.join(path, file)
        print(f"Delete {full_path}")
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

def extract_series_templ(meta, saveto, raw, download):

    series_name = meta["name"]
    current_index = meta["current-index"]
    templ_list = meta["list-templ"]
    select_item = templ_list[current_index]
    item_name = select_item[0].strip()
    if item_name == "" or item_name == "." or item_name == ".." or item_name.find("/") != -1:
        print(f"Invalid series templ name [{item_name}]")
        return 1

    templ_name = f"{series_name}-{item_name}"
    templ_url = f"{system.KIWIURL_ROOT}/code_template/{templ_name}.zip"
    templ_cache_local_zip = os.path.join(system.CACHE_ROOT, "code_template", f"{templ_name}.zip")
    if not download and os.path.exists(templ_cache_local_zip):
        print(f"Use cache {templ_cache_local_zip}")
    elif not downloader.download_to_file(templ_url, templ_cache_local_zip):
        print(f"Template '{templ_name}' not found")
        return 1

    if os.path.isdir(saveto):
        print(f"Remove old files")
        remove_tree_keep_father(saveto)

    print(f"Extract to {saveto} . ")
    namelist = downloader.extract_zip_to(templ_cache_local_zip, saveto)

    if not raw:
        print("Replace project variable")
        variable_template = get_variable_template()
        process_code_template.process_code_template(saveto, namelist, variable_template)

    series_directory = os.path.join(saveto, ".series")
    os.makedirs(series_directory, exist_ok=True)
    local_config_json = os.path.join(series_directory, "config.json")

    print(f"Save to {local_config_json}")
    json.dump(meta, open(local_config_json, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
    print(f"Done! current template is {templ_name}, {select_item[1]}")
    return 0

def do_get_series_single(args):
    if args.saveto is None:
        args.saveto = args.name

    if os.path.isdir(args.saveto):
        while True:
            opt = input(f"{args.saveto} has exists, overwrite? (Y=yes, N=no): default [Y]:").lower()
            if opt == "": opt = "y"
            if opt != "y" and opt != "n":
                continue
                
            if opt == "n":
                print("Operation cancel.")
                return 0
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return 1

    meta_url = f"{system.KIWIURL_ROOT}/code_template/{args.name}.series.json"
    meta_cache_local_file = os.path.join(system.CACHE_ROOT, "code_template", f"{args.name}.series.json")
    if not args.download and os.path.exists(meta_cache_local_file):
        print(f"Use cache {meta_cache_local_file}")
    elif not downloader.download_to_file(meta_url, meta_cache_local_file):
        print(f"Series '{args.name}' not found")
        return 1

    meta = json.load(open(meta_cache_local_file, "r", encoding="utf-8"))
    templ_list = meta["list-templ"]

    current_index = 0
    meta["current-index"] = current_index
    if len(templ_list) == 0:
        print(f"Series list-templ is empty")
        return 0

    return extract_series_templ(meta, args.saveto, args.raw, args.download)

def do_get_series_all(args):
    if args.saveto is None:
        args.saveto = args.name

    if os.path.isdir(args.saveto):
        while True:
            opt = input(f"{args.saveto} has exists, overwrite? (Y=yes, N=no): default [Y]:").lower()
            if opt == "": opt = "y"
            if opt != "y" and opt != "n":
                continue
                
            if opt == "n":
                print("Operation cancel.")
                return 0
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return 1

    meta_url = f"{system.KIWIURL_ROOT}/code_template/{args.name}.series.json"
    meta_cache_local_file = os.path.join(system.CACHE_ROOT, "code_template", f"{args.name}.series.json")
    if not args.download and os.path.exists(meta_cache_local_file):
        print(f"Use cache {meta_cache_local_file}")
    elif not downloader.download_to_file(meta_url, meta_cache_local_file):
        print(f"Series '{args.name}' not found")
        return 1

    meta = json.load(open(meta_cache_local_file, "r", encoding="utf-8"))
    templ_list = meta["list-templ"]

    if len(templ_list) == 0:
        print(f"Series list-templ is empty")
        return 1

    for index, (templ_name, templ_descript) in enumerate(templ_list):
        new_save_to = f"{args.saveto}/{templ_name}"
        current_index = 0
        meta["current-index"] = index
        success = extract_series_templ(meta, new_save_to, args.raw, args.download, args.cuda, args.trt)
        if success != 0:
            print(f"Download {templ_name} failed")
            return 1
    return 0

def do_get_series_system(args):
    if args.all:
        do_get_series_all(args)
    else:
        do_get_series_single(args)

def do_change_proj(args):

    current_dir = os.path.abspath(".")
    config_json_file = os.path.join(current_dir, ".series", "config.json")
    if not os.path.isfile(config_json_file):
        print(f"Current is not series folder")
        return 1

    meta = json.load(open(config_json_file, "r", encoding="utf-8"))
    current_index = meta["current-index"]
    templ_list = meta["list-templ"]
    if len(templ_list) == 0:
        print(f"list templ is empty")
        return 1

    if args.index in ["next", "prev"]:
        if args.index == "next":
            current_index = max(0, current_index)
            current_index = (current_index + 1) % len(templ_list)
        elif args.index == "prev":
            current_index = max(0, current_index)
            current_index = (current_index - 1 + len(templ_list)) % len(templ_list)
        
        meta["current-index"] = current_index
        return extract_series_templ(meta, current_dir, args.raw, args.download, args.cuda, args.trt)

    index_names_map = []
    for index, (templ_name, templ_descript) in enumerate(templ_list):
        p = templ_name.find("-")
        if p != -1:
            names = [templ_name[:p], templ_name[p+1:]]
        else:
            names = [templ_name]    
        
        names = [name for name in names if name.strip() != ""]
        index_names_map.append([index, names, templ_descript])

    if args.index != "":
        for index, names, templ_descript in index_names_map:
            if args.index in names:
                meta["current-index"] = index
                return extract_series_templ(meta, current_dir, args.raw, args.download, args.cuda, args.trt)
    
    print(f"List templ: ")
    for index, names, templ_descript in index_names_map:
        if len(names) > 0:
            if len(names) == 1:
                print(names[0])
            else:
                chapter = names[0]
                caption = names[1]
                print(f"chapter: {chapter}, caption: {caption}, description: {templ_descript}")
        
    if args.index != "":
        print(f"Unknow index [{args.index}]")
    return 0


def do_templ_list(args):

    url = f"{system.KIWIURL_ROOT}/code_template/list.txt"
    url = downloader.process_url_with_key(url)
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]

    print(f"Found {len(list_info)} items:")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0


def do_templ_search(args):
    url = f"{system.KIWIURL_ROOT}/code_template/list.txt"
    url = downloader.process_url_with_key(url)
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]
    pattern = args.pattern
    def pattern_match(pattern, value : str):
        array = pattern.lower().split("%")
        value = value.lower()
        if len(array) == 0: return False
        i = 0
        p = 0
        while i < len(array):
            item = array[i]
            p = value.find(item, p)
            if p == -1: return False
            p += len(item)
            i += 1
        return True

    list_info = [item for item in list_info if pattern_match(pattern, item[0])]

    if len(list_info) == 0:
        print(f"Not found any items match for '{pattern}'")
        return 1

    print(f"Found {len(list_info)} items for '{pattern}':")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0

def do_series_detail(args):
    
    if args.name == "" or args.name == ".":
        print_current = True
        current_dir = os.path.abspath(".")
        config_json_file = os.path.join(current_dir, ".series", "config.json")
        if not os.path.isfile(config_json_file):
            print(f"Current is not series folder")
            return 1
    else:
        print_current = False
        meta_url = f"{system.KIWIURL_ROOT}/code_template/{args.name}.series.json"
        meta_cache_local_file = os.path.join(system.CACHE_ROOT, "code_template", f"{args.name}.series.json")
        if not args.download and os.path.exists(meta_cache_local_file):
            print(f"Use cache {meta_cache_local_file}")
        elif not downloader.download_to_file(meta_url, meta_cache_local_file):
            print(f"Series '{args.name}' not found")
            return 1
        config_json_file = meta_cache_local_file

    meta = json.load(open(config_json_file, "r", encoding="utf-8"))
    current_index = meta["current-index"]
    templ_list = meta["list-templ"]
        
    index_names_map = []
    for index, (templ_name, templ_descript) in enumerate(templ_list):
        p = templ_name.find("-")
        if p != -1:
            names = [templ_name[:p], templ_name[p+1:]]
        else:
            names = [templ_name]    
        
        names = [name for name in names if name.strip() != ""]
        index_names_map.append([index, names, templ_descript])

    print(f"List templ: ")
    for index, names, templ_descript in index_names_map:
        if len(names) > 0:
            if len(names) == 1:
                print(names[0])
            else:
                chapter = names[0]
                caption = names[1]
                print(f"chapter: {chapter}, caption: {caption}, description: {templ_descript}")

    if print_current:
        current_item = templ_list[current_index]
        print(f"Current is {current_item[0]}, {current_item[1]}")
    return 0

def do_series_list(args):

    url = f"{system.KIWIURL_ROOT}/code_template/list.series.txt"
    url = downloader.process_url_with_key(url)
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch series list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]

    print(f"Found {len(list_info)} items:")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0

def do_series_search(args):
    url = f"{system.KIWIURL_ROOT}/code_template/list.series.txt"
    url = downloader.process_url_with_key(url)
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch series list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]
    pattern = args.pattern
    def pattern_match(pattern, value : str):
        array = pattern.lower().split("%")
        value = value.lower()
        if len(array) == 0: return False
        i = 0
        p = 0
        while i < len(array):
            item = array[i]
            p = value.find(item, p)
            if p == -1: return False
            p += len(item)
            i += 1
        return True

    list_info = [item for item in list_info if pattern_match(pattern, item[0])]

    if len(list_info) == 0:
        print(f"Not found any items match for '{pattern}'")
        return 1

    print(f"Found {len(list_info)} items for '{pattern}':")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0

def do_prep_vars(args):
    file_or_directory = args.file_or_directory
    if not os.path.exists(file_or_directory):
        print(f"No such file or directory, {file_or_directory}")
        return 1

    files = []
    if os.path.isdir(file_or_directory):
        for d, ds, fs in os.walk(file_or_directory):
            files.extend([os.path.join(d, f) for f in fs])
    else:
        files.append(file_or_directory)

    print("Replace project variable")
    variable_template = get_variable_template()
    process_code_template.process_code_template(None, files, variable_template)
    print("Done!")
    return 0

def do_invert_variable(args):

    file_or_directory = args.file_or_directory
    if not os.path.exists(file_or_directory):
        print(f"No such file or directory, {file_or_directory}")
        return 1

    files = []
    if os.path.isdir(file_or_directory):
        for d, ds, fs in os.walk(file_or_directory):
            files.extend([os.path.join(d, f) for f in fs])
    else:
        files.append(file_or_directory)

    print("Replace project value to variable")
    variable_template = get_inv_variable_template()
    process_code_template.process_code_template(None, files, variable_template, process_code_template.inv_filter_content)
    print("Done!")
    return 0

def do_set_key(args):

    keyfile = downloader.get_cache_path("key.txt")
    os.makedirs(os.path.dirname(keyfile), exist_ok=True)

    with open(keyfile, "w", encoding="utf-8") as f:
        f.write(args.key)

    print(f"Done, key is [{args.key}], file is [{keyfile}]")
    return 0

def do_config(args):

    keyfile = downloader.get_cache_path("config.txt")
    os.makedirs(os.path.dirname(keyfile), exist_ok=True)

    config_dict = {}
    if os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            config_dict = json.loads(f.read())

    if args.value is not None:
        args.value = args.value.strip()

    if args.value is None or args.value == "":
        print("Value is empty.")
        return 1

    config_dict[args.name] = args.value
    with open(keyfile, "w", encoding="utf-8") as f:
        f.write(json.dumps(config_dict, ensure_ascii=False, indent=4))

    print(f"Done, key: [{args.name}], value: [{args.value}], save to: [{keyfile}]")
    return 0

def do_delete_config(args):

    keyfile = downloader.get_cache_path("config.txt")
    os.makedirs(os.path.dirname(keyfile), exist_ok=True)

    config_dict = {}
    if os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            config_dict = json.loads(f.read())

    if args.name not in config_dict:
        print(f"Can not find key [{args.name}] in config")
        return 1
        
    del config_dict[args.name]
    with open(keyfile, "w", encoding="utf-8") as f:
        f.write(json.dumps(config_dict, ensure_ascii=False, indent=4))

    print(f"Done, key: [{args.name}], Save to: [{keyfile}]")
    return 0

if __name__ == "__main__":

    def new_parser_with_version(name, help):
        global subp
        p = subp.add_parser(name, help=help)
        return p

    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(dest="cmd")
    p = new_parser_with_version("info", help="display support list")
    
    subp.add_parser("list-templ", help="display all code template")
    p = subp.add_parser("search-templ", help="search all code template")
    p.add_argument("pattern", type=str, help="search name, yolo* etc.")

    p = new_parser_with_version("get-templ", help="fetch code template")
    p.add_argument("template", type=str, help="template name: tensorrt-mnist cuda-sample")
    p.add_argument("saveto", type=str, help="save to directory, default[template name]", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    subp.add_parser("list-series", help="display all series template")
    p = subp.add_parser("search-series", help="search all series template")
    p.add_argument("pattern", type=str, help="search name, yolo* etc.")

    p = subp.add_parser("set-key", help="configure authkey")
    p.add_argument("key", type=str, help="auth key")

    p = new_parser_with_version("get-series", help="fetch series template")
    p.add_argument("name", type=str, help="series name")
    p.add_argument("saveto", type=str, help="save to directory, default[template name]", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")
    p.add_argument("--all", action="store_true", help="download all template")

    p = new_parser_with_version("change-proj", help="change series proj")
    p.add_argument("index", type=str, default="", help="series proj index, 1.1/cuinit", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    p = subp.add_parser("series-detail", help="change series proj")
    p.add_argument("name", type=str, default="", help="series name", nargs="?")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    p = new_parser_with_version("prep-vars", help="replace local file variables")
    p.add_argument("file_or_directory", type=str, help=f"Project directory or file, file filter = {process_code_template.include_list}")

    p = new_parser_with_version("inv-vars", help="replace local file value invert to variables")
    p.add_argument("file_or_directory", type=str, help=f"Project directory or file, file filter = {process_code_template.include_list}")

    subp.add_parser("list-pkg", help="display all installed local cpp package")
    p = subp.add_parser("config", help="config custom variable")
    p.add_argument("name", type=str, help="variable name")
    p.add_argument("value", type=str, help="variable value")

    p = subp.add_parser("delete-config", help="delete config custom variable")
    p.add_argument("name", type=str, help="variable name")

    p = subp.add_parser("install", help="install cpp package")
    p.add_argument("name", type=str, help="package name")
    p.add_argument("--save", type=str, help="save to directory, default is KIWIPKG_ROOT")

    p = subp.add_parser("get-data", help="get data")
    p.add_argument("name", type=str, help="data name")
    p.add_argument("--save", type=str, help="save to directory, default is current directory")
    args = parser.parse_args()

    cmd_funcs = {
        "info":          do_info,
        "get-templ":     do_get_templ,
        "list-templ":    do_templ_list,
        "search-templ":  do_templ_search,
        "install":       do_get_cpp_pkg,
        "get-data":      do_get_data,
        "list-pkg":      do_local_cpp_pkg,
        "prep-vars":     do_prep_vars,
        "inv-vars":      do_invert_variable,
        "get-series":    do_get_series_system,
        "list-series":   do_series_list,
        "search-series": do_series_search,
        "change-proj":   do_change_proj,
        "series-detail": do_series_detail,
        "set-key":       do_set_key,
        "config":        do_config,
        "delete-config": do_delete_config
    }

    if args.cmd in cmd_funcs:
        sys.exit(cmd_funcs[args.cmd](args))

    parser.print_help()