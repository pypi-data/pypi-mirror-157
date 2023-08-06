from reportclassicproject.report_classic import ReportClassicClass


class ReportLabel(ReportClassicClass):

    def render(self):
        super().render(rodape=False)

    def width_column(self, lista, larg_folha=0):
        """Cria lista de limite de tamanho das colunas do relatório line"""  # noqa: E501
        rtn = []
        for key, value in lista.items():
            for item in super().width_column(value, larg_folha):
                rtn.append([key] + item)
        return rtn

    def def_label(self, qtde_eti_linha, qtde_eti_coluna,
                  marg_esquerda, marg_direita, marg_superior,
                  larg_etiqueta, tam_linha,
                  altura_etiqueta, esp_entre_etiqueta,
                  fmt_label):  # noqa: E501
        """ Definir um relatório para etiquetas
        qtde_eti_linha: Quantidade de etiquetas na horizontal
        qtde_eti_coluna: Quantidade de etiquetas na vertical
        marg_esquerda: Margem esquerda (em mm)
        marg_direita: Margem direita (em mm)
        marg_superior: Margem superior (em mm)
        larg_etiqueta: Largura da Etiqueta (em mm)
        altura_etiqueta: Altura da Etiqueta (em mm)
        tam_linha: tamanho da linha dentro da etqieuta (em mm)
        esp_entre_etiqueta: Espaço entre as Etiquetas na linha (em mm)
        fmt_label: (dicionário) Posicionamento dos campos na etiqueta
        """
        self.qtde_eti_linha = qtde_eti_linha
        self.qtde_eti_coluna = qtde_eti_coluna
        self.marg_esquerda = self.mm2p(marg_esquerda)
        self.marg_direita = self.mm2p(marg_direita)
        self.marg_superior = self.mm2p(marg_superior)
        self.larg_etiqueta = self.mm2p(larg_etiqueta)
        self.altura_etiqueta = self.mm2p(altura_etiqueta)
        self.tam_linha = self.mm2p(tam_linha)
        self.esp_entre_etiqueta = self.mm2p(esp_entre_etiqueta)
        self.max_etiq_pagina = qtde_eti_linha * qtde_eti_coluna
        self.etiq_pagina = 0
        self.etiq_coluna = 1
        self.etiq_linha = 0
        self.fmt_label = self.width_column(fmt_label, self.larg_etiqueta)

    def label_detail(self, detalhe, options={}):
        """Imprimir a etiqueta
        Este método irá fazer toda a gestão da quebra de página"""
        if self.etiq_pagina == self.max_etiq_pagina:
            self.break_page()
            self.etiq_pagina = 0
            self.etiq_coluna = 1
            self.etiq_linha = 0
        if self.etiq_linha == self.qtde_eti_linha:
            self.etiq_linha = 0
            self.etiq_coluna += 1
        self.etiq_pagina += 1
        self.etiq_linha += 1
        altura = self.altura - self.marg_superior - \
            self.altura_etiqueta * (self.etiq_coluna - 1)
        largura = self.marg_esquerda + \
            self.larg_etiqueta * (self.etiq_linha - 1) + \
            self.esp_entre_etiqueta * (self.etiq_linha - 1)
        lista = self.detail_list(lista=detalhe, options=options,
                                 position=self.fmt_label)
        self.label_detail_detail(altura=altura, largura=largura, line=lista)

    def label_detail_detail(self, altura, largura, line):
        """Imprime somente o detalhe do relatório tipo etiqueta"""
        self.pdf.setFont(self.fontname, self.fontsize)
        for detail in line:
            max_width = detail[2]
            coluna = largura + self.mm2p(detail[1])
            linha = altura - self.mm2p(self.altura_linha) * detail[0]
            texto = self.text_redutor(texto=detail[3], max_width=max_width)
            self.print_string(coluna=coluna, linha=linha, texto=texto,
                              options=detail[4])
        self.pdf.setFont(self.fontname, self.fontsize)
