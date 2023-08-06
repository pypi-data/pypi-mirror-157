import typer
import os
import hashlib
import boto3
import botocore
from ic_multitool_fluxodedados.functions import path
from ic_multitool_fluxodedados.database import executa_query

app = typer.Typer()

@app.command()
def test():
    print(path())
@app.command()
def config(
    user_db: str = typer.Option(..., prompt=True),
    password_db: str = typer.Option(..., prompt=True),
    host_db: str = typer.Option(..., prompt=True),
    port_db: int = typer.Option(..., prompt=True),
    name_db: str = typer.Option(..., prompt=True)):
    if not os.path.exists(path()):
        os.mkdir(path())
    with open(f"{path()}/.credentials", 'w') as credentials:
        credentials.write(f"userDB:{user_db}\npasswordDB:{password_db}\nhostDB:{host_db}\nportDB:{port_db}\nnameDB:{name_db}")

@app.command()
def downpadr(id_arq: str):
    query = f"select * from upload.pipeline where id_arquivo_padronizado in ({id_arq})"
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
                    typer.echo(" " + typer.style("ARQUIVO INEXISTENTE NA S3", fg=typer.colors.WHITE, bg=typer.colors.RED))
                    return
                else:
                    return
        typer.echo(typer.style(" SUCESSO", fg=typer.colors.GREEN, bold=True))

@app.command()
def downpars(id_arq: str):
    query = f"select * from upload.pipeline where id_arquivo_parseado in ({id_arq})"
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
                    typer.echo(" " + typer.style("ARQUIVO INEXISTENTE NA S3", fg=typer.colors.WHITE, bg=typer.colors.RED))
                    return
                else:
                    return
        typer.echo(typer.style(" SUCESSO", fg=typer.colors.GREEN, bold=True))

@app.command()
def downorig(id_arq: str):
    query = f"select * from upload.pipeline where id_arquivo_original in ({id_arq})"
    result = executa_query(query)
    with typer.progressbar(range(len(result)), length=len(result)) as progress:
        for i in progress:
            prefix = result['orig_caminho_s3'][i]
            file_name = result['orig_nome_arquivo'][i]
            bucket = result['orig_s3_bucket'][i]
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
                    return
        typer.echo(typer.style(" SUCESSO", fg=typer.colors.GREEN, bold=True))

@app.command()
def gethash():
    md5_list = []
    filename_list = [f for f in os.listdir('./') if os.path.isfile(f)]
    for file in filename_list:
        with open(file,"rb") as f:
            bytes = f.read()
            readable_hash = hashlib.md5(bytes).hexdigest()
            md5_list.append(f'"{readable_hash}"')
    md5_hashs = ','.join(str(md5) for md5 in md5_list)
    with open(f"{path()}/md5_query.txt", 'w') as txt:
        txt.write(f'select * from upload.pipeline p where orig_ic_hash in ({md5_hashs});')
    typer.launch(f"{path()}/md5_query.txt", locate=False)

@app.command()
def upload():
    filename_list = [f for f in os.listdir('./upload') if os.path.isfile(f)]
    with typer.progressbar(range(len(filename_list)), length=len(filename_list)) as progress:
        for i in progress:
            prefix = "Original/Plataforma/Upload/Old/pdf/"
            file_name = filename_list[i]
            bucket = 'ic-filerepo-nvus'
            key = prefix + file_name
            s3 = boto3.resource('s3')
            try:
                s3.meta.client.upload_file(key, bucket, file_name)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    typer.echo(" " + typer.style("ARQUIVO INEXISTENTE NA S3", fg=typer.colors.WHITE, bg=typer.colors.RED))
                    return
                else:
                    return
        typer.echo(typer.style(" SUCESSO", fg=typer.colors.GREEN, bold=True))