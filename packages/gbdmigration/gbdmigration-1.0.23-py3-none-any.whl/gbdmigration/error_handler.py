import os
from gbdmigration.filescanner import FileScanner
from datetime import datetime


def error_file_cleaner(path):
    for col in os.listdir(path):
        if os.path.isdir(os.path.join(path, col)):
            for f in os.listdir(os.path.join(path, col)):
                p = os.path.join(path, col, f)
                new_lines = []
                if '.zip' in f:
                    continue
                print("Processing %s" % p)
                with open(p, 'r') as i:
                    lines = i.readlines()
                    for line in lines:
                        if 'Incomplete Document Info' in line:
                            continue
                        if 'Bypass' in line:
                            continue
                        if 'Do Not Use' in line:
                            continue
                        if 'File should not be imported' in line:
                            continue
                        if 'Do not Import' in line:
                            continue
                        if 'Icon image missing' in line:
                            continue
                        if 'Data can be only JSON or XML' in line:
                            continue
                        new_lines.append(line.replace('\n', ''))
                if new_lines:
                    with open(p, 'w') as i:
                        i.write('\n'.join(new_lines))
                else:
                    os.remove(p)


def respanshooter(path, path_collection, output):
    for col in os.listdir(path):
        if os.path.isdir(os.path.join(path, col)):
            respanshooter_col(path, col, path_collection, output)


def respanshooter_col(path, col, path_collection, output):
    snapshot_name = 'errors_snapshot.%s.%s' % (
        datetime.now().strftime('%Y%m%d.%H%M'), col
    )
    snapshot_path = os.path.join(output, col)
    os.makedirs(snapshot_path, exist_ok=True)
    snapshot_path = os.path.join(snapshot_path, snapshot_name)
    s_data = {}
    for fi in os.listdir(os.path.join(path, col)):
        print("Processing file %s of %s" % (fi, col))
        p = os.path.join(path, col, fi)
        with open(p, 'r') as i:
            lines = i.readlines()
            for line in lines:
                if line[0] in [' ', '\t']:
                    continue
                if ' - ' not in line:
                    continue
                appunm = line.split(' - ')[0]
                f = FileScanner(col, path_collection, appunm)
                s_data.update(f.get_raw_files())
    if s_data:
        FileScanner._to_csv(snapshot_path, s_data)
