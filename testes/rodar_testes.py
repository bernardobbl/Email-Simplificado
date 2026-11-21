# rodar_testes.py - roda todas as palavras de teste de uma vez
#
#   python testes/rodar_testes.py             tabela com esperado, obtido e se bateu
#   python testes/rodar_testes.py --caminho   mostra também o caminho de estados
#
# Também confere se o AFD mínimo (gerado pela minimização) responde igual ao original.

import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PASTA, "..", "src"))
from email_afd import AFD_EMAIL, AFD_EMAIL_HIFEN, explicar

ARQUIVOS = [
    ("obrigatorias.txt", AFD_EMAIL, "Palavras obrigatórias do enunciado"),
    ("proprias.txt", AFD_EMAIL, "Palavras do grupo"),
    ("hifen.txt", AFD_EMAIL_HIFEN, "Versão com hífen (para ir além)"),
]


def ler_casos(nome):
    # cada linha:   esperado   "palavra"   descrição
    # a palavra fica entre aspas para dar para testar espaço e a palavra vazia ("")
    casos = []
    with open(nome, encoding="utf-8-sig") as f:
        for linha in f.read().splitlines():
            if linha.strip() == "" or linha.strip().startswith("#"):
                continue
            i = linha.index('"')
            j = linha.index('"', i + 1)
            esperado = linha[:i].strip()
            if esperado not in ("aceita", "rejeita"):
                raise ValueError("esperado tem que ser aceita ou rejeita: " + linha)
            casos.append((esperado, linha[i + 1:j], linha[j + 1:].strip()))
    return casos


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ver_caminho = "--caminho" in sys.argv
    total = falhas = diferentes_do_minimo = 0

    for nome, afd, titulo in ARQUIVOS:
        minimo = afd.minimizar()[0]
        casos = ler_casos(os.path.join(PASTA, nome))
        print("=" * 90)
        print("%s (%s)" % (titulo, nome))
        print("=" * 90)
        print("%-37s %-9s %-9s %-6s %s" % ("palavra", "esperado", "obtido", "bateu", "descrição"))
        print("-" * 90)
        ok = 0
        for esperado, palavra, descricao in casos:
            r = afd.executar(palavra)
            obtido = "aceita" if r.aceita else "rejeita"
            if minimo.aceita(palavra) != r.aceita:
                diferentes_do_minimo += 1
            total += 1
            if obtido == esperado:
                ok += 1
                bateu = "sim"
            else:
                falhas += 1
                bateu = "NÃO <<"
            w = "ε (vazia)" if palavra == "" else '"' + palavra + '"'
            print("%-37s %-9s %-9s %-6s %s" % (w, esperado, obtido, bateu, descricao))
            if ver_caminho:
                print("      caminho: " + " → ".join(r.caminho))
                if not r.aceita:
                    print("      motivo:  " + explicar(afd, r))
        print("-" * 90)
        print("%d de %d passaram\n" % (ok, len(casos)))

    print("TOTAL: %d de %d testes passaram" % (total - falhas, total))
    print("AFD mínimo deu a mesma resposta em %d de %d palavras" % (total - diferentes_do_minimo, total))
    if falhas or diferentes_do_minimo:
        sys.exit(1)


if __name__ == "__main__":
    main()
