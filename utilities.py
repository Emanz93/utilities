from datetime import datetime, timezone
import difflib
import json
import os
import shutil
import tarfile

""" Library of some useful functions. """


def str_date_to_unix(str_date):
    """ Takes string datetime in a specific format and returns unix time.
    e.g.: 2021-03-22T17:18:03Z -> 1616429883
    Parameter:
        str_date: String. Datetime.
    Returns:
        timestamp: int. Unix timestamp.
    """
    return int(datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%SZ').timestamp())


def unix_to_date_str(unix_time, locale='UTC'):
    """ Takes an integer timestamp and returns a string with a specific format in UTC.
    e.g.: 2021-03-22T17:18:03Z -> 1616429883
    Parameters:
        unix_time: Int. Timestamp.
        locale: string. Default UTC. Else will use the local timezone. 
    Returns:
        datetime: String. Datetime.
    """
    if locale=='UTC':
        return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        return datetime.fromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    

def get_system_time_unix(locale='UTC'):
    """ Get the system time and convert it in unix time.
    Parameter:
        locale: string. Default UTC. Else will use the local timezone. 
    Returns:
        timestamp: int. Unix timestamp.
    """
    if locale=='UTC':
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()
    return int(now.timestamp())
    

def get_system_time_string(locale='UTC'):
    """ Takes the system time and return it in a string datetime.
    e.g.: 2021-03-22T17:18:03Z
    Parameter:
        locale: string. Default UTC. Else will use the local timezone.
    Returns:
        datetime: String. Datetime.
    """
    if locale=='UTC':
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')


def extract_tgz(filename, out_directory):
    """ Extract a tar gz file in a specific directory.
    Parameter:
        filename: String. Path of the input file.
        out_directory: String. Path of the output directory.
    """
    tar = tarfile.open(filename, "r:gz")
    tar.extractall(path=out_directory)
    tar.close()


def create_tgz(source_folder, destination_folder, tgz_filename):
    """ Compress the source_folder into a tar.gz archive called tgz_filename.
    Move the archive in destination_folder.

    Parameters:
        source_folder: String. Abosulute path of the source folder that needs to be compressed.
        destination_folder: String. Abosulute path of the destination folder of the tgz_filename.
        tgz_filename: String. Name of the tgz file.
    Returns:
        tgz_path: String. Absolute path of the compressed file.
    """
    # check the filename
    if tgz_filename.endswith('.tgz'):
        tgz_filename = tgz_filename.replace('.tgz', '.tar.gz')

    # check the existance of the destination_folder
    if not os.path.isdir(destination_folder):
        create_folder(destination_folder) # create folder(s) if it doesn't exist

    # chekc if the output file exists
    tgz_path = os.path.join(destination_folder, tgz_filename)
    if os.path.isfile(tgz_path):
        os.unlink(tgz_path) # delete if exists

    # compress the source_folder
    with tarfile.open(tgz_path, "w:gz", format=tarfile.GNU_FORMAT) as tar_fd:
        for root, dirs, files in os.walk(source_folder):
            for name in files: # compress the files
                fullname = os.path.join(root, name)
                tar_fd.add(fullname, arcname=fullname.split("\\", 1)[1])
                for name in dirs: # recursevly compress the folders
                    fullname = os.path.join(root, name)
                    tar.add(fullname, arcname=fullname.split("\\", 1)[1], recursive=False)
    return tgz_path


def create_zip(source_folder, destination_folder, zip_filename):
    """ Creating the ZIP file.
    Parameters:
        input_folder: String. Path of the source folder to be compressed.
        output_filename: String. Name of the zip file. Without the .zip ending. This is automatically added by zip library.
        zip_filename: String. Name of the zip file.
    Returns:
        zip_path: String. Absolute path of the compressed file.
    """
    # check the existance of the destination_folder
    if not os.path.isdir(destination_folder):
        create_folder(destination_folder) # create folder(s) if it doesn't exist

    # chekc if the output file exists
    zip_path = os.path.join(destination_folder, zip_filename)
    if os.path.isfile(zip_path):
        os.unlink(zip_path) # delete if exists

    # check the filename
    if zip_filename.endswith('.zip'):
        zip_filename = zip_filename.replace('.zip', '')

    # compress the source_folder
    tmp_path = shutil.make_archive(zip_filename, 'zip', source_folder)
    shutil.move(tmp_path, destination_folder)
    return os.path.join(destination_folder, zip_filename + '.zip')


def create_folder(dir_path):
    """ Make a directory or multiple directories if they don't exist.
    If the folder already exists, then remove it and create a clean one.
    Parameters:
        dir_path: String. RELATIVE Path of the directory.
    """
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path)


def _read_files(filename1, filename2):
    """ Read the two files and returs two lists containing their lines without trailing newline character.
    Parameters:
        filename1: String. First file filename.
        filename2: String. Second file filename.
    Returns:
        lines1: List. List of lines.
        lines2: List. List of lines.
    """
    # read the files
    with open(filename1, 'r') as f1:
        lines1 = f1.readlines()

    for i in range(len(lines1)):
        lines1[i] = lines1[i].strip()

    with open(filename2, 'r') as f2:
        lines2 = f2.readlines()

    for i in range(len(lines2)):
        lines2[i] = lines2[i].strip()

    return lines1, lines2


def compare_two_files_differ(new_filename, old_filename):
    """ Compare two ascii files and generate a list of lines wit the differences.
    Parameters:
        new_filename: path of the new version of the file.
        old_filename: path of the old version of the file.
    """
    lines1, lines2 = _read_files(new_filename, old_filename)
    d = difflib.Differ()
    cmp_lines = list(d.compare(lines2, lines1))

    go = False
    for line in cmp_lines:
        if line.startswith("- ") or line.startswith("+ "):
            go = True
            break
    if go:
        return cmp_lines
    else:
        return []


def read_json(json_path):
    """ Read a json file.
    Parameters:
        json_path: String. Path of the json file.
    Returns:
        d: dict. Content of the file.
    """
    with open(json_path, 'r') as f:
        d = json.load(f)
    return d


def write_json(json_path, d):
    """Write a dictionary in a json file.
    Parameters:
        json_path: String. Path of the json file.
        d: dict.
    """
    with open(json_path, 'w') as f:
        json.dump(d, f, indent=2, sort_keys=True)


def is_hex(value):
    """Check if the value is expressed in hex.
    Parameter:
        value: String. Value to be checked.
    Returns:
        True: if value is expressed in HEX.
        False: Otherwise.
    """
    if isinstance(value, str):  # test if input is a string.
        try:
            if isinstance(int(value, 16), int):
                return True
        except ValueError:
            return False


def hex_to_bin(value):
    """Retuns the string representation of the binary value from the hexadecimal input value. i.e. 'd5' -> '11010101'
    Parameter:
        value: String. Value to be converted.
    Returns:
        String. Converted value.
    """
    return bin(int(value, 16))[2:]


def dec_to_hex(value):
    """ Convert the input integer to hexadecimal string. 
    Parameters:
        value: integer. Value to be converted.
    Returns:
        String. Converted value.
    """
    return hex(16)[2:]


def dec_to_bin(value):
    """Retuns the string representation of the binary value from the decimal input value. i.e. 15 -> '1111'
    Parameter:
        value: String. Value to be converted.
    Returns:
        String. Converted value.
        """
    return bin(int(value))[2:]


def bin_to_hex(value):
    """Retuns the string representation of the hexadecimal value from the binary input value. i.e. '1101' -> 'd'
    Parameter:
        value: String. Value to be converted.
    Returns:
        String. Converted value.
    """
    return hex(int(value, 2))[2:]


def bin_to_dec(value):
    """Retuns the integer value from a binary string representation as input value. i.e. '1001' -> 9
    Parameter:
        value: String. Value to be converted.
    Returns:
        Integer. Converted value.
    """
    return int(value, 2)
