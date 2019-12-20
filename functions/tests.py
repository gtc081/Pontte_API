import boto3

import json

import unittest


from flask import Flask
app = Flask(__name__)

TABELA_CONTRATOS = 'TABELA_CONTRATOS'
TABELA_CRIACAO   = 'TABELA_CRIACAO'
TABELA_UPLOAD    = 'TABELA_UPLOAD'
BUCKET           = 'NOME DO BUCKET A SER ALTERADO' 
client           = boto3.client('dynamodb')
dynamodb         = boto3.resource('dynamodb')
s3               = boto3.resource('s3')

from Functions import Functions

class TestFunctions(unittest.TestCase):

    def setUp(self):
        """
        Classe que faz testes para os métodos para a classe Functions
        """
        self.funcao = Functions()
    
    def test_get_contract_estado_errado(self):
        self.assertEqual("ERRO: ESTADO INVÁLIDO", self.funcao.get_contract(client,'tabela_qualquer','id_qualquer','estado_errado'))
        
    def test_get_contract_contrato_nao_existe(self):
        self.assertEqual('ERRO: Este contrato não existe<br><br>Veja na documentação sobre como criar contratos', self.funcao.get_contract(client,TABELA_CONTRATOS,'id_errado','criar'))
        
    def test_get_contract_contrato_upload_nao_existe(self):
        self.assertEqual("Erro: nenhum documento com este id neste estado", self.funcao.get_contract(client,TABELA_UPLOAD,'id_errado','cnh'))
        
    def test_get_contract_contrato_finalizado_nao_existe(self):
        self.assertEqual('ERRO: Este contrato não existe!<br><br>Veja na documentação sobre como criar contratos', self.funcao.get_contract(client,TABELA_UPLOAD,'id_errado','finalizar'))
        
    def test_create_contract_no_name(self):
        self.assertEqual('ERRO: "Nome" é um campo obrigatório', self.funcao.create(client,TABELA_CONTRATOS,TABELA_CRIACAO,None,json.loads('{"campo":"valor"}')))    
        
    def test_create_contract_no_email(self):
        self.assertEqual('ERRO: "Email" é um campo obrigatório', self.funcao.create(client,TABELA_CONTRATOS,TABELA_CRIACAO,None,json.loads('{"Nome":"valor"}')))
        
    def test_create_contract_no_cpf(self):
        self.assertEqual('ERRO: "CPF" é um campo obrigatório', self.funcao.create(client,TABELA_CONTRATOS,TABELA_CRIACAO,None,json.loads('{"Nome":"valor","Email":"valor"}')))
        
    def test_create_contract_no_valor(self):
        self.assertEqual('ERRO: "Valor do empréstimo" é um campo obrigatório', self.funcao.create(client,TABELA_CONTRATOS,TABELA_CRIACAO,None,json.loads('{"Nome":"valor","Email":"valor","CPF":"valor"}')))
        
    def test_can_finalize_no_requirements(self):
        self.assertEqual(False, self.funcao.can_finalize(client,TABELA_UPLOAD,'id_qualquer'))
        
    def test_finalize_no_status(self):
        self.assertEqual('Erro: "Status" não especificado no JSON de entrada', self.funcao.finalize(client,TABELA_CONTRATOS,'id_qualquer',json.loads('{"Status_errado":"qualquer"}')))
        
    def test_finalize_wrong_status(self):
        self.assertEqual('Erro: "Status" inválido. Apenas "Aprovado" ou "Reprovado" são "Status" válidos', self.funcao.finalize(client,TABELA_CONTRATOS,'id_qualquer',json.loads('{"Status":"errado"}')))

if __name__ == '__main__':
    unittest.main()