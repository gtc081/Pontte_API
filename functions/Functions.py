# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 23:06:39 2019

@author: crgab
"""

import hashlib
import datetime

from flask import jsonify

class Functions:

    def __init__(self):
        """
        Classe com funções auxiliares para o arquivo app.py
        """
        pass
    
    def get_contract(self,client,TABELA,ID,estado):
        """
        Método que busca um item em uma tabela, pelo ID

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca bot03
            
        TABELA: string, obrigatório
            Noma da tabela a ser buscada
            
        ID: string, obrigatório (default=None)
            ID do documento buscado
            
        estado: string, obrigatório
            estado que define como será o retorno desse método

        Retorno
        -------
        
        json
            JSON com informações da tabela do estado 'criar'
            
        string
            String com mensagens de erro

        """

        # se não for um desses estados, retorna mensagem de erro
        if (estado != 'criar' and estado != 'cnh' and estado != 'cpf' and estado != 'renda' and estado != 'imagem' and estado != 'finalizar'):
            return "ERRO: ESTADO INVÁLIDO"
        else:

            #busca o contrato da tabela do respectivo estado
            resp = client.get_item(
                TableName=TABELA,
                Key={
                    'ID': { 'S': ID }
                }
            )
            item = resp.get('Item')

            # para cada estado retorna uma resposta diferente
            if(estado == 'criar'):
                if not item:
                    return 'ERRO: Este contrato não existe<br><br>Veja na documentação sobre como criar contratos'
            
                return item
                
            elif(estado != 'finalizar'):
                
                if not item:
                    return "Erro: nenhum documento com este id neste estado"
                else:
                    return item
                
            else:
                if not item:
                    return 'ERRO: Este contrato não existe!<br><br>Veja na documentação sobre como criar contratos'
                return item
                
    
    def update(self,client,tabela,ID,key,value):
        """
        Método que faz um update em um item em uma determinada tabela

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca bot03
            
        tabela: string, obrigatório
            Noma da tabela a ser alterada
            
        ID: string, obrigatório (default=None)
            ID do contrato, caso exista
            
        key: string, obrigatório
            Chave cujo o valor será atualizado
            
        value: string, obrigatório
            Valor a ser atualizado
        """
        client.update_item(
            TableName=tabela,
            Key={
                'ID': {'S': ID }
            },
            UpdateExpression='SET #attrName = :val1',
            ExpressionAttributeNames={
                "#attrName" : key
            },
            ExpressionAttributeValues={
                ':val1': {'S': value }
            }
        )
    
    def create(self,client,TABELA_CONTRATOS,TABELA_CRIACAO,ID,entrada):
        """
        Método para criar um contrato, ou editar o estado CRIAR de um contrato que já existe

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca boto3
            
        TABELA_CONTRATOS: string, obrigatório
            Noma da tabela dos estados dos contratos
            
        TABELA_CRIACAO: string, obrigatório
            Noma da tabela do estado de criação dos contratos
            
        ID: string, obrigatório (default=None)
            ID do contrato, caso exista
            
        entrada: json, obrigatório
            JSON com as informações que vem do POST
            Os campos válidos são(Lembre-se que há distinção entre letras MAIÚSCULAS e MINÚSCULAS):
                - Nome
                - Email
                - CPF
                - Valor do empréstimo
                - Renda
                - Data de nascimento
                - Estado civil
                - Endereço

        Retorno
        -------
        
        json
            JSON com informações que foram cadastradas ou editadas
        """
        
        # pega as informacoes do JSON de entrada
        nome            = entrada.get('Nome')
        email           = entrada.get('Email')
        cpf             = entrada.get('CPF')
        valor           = entrada.get('Valor do empréstimo')
        renda           = entrada.get('Renda mensal')
        data_nascimento = entrada.get('Data de nascimento')
        estado_civil    = entrada.get('Estado civil')
        endereco        = entrada.get('Endereço')
        
        # pega a hora da modificação
        hora = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # se um ID for passada, cria o contrato
        if not ID: 
            
            # verifica os campos obrigatórios
            if not nome:
                return 'ERRO: "Nome" é um campo obrigatório'
            if not email:
                return 'ERRO: "Email" é um campo obrigatório'
            if not cpf:
                return 'ERRO: "CPF" é um campo obrigatório'
            if not valor:
                return 'ERRO: "Valor do empréstimo" é um campo obrigatório' 
            if not renda:
                renda = None
            if not data_nascimento:
                data_nascimento = None
            if not estado_civil:
                estado_civil = None
            if not endereco:
                endereco = None   
                
            # gera o id da tabela principal
            id_contrato = hashlib.md5((hora+nome).encode()).hexdigest()
        
            # adiciona um elemento na tabela princiapal sobre o estado do contrato
            client.put_item(
                TableName=TABELA_CONTRATOS,
                Item={
                    'ID': {'S': str(id_contrato) },
                    'Estado': {'S': 'criar' },
                    'Data de criação': {'S': hora },
                    'Última modificação': {'S': hora },
                    'Status':{'S':'Em andamento'}
                }
            )
        
            # adiciona um elemento na tabela de criação de contratos
            client.put_item(
                TableName=TABELA_CRIACAO,
                Item={
                    'ID': {'S': str(id_contrato) },
                    'Nome': {'S': nome },
                    'Email': {'S': email },
                    'CPF': {'S': cpf },
                    'Valor do empréstimo': {'S': valor },
                    'Renda mensal': {'S': str(renda) },
                    'Data de nascimento': {'S': str(data_nascimento) },
                    'Estado civil': {'S': str(estado_civil) },
                    'Endereço': {'S': str(endereco) },
                }
            )
        
            return {
                'ID': {'S': str(id_contrato) },
                'Nome': {'S': nome },
                'Email': {'S': email },
                'CPF': {'S': cpf },
                'Valor do empréstimo': {'S': valor },
                'Renda mensal': {'S': str(renda) },
                'Data de nascimento': {'S': str(data_nascimento) },
                'Estado civil': {'S': str(estado_civil) },
                'Endereço': {'S': str(endereco) },
            }
        
        # se o contrato já existir, faz o update do estado de criação do contrato
        else:
            # faz o update para cada campo que for adicionado e retorna um json com esses campos
            retorno = {'ID': {'S': ID }}
            if nome:
                self.update(client,TABELA_CRIACAO,ID,'Nome',nome)
                retorno['Nome'] = {'S': nome }
            if email:
                self.update(client,TABELA_CRIACAO,ID,'Email',email)
                retorno['Email'] = {'S': email }
            if cpf:
                self.update(client,TABELA_CRIACAO,ID,'CPF',cpf)
                retorno['CPF'] = {'S': cpf }
            if valor:
                self.update(client,TABELA_CRIACAO,ID,'Valor do empréstimo',valor)
                retorno['Valor do empréstimo'] = {'S': valor }
            if renda:
                self.update(client,TABELA_CRIACAO,ID,'',renda)
                retorno['Renda mensal'] = {'S': renda }
            if data_nascimento:
                self.update(client,TABELA_CRIACAO,ID,'Data de nascimento',data_nascimento)
                retorno['Data de nascimento'] = {'S': data_nascimento }
            if estado_civil:
                self.update(client,TABELA_CRIACAO,ID,'Estado civil',estado_civil)
                retorno['Estado civil'] = {'S': estado_civil }
            if endereco:
                self.update(client,TABELA_CRIACAO,ID,'Endereço',endereco)
                retorno['Endereço'] = {'S': endereco }
                
            self.update(client,TABELA_CONTRATOS,ID,'Última modificação',hora)
                
            return retorno
        
    def upload(self,client,TABELA_CONTRATOS,TABELA_UPLOAD,ID,arquivo,estado):
        """
        Método para gravar na tabela de upload as informações sobre o arquivo enviado

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca boto3
            
        TABELA_CONTRATOS: string, obrigatório
            Nome da tabela dos estados dos contratos
            
        TABELA_UPLOAD: string, obrigatório
            Nome da tabela do estado de arquivos enviados, dos contratos
            
        ID: string, obrigatório (default=None)
            ID do contrato, caso exista
            
        arquivo: string, obrigatório
            Nome do arquivo enviado
            
        estado: string, obrigatório
            Nome do tipo de arquivo enviado

        Retorno
        -------
        
        json
            JSON com informações que foram cadastradas
        """
        # pega a hora da modificação
        hora = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        # gera o id da tabela de uploads
        id_arquivo = hashlib.md5((hora+arquivo+estado).encode()).hexdigest()

        # atualiza o elemento na tabela princiapal sobre o estado do contrato
        self.update(client,TABELA_CONTRATOS,ID,'Estado',estado)
        
        # busca um documento com o ID do contrato e, caso exista, faz o update do documento
        doc = self.get_contract(client,TABELA_UPLOAD,ID,estado)

        if(doc != "Erro: nenhum documento com este id neste estado"):
            self.update(client,TABELA_UPLOAD,ID,estado,arquivo)
            item = self.get_contract(client,TABELA_UPLOAD,ID,estado)
            return item
        else:
            item = {
                    'ID': {'S': ID },
                    'ID_arquivo': {'S': str(id_arquivo) },
                    'Última modificação': {'S': hora },
                    estado: {'S': arquivo }
                }
        
            # adiciona um elemento na tabela de uploads de documentos
            client.put_item(
                TableName=TABELA_UPLOAD,
                Item=item
            )
            return jsonify(item)
        
    def can_finalize(self,client,TABELA_UPLOAD,ID):
        """
        Método que analisa se é possível finalizar o contrato

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca boto3
            
        TABELA_UPLOAD: string, obrigatório
            Nome da tabela do estado de arquivos enviados dos contratos
            
        ID: string, obrigatório (default=None)
            ID do contrato

        Retorno
        -------
        
        True or False
            bool 
        """
        
        item = self.get_contract(client,TABELA_UPLOAD,ID,'cnh')
        if (item == 'Erro: nenhum documento com este id neste estado' or (not item.get('cnh') and not item.get('cpf'))):
            return False
        else:
            return True
        
    def finalize(self,client,TABELA_CONTRATOS,ID,entrada):
        """
        Método para gravar na tabela de upload as informações sobre o arquivo enviado

        Parâmetros
        ----------
        
        client: objeto, obrigatório
            Objeto que acessa o DynamoDB através da biblioteca boto3
            
        TABELA_CONTRATOS: string, obrigatório
            Noma da tabela dos estados dos contratos
            
        ID: string, obrigatório (default=None)
            ID do contrato
            
        entrada: list, obrigatório
            JSON com as informações que vem do POST
            O úncio campo válido é(Lembre-se que há distinção entre letras MAIÚSCULAS e MINÚSCULAS):
                - Status

        Retorno
        -------
        
        nome_arquivo
            string com o nome do arquivo enviado
        """
        item = entrada.get('Status')
        
        if not item:
            return 'Erro: "Status" não especificado no JSON de entrada'
        else:
            if (entrada['Status'] != 'Aprovado' and entrada['Status'] != 'Reprovado'):
                return 'Erro: "Status" inválido. Apenas "Aprovado" ou "Reprovado" são "Status" válidos'
            else:
                self.update(client,TABELA_CONTRATOS,ID,'Status',item)
                self.update(client,TABELA_CONTRATOS,ID,'Estado','Finalizado')
                novoitem = self.get_contract(client,TABELA_CONTRATOS,ID,'Finalizado')
                return novoitem
    
    def add_file(self,s3,BUCKET,entrada,estado,ID):
        """
        Método para gravar na tabela de upload as informações sobre o arquivo enviado

        Parâmetros
        ----------
        
        s3: objeto, obrigatório
            Objeto que acessa o S3 através da biblioteca boto3
            
        BUCKET: string, obrigatório
            Noma do Bucket da S3 onde serão adicionados os arquivos
            
        entrada: list, obrigatório
            JSON com as informações que vem do POST
            O úncio campo válido é (Lembre-se que há distinção entre letras MAIÚSCULAS e MINÚSCULAS):
                - Caminho do arquivo

        estado: string, obrigatório
            Noma do estado que concatena com o nome do arquivo para gera a chave do mesmo

        Retorno
        -------
        
        nome_arquivo
            string com o nome do arquivo enviado
        """
        
        
        nome_arquivo = entrada['Caminho do arquivo'].filename
        
#        with open(entrada['Caminho do arquivo'], "rb") as f:
        s3.Bucket(BUCKET).put_object(Key=(ID+estado+nome_arquivo),Body=entrada['Caminho do arquivo'])
            
        return nome_arquivo
    
    def update_file(self,s3,BUCKET,entrada,arquivo,estado,ID):
        """
        Método para deletar o arquivo anterior e adicionar o novo arquivo enviado

        Parâmetros
        ----------
        
        s3: objeto, obrigatório
            Objeto que acessa o S3 através da biblioteca boto3
            
        BUCKET: string, obrigatório
            Noma do Bucket da S3 onde serão adicionados os arquivos
            
        entrada: list, obrigatório
            JSON com as informações que vem do POST
            O úncio campo válido é(Lembre-se que há distinção entre letras MAIÚSCULAS e MINÚSCULAS):
                - Caminho do arquivo

        arquivo: string, obrigatório
            Nome do arquivo que será retirado do s3
            
        estado: string, obrigatório
            Noma do estado que concatena com o nome do arquivo para gera a chave do mesmo

        Retorno
        -------
        
        nome_arquivo
            string com o nome do arquivo enviado
        """
        
        s3.Object(BUCKET, (ID+estado+arquivo)).delete()
        
        nome_arquivo = self.add_file(s3,BUCKET,entrada,estado,ID)
        
        return nome_arquivo
        
        