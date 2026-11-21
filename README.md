# Tema 6 - E-mail simplificado (AFD)

Trabalho prático de Linguagens Formais e Autômatos (2026.2), Prof. Dr. Leonardo Angelo.

Integrantes:
- Alawander
- Bernardo Barcellos Leite
- Dereck
- Pietro Santana
- Roberto Vieira

O programa lê e-mails e diz se cada um é aceito ou rejeitado pelo AFD, mostrando o caminho de estados percorrido. Quando rejeita, ele também mostra o motivo.

## Requisitos

Python 3 (qualquer versão 3.x). Não precisa instalar nenhuma biblioteca.

No Windows, troque `python3` por `python` (ou `py`) nos comandos abaixo.

## Como rodar

Abra o terminal na pasta do projeto (onde está este README) e rode:

```
python3 src/main.py
```

Isso abre o modo interativo: digite um e-mail por linha. Os comandos `:passo` (mostra símbolo por símbolo), `:tabela` e `:sair` também funcionam aí.

Para rodar todos os testes de uma vez:

```
python3 testes/rodar_testes.py
```

Para cada palavra o script mostra o resultado esperado, o obtido e se bateu.

## Outras opções

```
python3 src/main.py testes/exemplos.txt          lê um e-mail por linha de um arquivo
python3 src/main.py -e aluno@uni.edu.br          testa um e-mail direto (pode repetir o -e)
python3 src/main.py --passo -e j@a.io            mostra cada símbolo lido e o estado
python3 src/main.py --tabela                     mostra a 5-tupla e a tabela de transição
python3 src/main.py --minimizar                  minimiza o AFD (algoritmo de Moore)
python3 src/main.py --hifen -e joao@mail-x.com   versão que aceita hífen no domínio
python3 testes/rodar_testes.py --caminho         testes mostrando o caminho de cada palavra
python3 testes/verificacao_exaustiva.py          teste extra com todas as palavras até tamanho 7
```

Se o terminal não mostrar a seta `→` direito, acrescente `--ascii`.

Exemplo:

```
$ python3 src/main.py -e j@a.io -e joao..silva@mail.com
ACEITA   j@a.io
         caminho: q0 → q1 → q3 → q4 → q5 → q6 → q7

REJEITA  joao..silva@mail.com
         caminho: q0 → q1 → q1 → q1 → q1 → q2 → qp → qp → qp → ... → qp
         motivo:  o usuário não pode ter dois pontos seguidos (símbolo '.' na posição 6, saindo de q2)
```

## Arquivos

```
src/email_afd.py          o autômato: alfabeto, estados e significado, tabela de transição, q0, F e poço
src/afd.py                classe AFD (executa a palavra, confere a tabela, gera o diagrama, minimiza)
src/main.py               programa principal
testes/obrigatorias.txt   as 9 palavras obrigatórias do enunciado
testes/proprias.txt       37 palavras do grupo (15 aceitas e 22 rejeitadas)
testes/hifen.txt          14 palavras da versão com hífen
testes/exemplos.txt       exemplos para testar o modo arquivo
testes/rodar_testes.py    roda todos os testes
testes/verificacao_exaustiva.py   compara o AFD com as regras escritas de outro jeito
docs/relatorio.pdf        relatório
docs/diagrama.png         diagrama do AFD
docs/diagrama_com_poco.png   diagrama desenhando também o poço
docs/diagrama_hifen.png   diagrama da versão com hífen
docs/fonte/               fonte do relatório (LaTeX) e dos diagramas
```

Os diagramas foram gerados a partir da própria tabela do programa, com o Graphviz:

```
python3 src/main.py --dot docs/diagrama.dot
dot -Tpng docs/diagrama.dot -o docs/diagrama.png
```
