import pandas as pd
import pymysql
import typer
import os
import boto3
import botocore
import platform
from marceloapd_ic_toolkit.functions import read_credentials


app = typer.Typer()

try:
    credentials = read_credentials()
except:
    pass

@app.command()
def config(
    user_db: str = typer.Option(..., prompt=True),
    password_db: str = typer.Option(..., prompt=True),
    host_db: str = typer.Option(..., prompt=True),
    port_db: int = typer.Option(..., prompt=True),
    name_db: str = typer.Option(..., prompt=True)):
    if platform.system() == "Windows":
        if not os.path.exists(f"C:/Users/{os.getlogin()}/.intuitivecare"):
            os.mkdir(f"C:/Users/{os.getlogin()}/.intuitivecare")
        with open(f"C:/Users/{os.getlogin()}/.intuitivecare/.credentials", 'w') as credentials:
            credentials.write(f"userDB:{user_db}\npasswordDB:{password_db}\nhostDB:{host_db}\nportDB:{port_db}\nnameDB:{name_db}")
    else:
        if not os.path.exists(f"{os.path.expanduser('~')}/.intuitivecare"):
            os.makedirs(f"{os.path.expanduser('~')}/.intuitivecare")
        with open(f"{os.path.expanduser('~')}/.intuitivecare/.credentials", 'w') as credentials:
            credentials.write(f"userDB:{user_db}\npasswordDB:{password_db}\nhostDB:{host_db}\nportDB:{port_db}\nnameDB:{name_db}")

@app.command()
def downpadr(id_arq: str):
    query = f"select * from upload.pipeline where id_arquivo in ({id_arq})"
    result = executa_query(query)
    with typer.progressbar(range(len(result)), length=len(result)) as progress:
        for i in progress:
            prefix = result['padr_caminho_s3'][i]
            file_name = result['padr_nome_arquivo'][i]
            bucket = result['padr_s3_bucket'][i]
            path = f"./"
            key = prefix + file_name
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(bucket).download_file(key, path + '\\' + file_name)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    typer.echo(typer.style("ERRO", fg=typer.colors.WHITE, bg=typer.colors.RED))
                else:
                    raise
        typer.echo(typer.style("\tSUCESSO", fg=typer.colors.GREEN, bold=True))

@app.command()
def downpars(id_arq: str):
    query = f"select * from upload.pipeline where id_arquivo in ({id_arq})"
    result = executa_query(query)
    with typer.progressbar(range(len(result)), length=len(result)) as progress:
        for i in progress:
            prefix = result['pars_caminho_s3'][i]
            file_name = result['pars_nome_arquivo'][i]
            bucket = result['pars_s3_bucket'][i]
            path = f"./"
            key = prefix + file_name
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(bucket).download_file(key, path + '\\' + file_name)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    typer.echo(typer.style("ERRO", fg=typer.colors.WHITE, bg=typer.colors.RED))
                else:
                    raise
        typer.echo(typer.style("\tSUCESSO", fg=typer.colors.GREEN, bold=True))

def executa_query(query):
    try:
        connection = pymysql.connect(user=credentials['userDB'],
                                     password=credentials['passwordDB'],
                                     host=credentials['hostDB'],
                                     port=int(credentials['portDB']),
                                     db=credentials['nameDB'],
                                     connect_timeout=5,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     local_infile=True)
    except Exception as e:
        print(f'Erro ao criar conexao {e}')

    with connection.cursor() as cur:
        cur.execute(query)
        df_results = pd.DataFrame(cur.fetchall())
    connection.close()
    return df_results