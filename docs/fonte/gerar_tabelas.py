# gerar_tabelas.py
# Gera o tabelas.tex usado no relatório a partir do código em src/,
# assim a tabela de transição e os resultados dos testes no relatório
# são os mesmos que o programa produz.

import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..")
sys.path.insert(0, os.path.join(RAIZ, "src"))
sys.path.insert(0, os.path.join(RAIZ, "testes"))

from email_afd import AFD_EMAIL, AFD_EMAIL_HIFEN, explicar
from rodar_testes import ler_casos


def esc(t, visivel=False):
    out = []
    for c in t:
        if c in "_&%$#{}":
            out.append("\\" + c)
        elif c == "\\":
            out.append("\\textbackslash{}")
        elif c == "~":
            out.append("\\textasciitilde{}")
        elif c == "^":
            out.append("\\textasciicircum{}")
        elif c == " " and visivel:
            out.append("␣")
        else:
            out.append(c)
    return "".join(out)


def tt(t):
    return "\\texttt{%s}" % esc(t, True)


def estado(q):
    if q.startswith("["):
        return "$\\{%s\\}$" % ",".join("q_{%s}" % x[1:] for x in q[1:-1].split(","))
    if q == "qp":
        return "$q_p$"
    return "$q_{%s}$" % q[1:]


def tabela_delta(afd, nome):
    rot = list(afd.grupos)
    cols = "l" + "c" * len(rot)
    linhas = ["\\begin{tabular}{%s}" % cols, "\\toprule",
              "$\\delta$ & " + " & ".join(tt(r) for r in rot) + " \\\\", "\\midrule"]
    for q in afd.estados:
        marca = ""
        if q == afd.inicial:
            marca = "$\\rightarrow$\\,"
        if q in afd.finais:
            marca = "$*$\\,"
        cel = []
        for r in rot:
            d = afd.transicoes[q][r]
            s = estado(d)
            if d == afd.poco:
                s = "\\textcolor{cinza}{%s}" % s
            cel.append(s)
        cor = "\\rowcolor{verdeclaro}" if q in afd.finais else ""
        linhas.append(cor + marca + estado(q) + " & " + " & ".join(cel) + " \\\\")
    linhas += ["\\bottomrule", "\\end{tabular}"]
    return "\\newcommand{\\%s}{%%\n%s}\n" % (nome, "\n".join(linhas))


def tabela_significado(afd, nome):
    linhas = ["\\begin{tabular}{@{}l p{0.80\\linewidth}@{}}", "\\toprule",
              "estado & significado \\\\",
              "\\midrule"]
    for q in afd.estados:
        s = esc(afd.significado[q]).replace("->", "$\\Rightarrow$")
        cor = "\\rowcolor{verdeclaro}" if q in afd.finais else ""
        linhas.append(cor + estado(q) + " & " + s + " \\\\")
    linhas += ["\\bottomrule", "\\end{tabular}"]
    return "\\newcommand{\\%s}{%%\n%s}\n" % (nome, "\n".join(linhas))


def tabela_testes(afd, arquivo, nome):
    casos = ler_casos(os.path.join(RAIZ, "testes", arquivo))
    linhas = ["\\begin{tabular}{@{}l l l c >{\\raggedright\\arraybackslash}p{0.43\\linewidth}@{}}", "\\toprule",
              "palavra & esperado & obtido & ok & para em / motivo \\\\", "\\midrule"]
    ok = 0
    for esperado, palavra, _ in casos:
        r = afd.executar(palavra)
        obtido = "aceita" if r.aceita else "rejeita"
        bateu = obtido == esperado
        ok += bateu
        w = "$\\varepsilon$ (vazia)" if palavra == "" else tt(palavra)
        if r.aceita:
            info = "termina em " + estado(r.estado_final())
        else:
            m = explicar(afd, r)
            if " (símbolo" in m:
                m = m[:m.index(" (símbolo")]
            if " (posição" in m:
                m = m[:m.index(" (posição")]
            m = esc(m).replace("Σ", "$\\Sigma$")
            onde = estado(r.estado_final()) if r.pos_poco is None else \
                "%s, pos.\\,%d" % (estado("qp"), r.pos_poco + 1)
            info = onde + ": " + m
        linhas.append("%s & %s & %s & %s & {\\scriptsize %s} \\\\" % (
            w, esperado, obtido, "\\ok" if bateu else "\\falha", info))
    linhas += ["\\bottomrule", "\\end{tabular}"]
    texto = "\\newcommand{\\%s}{%%\n%s}\n" % (nome, "\n".join(linhas))
    texto += "\\newcommand{\\%sTotal}{%d/%d}\n" % (nome, ok, len(casos))
    return texto, ok, len(casos)


def minimizacao(afd, nome):
    _, rodadas = afd.minimizar()
    linhas = ["\\begin{tabular}{@{}l c l@{}}", "\\toprule", "rodada & blocos & partição \\\\",
              "\\midrule"]
    for k, part in enumerate(rodadas):
        blocos = ["$\\{%s\\}$" % ",".join(estado(q).strip("$") for q in b) for b in part]
        linhas.append("$P_{%d}$ & %d & {\\small %s} \\\\" % (k, len(part), "\\ ".join(blocos)))
    linhas += ["\\bottomrule", "\\end{tabular}"]
    return "\\newcommand{\\%s}{%%\n%s}\n" % (nome, "\n".join(linhas))


def main():
    partes = ["%% gerado por gerar_tabelas.py\n"]
    partes.append(tabela_delta(AFD_EMAIL, "TabelaDelta"))
    partes.append(tabela_significado(AFD_EMAIL, "TabelaEstados"))
    minimo, _ = AFD_EMAIL.minimizar()
    partes.append(tabela_delta(minimo, "TabelaDeltaMinimo"))
    partes.append(minimizacao(AFD_EMAIL, "TabelaMinimizacao"))
    total = ok_total = 0
    for afd, arq, nome in [(AFD_EMAIL, "obrigatorias.txt", "TestesObrig"),
                           (AFD_EMAIL, "proprias.txt", "TestesProprias"),
                           (AFD_EMAIL_HIFEN, "hifen.txt", "TestesHifen")]:
        t, ok, n = tabela_testes(afd, arq, nome)
        partes.append(t)
        total += n
        ok_total += ok
    partes.append("\\newcommand{\\TestesTotal}{%d/%d}\n" % (ok_total, total))
    with open(os.path.join(AQUI, "tabelas.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print("tabelas.tex gerado (%d/%d testes passando)" % (ok_total, total))


if __name__ == "__main__":
    main()
