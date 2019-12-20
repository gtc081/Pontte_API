# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 16:47:55 2019

@author: crgab
"""
# app.py

import os
import json

import boto3

from flask import Flask, request
app = Flask(__name__)

TABELA_CONTRATOS = os.environ['TABELA_CONTRATOS']
TABELA_CRIACAO   = os.environ['TABELA_CRIACAO']
TABELA_UPLOAD    = os.environ['TABELA_UPLOAD']
BUCKET           = 'NOME DO BUCKET A SER ALTERADO' 
client           = boto3.client('dynamodb')
dynamodb         = boto3.resource('dynamodb')
s3               = boto3.resource('s3')

from functions.Functions import Functions
from functions.Html import Html


@app.route("/")
def inicio():
    """
    Função inicial da API
    
    Retorno
    -------

    bemvindo
        String com a mensagem de boas-vindas
    """
    bemvindo = """BEM-VINDO À API DA PONTTE, PARA CONTRATOS DE EMPRÉSTIMOS!<br><br>
                  Digite <i>/docs</i> ao final da URL para ver a documentação!<br><br>
                  Digite <i>/contratos</i> ao final da URL para ver a lista de contratos existentes!"""

    return bemvindo

@app.route("/contratos")
def get_all_contracts():
    """
    Função que traz todos os contratos em uma tabela
    
    Retorno
    -------

    tabela
        String o HTML da tabela com os contratos
    """
    response = client.scan(
        TableName=TABELA_CONTRATOS
    )
    items = response['Items']

    tabela = Html().table(items)

    return tabela

@app.route("/contrato/<string:id_contrato>")
def get_contract(id_contrato,String=None):
    """
    Função que traz as informações principais sobre o contrato
    
    Parâmetros
        ----------
        
    id_contrato: string, obrigatório
        ID do contrato buscado
        
    String: bool
        Booleano que define a string de retorno
    
    Retorno
    -------

    json
        JSON com os dados requisitados 
    """
    resp = client.get_item(
        TableName=TABELA_CONTRATOS,
        Key={
            'ID': { 'S': id_contrato }
        }
    )
    item = resp.get('Item')
    if not item:
        return 'ERRO: Este contrato não existe<br><br>Veja na documentação sobre como criar contratos', 404

    if String:
        return '[{"ID":"'+item.get('ID').get('S')+'","Estado":"'+item.get('Estado').get('S')+'","Data de criação":"'+item.get('Data de criação').get('S')+'","Última modificação":"'+item.get('Última modificação').get('S')+'"}]'
    else:
        return json.loads(str(item).replace("'",'"'))
        
@app.route("/contrato/<string:estado>/<string:id_contrato>")
def get_contract_by_state(id_contrato,estado,string=None):
    """
    Função que busca o estado de um contrato específico
    
    Parâmetros
        ----------
        
    id_contrato: string, obrigatório
        ID do contrato buscado
        
    estado: string, obrigatório
        estado requisitado
        
    String: bool
        Booleano que define a string de retorno
    
    Retorno
    -------

    json
        JSON com os dados requisitados 
    """  
    
    if(estado == 'criar'):
        tabela = TABELA_CRIACAO
    elif(estado != 'finalizar'):
        tabela = TABELA_UPLOAD
    else:
        tabela = TABELA_CONTRATOS
    
    item = Functions().get_contract(client,tabela,id_contrato,estado)
    if string or item == "ERRO: ESTADO INVÁLIDO":
        return item
    else:
        return json.loads(str(item).replace("'",'"'))


@app.route("/contrato/<string:estado>", methods=["POST"])
def create_contract(estado,ID = None):
    """
    Função que cria o contrato
    Parâmetros
        ----------
        
    estado: string, obrigatório
        estado requisitado
        
    ID: string
        string com o ID do contrato
    
    Retorno
    -------

    json
        JSON com os dados requisitados 
        
    string
        String de erro
    """
    
    entrada = request.json

    if(estado == 'criar'):
        json_resposta = Functions().create(client,TABELA_CONTRATOS,TABELA_CRIACAO,ID,entrada)
        return json.loads(str(json_resposta).replace("'",'"'))
    else:
        return "ERRO: o estado "+estado+" não é um estado válido. Estado válido para esse tipo de operação é 'criar'."

@app.route("/contrato/<string:estado>/<string:id_contrato>", methods=["POST"])
def update_contract(id_contrato,estado):
    """
    Função que faz o update do contrato em seus próximos estados, a aprtir do ID
    Parâmetros
        ----------
        
    id_contrato: string
        string com o ID do contrato
        
    estado: string, obrigatório
        estado requisitado
    
    Retorno
    -------

    json
        JSON com os dados atualizados
        
    string
        String de erro ou de sucesso
    """
    
    entrada = request.json    
    
    if(estado == 'criar'):
        
        if 'Caminho do arquivo' in request.files:
            return "ERRO: arquivo enviado. Esperado um JSON"
        
        checaCriacaoString = get_contract(id_contrato,String=True)
        try:
            checaCriacao = json.loads(checaCriacaoString)
        except Exception:
            return checaCriacaoString
        
        if(checaCriacao[0]['Estado'] == 'Finalizado'):
            return "ERRO: Contrato finalizado. Não é possível alterá-lo."
        else:
            json_resposta = create_contract(estado,ID = id_contrato)
            return json_resposta
    
    elif(estado == 'cnh' or estado == 'cpf' or estado == 'renda' or estado == 'imagem'):
        
        checaCriacaoString = get_contract(id_contrato,String=True)
        try:
            checaCriacao = json.loads(checaCriacaoString)
        except Exception:
            return checaCriacaoString   
        
        if not 'Caminho do arquivo' in request.files:
            return "ERRO: nenhum arquivo recebido"
        else:
            entrada = request.files

        if (checaCriacao[0]['Estado'] == 'criar'):
            
            if not entrada.get('Caminho do arquivo'):
                return 'Erro: "Caminho do arquivo" não especificado no JSON de entrada'
        
            try:
                nome = Functions().add_file(s3,BUCKET,entrada,estado,id_contrato)

                json_resposta = Functions().upload(client,TABELA_CONTRATOS,TABELA_UPLOAD,checaCriacao[0]['ID'],nome,estado)

                return "UPLOAD DE "+nome+" COM SUCESSO"
            except Exception as error:
                return error
                return 'JSON inválido. O formato correto deve ser: {"Caminho do arquivo":"CAMINHO_ABSOLUTO_DO_ARQUIVO_COM_EXTENSÃO"}<br><br> Verifique se o caminho está correto'
            
        elif(checaCriacao[0]['Estado'] == 'cnh' or checaCriacao[0]['Estado'] == 'cpf' or checaCriacao[0]['Estado'] == 'renda' or checaCriacao[0]['Estado'] == 'imagem'):
            
            if not entrada.get('Caminho do arquivo'):
                return 'Erro: "Caminho do arquivo" não especificado no JSON de entrada'
            
            try:
                
                arquivo = get_contract_by_state(id_contrato,estado,True)
                
                if(arquivo.get(estado) != None):
                    nome = Functions().update_file(s3,BUCKET,entrada,arquivo.get(estado).get('S'),estado,id_contrato)
                else:
                    nome = Functions().add_file(s3,BUCKET,entrada,estado,id_contrato)
                    
                json_resposta = Functions().upload(client,TABELA_CONTRATOS,TABELA_UPLOAD,checaCriacao[0]['ID'],nome,estado)
                
                return "UPLOAD DE "+nome+" COM SUCESSO"
            except Exception as error:
                return error
                return 'JSON inválido. O formato carreto deve ser: {"Caminho do arquivo":"CAMINHO_ABSOLUTO_DO_ARQUIVO_COM_EXTENSÃO"}<br><br> Verifique se o caminho está correto'
            
        else:
            return "ERRO: Contrato finalizado. Não é possível alterá-lo."
 
    elif(estado == 'finalizar'):
        
        if 'Caminho do arquivo' in request.files:
            return "ERRO: arquivo enviado. Esperado um JSON"
        
        verifica = Functions().can_finalize(client,TABELA_UPLOAD,id_contrato)

        if(verifica):
            retorno = Functions().finalize(client,TABELA_CONTRATOS,id_contrato,entrada)
            return retorno
        else:
            return "Erro: para finalizar um contrato, faça o upload de um arquivo para CNH ou para o CPF."

    else:
        return "ERRO: ESTADO INVÁLIDO"

@app.route("/docs")
def document():    
    """
    Função que traz a documentação da API
    
    Retorno
    -------

    documentacao
        String o HTML da documentação
    """
    
    documentacao = Html().document()
    return documentacao
