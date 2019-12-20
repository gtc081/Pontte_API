# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:18:22 2019

@author: crgab
"""
class Html:

    def __init__(self):
        """
        Classe que retorna prints em HTML
        """
        pass
    
    def table(self,items):
        """
        Método que printa a tabela com todos os contratos
        
        Parâmetros
        ----------
        
        items: list, obrigatório
            Lista com todos os contratos
        
        Retorno
        -------

        tabela
            String em HTML com a tabela
        """
        tabela = """
            <table border=1><thead><tr><th>ID do contrato</th><th>Data de criação</th><th>Estado</th><th>Status</th><th>Última modificação</th></tr></thead>
            <tbody>
        """
        for i in items:
            tabela += "<tr><td>"+i['ID']['S']+"</td><td>"+i['Data de criação']['S']+"</td><td>"+i['Estado']['S']+"</td><td>"+i['Status']['S']+"</td><td>"+i['Última modificação']['S']+"</td></tr>"
            
        tabela += "</tbody></table>"
        
        return tabela
    
    def document(self):
        """
        Método que printa a documentação em HTML
        
        Retorno
        -------

        tabela
            String em HTML com a documentação
        """
        
        documentation ="""
        
        <h1>Bem-vindo à Pontte API</h1>
        
        <h2>Como usar:</h2>
        
        <p>Esta é uma API de cadastro rápido dos contratos de empréstimos. Comece criando um contrato, adicionando os campos obrigatórios.</p>
        <p>Só é possível realizar as outras etapas após criar o contrato. A partir do ID do contrato criado, faça o upload de imagens para este contrato. 
        Escolha o "ESTADO" onde será feito o upload do arquivo. Para finalizar um contrato, é necessário ter feito o upload para o estado "cnh" ou "cpf".</p>
        <p>Até aqui, é possível editar as informações do contrato, sobreescrevendo essas informações, uma vez adicionadas.</p>
        <p>Por fim, finalize um contrato definindo-o se foi "Aprovado" ou "Reprovado". A partir daqui, não é mais possível editar as informações do contrato</p>
        <p>Abaixo estão os endpoints usados nesta API</p>
        
        <h2>GET</h2>
        
        <h3>/</h3>
        <p> - Página inicial. Mostra todos os contratos</p>
        
        <h3>/contrato/{ID do contrato}</h3>
        <p> - Traz informação sobre o último estado ao qual o contrato foi submetido</p>
        <p> - RETORNO: JSON com as informações</p>
        
        <h3>/contrato/{estado}/{ID do contrato}</h3>
        <p> - Traz informação sobre aquele estado específico do controto</p>
        <p> - RETORNO: JSON com as informações daquele estado especifico do contrato</p>
        
        <h3>/docs</h3>
        <p> - Leva para esta página</p>
        
        <h2>POST</h2>
        
        <h3>/contrato/{estado}</h3>
        <p> - Cria um contrato novo. Válido apenas para o estado 'criar'</p>
        <p> - PARÂMETROS do POST: JSON (Olhe os ESTADOS mais abaixo para saber quais campos são válidos)</p>
        
        <h3>/contrato/{estado}/{ID do contrato}</h3>
        <p>Adiciona novos elementos a um contrato já criado</p>
        
        <h2>ESTADOS</h2>
        
        <h3>criar</h3>
        <p> - Campos válidos para o JSON do estado "criar"</p>
        <p> --- Nome (String) OBRIGATÓRIO</p>
        <p> --- Email (String) OBRIGATÓRIO</p>
        <p> --- CPF (String) OBRIGATÓRIO</p>
        <p> --- Valor do empréstimo (String) OBRIGATÓRIO</p>
        <p> --- Renda mensal (String)</p>
        <p> --- Data de nascimento (String)</p>
        <p> --- Estado civil (String)</p>
        <p> --- Endereço (String)</p>
        
        <h3>cnh/cpf/renda/imagem</h3>
        <p> - Campo válido para o JSON dos estados "cnh/cpf/renda/imagem"</p>
        <p> --- Caminho do arquivo (String -> Caminho absoluto do arquivo, com extensão)</p>
        
        <h3>finalizar</h3>
        <p> - Campo válido para o JSON do estado "finalizar"</p>
        <p> --- Status ("Aprovado" ou "Reprovado")</p>
        """
        
        return documentation