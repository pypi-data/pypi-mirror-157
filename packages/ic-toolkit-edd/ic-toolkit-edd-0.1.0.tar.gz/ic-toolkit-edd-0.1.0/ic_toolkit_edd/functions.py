import os
import platform
import boto3
import botocore
import typer

def read_credentials():
    if os.path.exists(path()):
        credentials_file = open(f"{path()}/.credentials", "r")
        credentials = credentials_file.read().split("\n")
        user_db = credentials[0].replace("userDB:", "")
        password_db = credentials[1].replace("passwordDB:", "")
        host_db = credentials[2].replace("hostDB:", "")
        port_db = credentials[3].replace("portDB:", "")
        name_db = credentials[4].replace("nameDB:", "")
    else:
        return

    return {"userDB": user_db, "passwordDB": password_db, "hostDB": host_db, "portDB": port_db, "nameDB": name_db}

def path():
    if platform.system() == "Windows":
        return f"C:/Users/{os.getlogin()}/.intuitivecare"
    else:
        return f"{os.path.expanduser('~')}/.intuitivecare"