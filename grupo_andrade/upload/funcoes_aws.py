import os
import boto3
from flask import flash, redirect, url_for, send_file
from dotenv import load_dotenv
import io

load_dotenv()


s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def enviar_arquivo_s3(file, filename):
    s3_client.upload_fileobj(
        file,
        os.getenv('S3_BUCKET'),
        filename,
        ExtraArgs={
            'ContentType': 'application/pdf',
            'ACL': 'public-read'  # Tornar o arquivo público
        }
    )
    return True

def ver_arquivo(filename):
    try:
        resposta = s3_client.get_object(
            Bucket=os.getenv('S3_BUCKET'),
            Key=filename
        )
        return send_file(
            io.BytesIO(resposta['Body'].read()),
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as erro:
        flash(f'Erro ao visualizar arquivo {str(erro)}')
        return redirect(url_for('placas.homepage'))
