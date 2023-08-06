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

def download(prefix, file_name, bucket):
    path = f"./"
    key = prefix + file_name
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket).download_file(key, path + '\\' + file_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            typer.echo(" " + typer.style("ARQUIVO INEXISTENTE NA S3", fg=typer.colors.WHITE, bg=typer.colors.RED))
            return
        else:
            raise
    