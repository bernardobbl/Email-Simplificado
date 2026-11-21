# afd.py
# Classe de um AFD genérico: M = (Q, Sigma, delta, q0, F), com estado de erro (poço).
# Aqui não tem nada específico de e-mail, o autômato do tema está em email_afd.py.


class Resultado:
    def __init__(self, palavra, aceita, caminho, pos_poco):
        self.palavra = palavra
        self.aceita = aceita
        self.caminho = caminho      # q0 e depois um estado para cada símbolo lido
        self.pos_poco = pos_poco    # índice do símbolo que levou ao poço (None se não caiu)

    def estado_final(self):
        return self.caminho[-1]


class AFD:
    # estados:    lista Q
    # alfabeto:   string com todos os símbolos de Sigma
    # grupos:     rótulo -> símbolos, ex.: "a-z" -> "abc...z". É só para escrever a
    #             tabela de um jeito mais curto; delta é montada símbolo por símbolo.
    # transicoes: estado -> {rótulo do grupo: destino}
    def __init__(self, nome, estados, alfabeto, grupos, transicoes,
                 inicial, finais, poco, significado):
        self.nome = nome
        self.estados = list(estados)
        self.alfabeto = alfabeto
        self.grupos = grupos
        self.transicoes = transicoes
        self.inicial = inicial
        self.finais = set(finais)
        self.poco = poco
        self.significado = significado
        self.simbolos = set(alfabeto)

        # valida a estrutura da tabela antes de expandi-la. Assim, um erro
        # de digitação em um rótulo de grupo produz uma mensagem útil, em vez
        # de um KeyError durante a construção de delta.
        estados_tabela = set(self.transicoes)
        estados_esperados = set(self.estados)
        faltando = estados_esperados - estados_tabela
        extras = estados_tabela - estados_esperados
        if faltando:
            raise ValueError("faltaram linhas na tabela: %s" % ", ".join(sorted(faltando)))
        if extras:
            raise ValueError("estados desconhecidos na tabela: %s" % ", ".join(sorted(extras)))

        grupos_desconhecidos = set()
        for transicoes_estado in self.transicoes.values():
            grupos_desconhecidos.update(set(transicoes_estado) - set(self.grupos))
        if grupos_desconhecidos:
            raise ValueError(
                "grupos desconhecidos na tabela: %s"
                % ", ".join(sorted(grupos_desconhecidos))
            )

        # monta delta[q][s] para cada estado e cada símbolo
        self.delta = {}
        for q in self.estados:
            self.delta[q] = {}
            for rotulo in self.transicoes[q]:
                for s in self.grupos[rotulo]:
                    if s in self.delta[q]:
                        raise ValueError("delta(%s, %r) definida duas vezes" % (q, s))
                    self.delta[q][s] = self.transicoes[q][rotulo]
        self.conferir()

    def conferir(self):
        # confere se a definição está certa e se delta é total
        Q = set(self.estados)
        if self.inicial not in Q or not self.finais <= Q or self.poco not in Q:
            raise ValueError("q0, F ou o poço não estão em Q")
        for q in self.estados:
            for s in self.alfabeto:
                if s not in self.delta[q]:
                    raise ValueError("faltou definir delta(%s, %r)" % (q, s))
                if self.delta[q][s] not in Q:
                    raise ValueError("delta(%s, %r) vai para um estado que não existe" % (q, s))
        for s in self.alfabeto:
            if self.delta[self.poco][s] != self.poco:
                raise ValueError("o poço tem que voltar para ele mesmo")

    def passo(self, q, s):
        # símbolo fora do alfabeto vai direto para o poço
        if s not in self.simbolos:
            return self.poco
        return self.delta[q][s]

    def executar(self, palavra):
        q = self.inicial
        caminho = [q]
        pos_poco = None
        for i in range(len(palavra)):
            q = self.passo(q, palavra[i])
            caminho.append(q)
            if q == self.poco and pos_poco is None:
                pos_poco = i
        return Resultado(palavra, q in self.finais, caminho, pos_poco)

    def aceita(self, palavra):
        return self.executar(palavra).aceita

    def grupo_do_simbolo(self, s):
        for rotulo in self.grupos:
            if s in self.grupos[rotulo]:
                return rotulo
        return None

    # ---------- impressão ----------

    def definicao_formal(self):
        finais = [q for q in self.estados if q in self.finais]
        return "\n".join([
            "M = (Q, Σ, δ, q0, F)  [%s]" % self.nome,
            "  Q  = {%s}  (%d estados)" % (", ".join(self.estados), len(self.estados)),
            "  Σ  = {%s}  (%d símbolos)" % (", ".join(self.grupos), len(self.alfabeto)),
            "  q0 = %s" % self.inicial,
            "  F  = {%s}" % ", ".join(finais),
            "  poço = " + self.poco,
        ])

    def tabela(self):
        rotulos = list(self.grupos)
        larg = max(6, max(len(q) for q in self.estados) + 4)
        cab = "δ".ljust(larg) + "".join(r.center(larg) for r in rotulos)
        linhas = [cab, "-" * len(cab)]
        for q in self.estados:
            marca = ""
            if q == self.inicial:
                marca = "->"
            if q in self.finais:
                marca = "*"
            nome = (marca + q).rjust(larg - 2).ljust(larg)
            linhas.append(nome + "".join(self.transicoes[q][r].center(larg) for r in rotulos))
        linhas.append("(-> inicial, * final, símbolo fora de Σ vai para %s)" % self.poco)
        return "\n".join(linhas)

    def para_dot(self, mostrar_poco=False):
        # gera o diagrama no formato do Graphviz usando a própria tabela delta
        out = ["digraph AFD {",
               "  rankdir=LR; nodesep=0.5; ranksep=0.45;",
               '  node [shape=circle, fontname="DejaVu Sans", fontsize=20, width=0.75, fixedsize=true];',
               '  edge [fontname="DejaVu Sans Mono", fontsize=18];',
               "  inicio [shape=point, width=0.1];"]
        for q in self.estados:
            if q == self.poco and not mostrar_poco:
                continue
            if q in self.finais:
                out.append('  %s [shape=doublecircle, style=filled, fillcolor="#e8f4ea"];' % q)
            elif q == self.poco:
                out.append('  %s [style=dashed, color="#999999", fontcolor="#777777"];' % q)
            else:
                out.append("  %s;" % q)
        out.append("  inicio -> %s;" % self.inicial)
        for q in self.estados:
            if q == self.poco and not mostrar_poco:
                continue
            # junta numa seta só os grupos que vão para o mesmo destino
            por_destino = {}
            ordem = []
            for rotulo in self.grupos:
                d = self.transicoes[q][rotulo]
                if d not in por_destino:
                    por_destino[d] = []
                    ordem.append(d)
                por_destino[d].append(rotulo)
            for d in ordem:
                if d == self.poco and not mostrar_poco:
                    continue
                texto = []
                for r in por_destino[d]:
                    texto.append(r if len(r) > 1 else "'%s'" % r)
                estilo = ""
                if d == self.poco:
                    estilo = ', style=dashed, color="#aaaaaa", fontcolor="#999999"'
                    if q == self.poco:
                        texto = ["Σ"]
                out.append('  %s -> %s [label=" %s "%s];' % (q, d, ", ".join(texto), estilo))
        if not mostrar_poco:
            out.append('  label="As transições que não aparecem (e os símbolos fora de Σ) vão para o poço %s.";'
                       % self.poco)
            out.append('  labelloc=b; fontname="DejaVu Sans"; fontsize=18;')
        out.append("}")
        return "\n".join(out)

    # ---------- minimização (algoritmo de Moore) ----------

    def alcancaveis(self):
        vistos = [self.inicial]
        i = 0
        while i < len(vistos):
            for s in self.alfabeto:
                p = self.delta[vistos[i]][s]
                if p not in vistos:
                    vistos.append(p)
            i += 1
        return [q for q in self.estados if q in vistos]

    def minimizar(self):
        # começa com P0 = {não finais, finais} e vai separando os estados que
        # vão para blocos diferentes com algum símbolo, até parar de mudar.
        # Devolve o AFD mínimo e a lista de partições P0, P1, ...
        Q = self.alcancaveis()
        simbolos = sorted(self.alfabeto)
        bloco = {}
        for q in Q:
            bloco[q] = 1 if q in self.finais else 0
        rodadas = [self.particao(Q, bloco)]
        while True:
            assinaturas = {}
            novo = {}
            for q in Q:
                a = (bloco[q],) + tuple(bloco[self.delta[q][s]] for s in simbolos)
                if a not in assinaturas:
                    assinaturas[a] = len(assinaturas)
                novo[q] = assinaturas[a]
            mudou = len(set(novo.values())) != len(set(bloco.values()))
            bloco = novo
            if not mudou:
                break
            rodadas.append(self.particao(Q, bloco))

        blocos = self.particao(Q, bloco)
        nome_de = {}
        for b in blocos:
            nome = b[0] if len(b) == 1 else "[" + ",".join(b) + "]"
            for q in b:
                nome_de[q] = nome
        estados = []
        transicoes = {}
        significado = {}
        for b in blocos:
            n = nome_de[b[0]]
            estados.append(n)
            transicoes[n] = {}
            for r in self.transicoes[b[0]]:
                transicoes[n][r] = nome_de[self.transicoes[b[0]][r]]
            significado[n] = " / ".join(self.significado[q] for q in b)
        finais = set(nome_de[q] for q in self.finais if q in nome_de)
        minimo = AFD(self.nome + " (mínimo)", estados, self.alfabeto, self.grupos,
                     transicoes, nome_de[self.inicial], finais, nome_de[self.poco],
                     significado)
        return minimo, rodadas

    def particao(self, Q, bloco):
        grupos = {}
        for q in Q:
            grupos.setdefault(bloco[q], []).append(q)
        lista = list(grupos.values())
        lista.sort(key=lambda b: self.estados.index(b[0]))
        return lista
