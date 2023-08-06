from reportclassicproject.report_classic import ReportClassicClass


class ReportMLineDetail(ReportClassicClass):

    def width_column(self, lista, larg_folha=0):
        """Cria lista de limite de tamanho das colunas do relatório line"""  # noqa: E501
        rtn = []
        for key, value in lista.items():
            for item in super().width_column(value, larg_folha=0):
                rtn.append([key] + item)
        return rtn

    def def_mline_detail(self, cabec, text_cabec="", imp_cabec=True,
                         sep_head_line_detail=True,
                         sep_detail_line_detail=False):  # noqa: E501
        """ Definir um relatório do tipo linha
        cabec: Dicionário com o cabeçalho do relatório
        sep_head_line_detail: boleano - separar o cabeçalho com uma linha
        sep_detail_line_detail: boleano - separar cada linha com um separador
        """
        self.sep_head_line_detail = sep_head_line_detail
        self.sep_detail_line_detail = sep_detail_line_detail
        self.cabec_line_detail = cabec
        self.text_mcabec = text_cabec
        self.imp_cabec = imp_cabec
        self.rep_line_detail_width = self.width_column(cabec)

    def mline_detail(self, detalhe, options={}):
        """Imprimir o detalhe do relatório tipo line_detail.
        Este método irá fazer toda a gestão da quebra de página"""
        if self.altura_atual <= self.mm2p(self.limite_rodape) and self.altura_atual != 0:  # noqa: E501
            self.footer()
            self.break_page()
            self.altura_atual = 0
        if self.altura_atual == 0:
            self.header()
            self.mline_detail_subheader(altura=self.altura_atual,
                                        cabec=self.cabec_line_detail,  # noqa: E501
                                        separator=self.sep_head_line_detail)
        lista = self.detail_list(lista=detalhe, options=options,
                                 position=self.rep_line_detail_width)
        self.mline_detail_detail(altura=self.altura_atual, line=lista,
                                 separator=self.sep_detail_line_detail)

    def mline_detail_subheader(self, altura, cabec, separator=True):
        """Imprimir cabecalho do relatório tipo line_detail."""
        if not self.imp_cabec:
            return True
        self.pdf.setFont(self.fontnamebold, self.fontsize)
        if self.text_mcabec == "":
            salto = 0
            for linha, value in cabec.items():
                for key, texto in value.items():
                    self.print_string(coluna=key, linha=altura -
                                      self.mm2p(self.altura_linha)
                                      * linha, texto=texto)
                salto += self.mm2p(self.altura_linha)
        else:
            self.print_string(coluna=self.mm2p(self.borda_esquerda),
                              linha=altura - self.mm2p(self.altura_linha),
                              texto=self.text_mcabec)
            salto = self.mm2p(self.altura_linha)
        self.altura_atual = altura - salto
        if separator:
            self.linha(altura=self.altura_atual - self.mm2p(2))
        self.pdf.setFont(self.fontname, self.fontsize)

    def mline_detail_detail(self, altura, line, separator=False):
        """Imprime somente o detalhe do relatório tipo line_detail"""
        self.pdf.setFont(self.fontname, self.fontsize)
        qtde = 0
        for detail in line:
            max_width = detail[2]
            linha = altura - self.mm2p(self.altura_linha) * detail[0]
            texto = self.text_redutor(texto=detail[3], max_width=max_width)
            self.print_string(coluna=self.mm2p(detail[1]), linha=linha,
                              texto=texto, options=detail[4])
            qtde = detail[0]
        self.altura_atual = altura - self.mm2p(self.altura_linha) * qtde
        if separator:
            self.linha(altura=self.altura_atual - self.mm2p(2))
        self.pdf.setFont(self.fontname, self.fontsize)
