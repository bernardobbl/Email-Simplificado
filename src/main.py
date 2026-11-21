# main.py - programa do Tema 6 (e-mail simplificado)
#
# Lê e-mails (um por linha) e diz se cada um é aceito ou rejeitado,
# mostrando o caminho de estados.
#
#   python src/main.py                        modo interativo
#   python src/main.py arquivo.txt            um e-mail por linha
#   python src/main.py -e joao@mail.com       e-mail direto no comando (pode repetir -e)
#   python src/main.py --passo -e j@a.io      mostra símbolo por símbolo
#   python src/main.py --tabela               5-tupla e tabela de transição
#   python src/main.py --minimizar            minimização do AFD
#   python src/main.py --hifen ...            versão que aceita hífen no domínio

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_afd import AFD_EMAIL, AFD_EMAIL_HIFEN, explicar

SETA = " → "
VAZIA = "ε"


def ler_arquivo(nome):
    # utf-8-sig tira o BOM que o Bloco de Notas do Windows coloca no começo do arquivo.
    # Se o arquivo não for UTF-8 (ANSI), lê como latin-1 para não travar.
    try:
        with open(nome, encoding="utf-8-sig") as f:
            linhas = f.read().splitlines()
    except UnicodeDecodeError:
        with open(nome, encoding="latin-1") as f:
            linhas = f.read().splitlines()
    palavras = []
    for linha in linhas:
        if linha == "":
            continue            # linha em branco é ignorada
        if linha == "ε":
            linha = ""          # 'ε' no arquivo representa a palavra vazia
        palavras.append(linha)  # espaços não são removidos: espaço é símbolo fora do alfabeto
    return palavras


def mostrar(afd, palavra, passo_a_passo=False):
    r = afd.executar(palavra)
    print("%s  %s" % ("ACEITA " if r.aceita else "REJEITA", palavra if palavra else VAZIA))
    print("         caminho: " + SETA.join(r.caminho))
    if not r.aceita:
        print("         motivo:  " + explicar(afd, r))
    if passo_a_passo:
        print("         %-3s %-8s %-6s %s" % ("#", "símbolo", "estado", "significado"))
        print("         %-3s %-8s %-6s %s" % ("", "", r.caminho[0], afd.significado[r.caminho[0]]))
        for i in range(len(palavra)):
            q = r.caminho[i + 1]
            print("         %-3d %-8s %-6s %s" % (i + 1, repr(palavra[i]), q, afd.significado[q]))
    print()
    return r.aceita


def interativo(afd, passo):
    print("AFD: " + afd.nome)
    print("Digite um e-mail por linha (Enter numa linha vazia testa a palavra vazia).")
    print("Comandos: :passo  :tabela  :sair\n")
    while True:
        try:
            palavra = input("e-mail> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if palavra == ":sair":
            break
        elif palavra == ":passo":
            passo = not passo
            print("passo a passo " + ("ligado\n" if passo else "desligado\n"))
        elif palavra == ":tabela":
            print(afd.definicao_formal() + "\n\n" + afd.tabela() + "\n")
        else:
            mostrar(afd, palavra, passo)


def minimizar(afd):
    minimo, rodadas = afd.minimizar()
    print("Minimização (algoritmo de Moore): " + afd.nome + "\n")
    for k in range(len(rodadas)):
        blocos = ["{" + ", ".join(b) + "}" for b in rodadas[k]]
        print("P%d (%d blocos): %s" % (k, len(rodadas[k]), "  ".join(blocos)))
    print("\nEstados equivalentes:")
    nenhum = True
    for b in rodadas[-1]:
        if len(b) > 1:
            print("  " + " ≡ ".join(b))
            nenhum = False
    if nenhum:
        print("  nenhum, o AFD já é mínimo")
    print("\nAFD original: %d estados, AFD mínimo: %d estados\n"
          % (len(afd.estados), len(minimo.estados)))
    print(minimo.tabela())


def main():
    global SETA, VAZIA
    p = argparse.ArgumentParser(description="Tema 6 - E-mail simplificado (AFD)")
    p.add_argument("arquivo", nargs="?", help="arquivo com um e-mail por linha")
    p.add_argument("-e", "--email", action="append", default=[], help="e-mail para testar")
    p.add_argument("--passo", action="store_true", help="mostra a leitura símbolo por símbolo")
    p.add_argument("--tabela", action="store_true", help="mostra a 5-tupla e a tabela de transição")
    p.add_argument("--minimizar", action="store_true", help="minimiza o AFD")
    p.add_argument("--dot", metavar="ARQ", help="salva o diagrama no formato do Graphviz")
    p.add_argument("--com-poco", action="store_true", help="desenha o poço no --dot")
    p.add_argument("--hifen", action="store_true", help="usa a versão com hífen no domínio")
    p.add_argument("--ascii", action="store_true", help="usa -> no lugar de →")
    a = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if a.ascii:
        SETA = " -> "
        VAZIA = "(vazia)"

    afd = AFD_EMAIL_HIFEN if a.hifen else AFD_EMAIL
    fez_algo = False

    if a.tabela:
        print(afd.definicao_formal() + "\n")
        print(afd.tabela() + "\n")
        for q in afd.estados:
            print("  %-4s %s" % (q, afd.significado[q]))
        print()
        fez_algo = True
    if a.minimizar:
        minimizar(afd)
        fez_algo = True
    if a.dot:
        with open(a.dot, "w", encoding="utf-8") as f:
            f.write(afd.para_dot(a.com_poco) + "\n")
        print("diagrama salvo em " + a.dot)
        fez_algo = True

    palavras = list(a.email)
    if a.arquivo:
        palavras += ler_arquivo(a.arquivo)

    if palavras:
        aceitas = 0
        for w in palavras:
            if mostrar(afd, w, a.passo):
                aceitas += 1
        print("%d e-mail(s): %d aceito(s), %d rejeitado(s)"
              % (len(palavras), aceitas, len(palavras) - aceitas))
    elif not fez_algo:
        if sys.stdin.isatty():
            interativo(afd, a.passo)
        else:
            # entrada redirecionada: python src/main.py < arquivo.txt
            for linha in sys.stdin.read().splitlines():
                mostrar(afd, linha, a.passo)


if __name__ == "__main__":
    main()
