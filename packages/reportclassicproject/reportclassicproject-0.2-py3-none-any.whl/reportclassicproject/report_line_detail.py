from reportclassicproject.report_classic import ReportClassicClass


class ReportLineDetail(ReportClassicClass):

    def def_line_detail(self, cabec, sep_head_line_detail=True,
                        sep_detail_line_detail=False):  # noqa: E501
        """ Definir um relatório do tipo linha
        cabec: Dicionário com o cabeçalho do relatório
        sep_head_line_detail: boleano - separar o cabeçalho com uma linha
        sep_detail_line_detail: boleano - separar cada linha com um separador
        """
        self.sep_head_line_detail = sep_head_line_detail
        self.sep_detail_line_detail = sep_detail_line_detail
        self.cabec_line_detail = cabec
        self.rep_line_detail_width = self.width_column(cabec)

    def line_detail(self, detalhe, options={}):
        """Imprimir o detalhe do relatório tipo line_detail.
        Este método irá fazer toda a gestão da quebra de página"""
        if self.altura_atual <= self.mm2p(self.limite_rodape) and self.altura_atual != 0:  # noqa: E501
            self.footer()
            self.break_page()
            self.altura_atual = 0
        if self.altura_atual == 0:
            self.header()
            self.line_detail_subheader(altura=self.altura_atual,
                                       cabec=self.cabec_line_detail,  # noqa: E501
                                       separator=self.sep_head_line_detail)
        lista = self.detail_list(lista=detalhe, options=options,
                                 position=self.rep_line_detail_width)
        self.line_detail_detail(altura=self.altura_atual, line=lista,
                                separator=self.sep_detail_line_detail)
        self.altura_atual -= self.altura_linha

    def line_detail_subheader(self, altura, cabec, separator=True):
        """Imprimir cabecalho do relatório tipo line_detail."""
        self.pdf.setFont(self.fontnamebold, self.fontsize)
        for key, value in cabec.items():
            self.print_string(coluna=key, linha=altura -
                              self.mm2p(self.altura_linha), texto=value)
        self.altura_atual = altura - self.mm2p(self.altura_linha)
        if separator:
            self.linha(altura=self.altura_atual - self.mm2p(2))
        self.pdf.setFont(self.fontname, self.fontsize)

    def line_detail_detail(self, altura, line, separator=False):
        """Imprime somente o detalhe do relatório tipo line_detail"""
        self.pdf.setFont(self.fontname, self.fontsize)
        for detail in line:
            max_width = detail[1]
            linha = altura - self.mm2p(self.altura_linha)
            texto = self.text_redutor(texto=detail[2], max_width=max_width)
            self.print_string(coluna=self.mm2p(detail[0]), linha=linha,
                              texto=texto, options=detail[3])
        self.altura_atual = altura - self.mm2p(self.altura_linha)
        if separator:
            self.linha(altura=self.altura_atual - self.mm2p(2))
        self.pdf.setFont(self.fontname, self.fontsize)
