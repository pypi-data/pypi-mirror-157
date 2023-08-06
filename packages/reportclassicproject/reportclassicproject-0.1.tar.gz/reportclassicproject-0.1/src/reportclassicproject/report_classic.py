from datetime import datetime

from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import A4, legal, letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


class ReportClassicClass:

    def __init__(self, filename, titulo="", subtitulo="", data_rodape=False,
                 fontsize=10, fontname='Helvetica',
                 altura_linha=5, limite_rodape=20,
                 borda_esquerda=10, borda_direita=10,
                 pag_rodape=False, texto_rodape="", pagesize='A4'):
        """Construtor para o Gerador do Relatório
        FILENAME: é o nome do arquivo em formato PDF que irá gerar,
        necessário colocar o diretório
        ex.: /diretorio/nome.pdf
        PAGESIZE: tipo de página: A4, Legal e Letter"""
        if pagesize == 'legal':
            self.pagesize = legal
        elif pagesize == 'letter':
            self.pagesize = letter
        else:
            self.pagesize = A4
        self.largura, self.altura = self.pagesize
        self.pdf = canvas.Canvas(filename, self.pagesize)
        self.fontname = self.valid_font(fontname)
        self.fontnamebold = self.fontname + '-Bold'
        self.fontsize = fontsize
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.pdf.setFont(self.fontname, self.fontsize)
        atual = datetime.now()
        self.data = atual.strftime("%d/%m/%Y %H:%M:%S")
        self.page = 1
        self.texto_rodape = texto_rodape
        self.pag_rodape = pag_rodape
        self.data_rodape = data_rodape
        self.altura_linha = altura_linha
        self.limite_rodape = limite_rodape
        self.altura_atual = 0
        self.borda_direita = borda_direita
        self.borda_esquerda = borda_esquerda

    def valid_font(self, fontname=""):
        if fontname in self.pdf.getAvailableFonts():
            return fontname
        else:
            return 'Helvetica'

    def format_fontname(self, options):
        fonte1 = ""
        fonte2 = ""
        if 'fontname' in options:
            fonte1 = self.valid_font(options['fontname'])
            fonte2 = self.valid_font(options['fontname'])
        else:
            fonte1 = self.fontname
            fonte2 = self.fontname
        if 'bold' in options or 'italic' in options:
            fonte1 += '-'
            fonte2 += '-'
        if 'bold' in options:
            if options['bold']:
                fonte1 += 'Bold'
                fonte2 += 'Bold'
        if 'italic' in options:
            if options['italic']:
                fonte1 += 'Italic'
                fonte2 += 'Oblique'
        if fonte1 in self.pdf.getAvailableFonts():
            return fonte1
        if fonte2 in self.pdf.getAvailableFonts():
            return fonte2
        return 'Helvetica'

    def mm2p(self, milimetros):
        """Converte milimetros para points.
        Retorna pontos"""
        return float(milimetros) * 2.834645669291339

    def p2mm(self, p):
        """Converte points para milimetros.
        Retorna milimetros"""
        return p / 2.834645669291339

    def header(self, titulo="", subtitulo=""):
        """Gerar uma cabeçalho
        TITULO: opcional - Título do cabeçalho
        SUBTITULO: opcional - Subtítulo do cabeçalho"""
        logo = 'home/assets/img/brasao.png'
        if subtitulo == "":
            subtitulo = self.subtitulo
        if titulo == "":
            titulo = self.titulo
        largura_ini = self.mm2p(self.borda_esquerda)
        altura_ini = self.altura - self.mm2p(25)
        self.imagem(logo, largura_ini, altura_ini, width=50, height=50)  # noqa: E501
        self.pdf.setFont(self.fontnamebold, self.fontsize + 2)
        self.pdf.drawString(largura_ini + 70, altura_ini + 20, titulo)
        self.pdf.drawString(largura_ini + 70, altura_ini + 5, subtitulo)
        self.pdf.setFont(self.fontname, self.fontsize)
        self.linha(altura=(altura_ini - 5))
        self.altura_atual = self.altura - self.mm2p(28)
        self.limite_altura = self.mm2p(15)

    def imagem(self, img, largura_ini, altura_ini, width, height):
        """Gerar uma imagem
        img: local onde se encontra a imagem
        largura_ini: posição X no canto inferior esquerdo
        altura_ini: posição Y no canto inferior esquerdo
        width: Largura da imagem a ser impressa
        height: Altura da imagem a ser impressa"""
        if finders.find(img):
            self.pdf.drawImage(finders.find(img), largura_ini, altura_ini, width=width,  # noqa: E501
                               height=height, preserveAspectRatio=True, mask='auto')  # noqa: E501
            self.altura_atual = largura_ini

    def linha(self, altura, largura_ini=0, largura_fim=0):
        """Gerar uma linha
        largura_ini: posição X no canto inferior esquerdo
        largura_fim: posição X no canto inferior direito
        altura: posição Y no canto inferior esquerdo"""
        if largura_ini == 0:
            largura_ini = self.mm2p(self.borda_esquerda)
        if largura_fim == 0:
            largura_fim = self.largura - self.mm2p(self.borda_direita)
        self.pdf.line(largura_ini, altura,
                      largura_fim, altura)
        self.altura_atual = altura

    def footer(self):
        """Gerador do rodapé
        TEXTO: opcional - texto no rodapé
        DATA: opcional - True ou False - para colocar no canto esquerdo a data
         e hora do relatório
        PAGINA: opcional - True ou False - para colocar a paginação
         no canto direito"""
        largura_ini = self.mm2p(self.borda_esquerda)
        altura_ini = self.mm2p(10)
        self.pdf.line(largura_ini, altura_ini,
                      self.largura - self.mm2p(self.borda_esquerda),
                      altura_ini)
        if self.data_rodape:
            self.pdf.drawString(largura_ini, 17, self.data +
                                " - " + self.texto_rodape)
        else:
            self.pdf.drawString(largura_ini, 17, self.texto_rodape)
        if self.pag_rodape:
            self.pdf.drawString(self.largura - 75, 17,
                                "pag. %(page)i" % {'page': self.page})

    def break_page(self):
        """Forçar uma quebra de página"""
        self.page += 1
        self.altura_atual = self.altura
        self.pdf.showPage()

    def render(self, rodape=True):
        """Gerar o pdf
        Este método irá forçar a quebra da última página"""
        if rodape:
            self.footer()
        self.pdf.showPage()
        self.pdf.save()

    def text_redutor(self, texto="", max_width=0):
        """Redutor de texto baseado no tamanho da fonte e tamanho definido"""
        rtn = simpleSplit(texto, self.fontname, self.fontsize, max_width)
        if len(rtn) == 0:
            return texto
        else:
            return rtn[0]

    def width_column(self, lista, larg_folha=0):
        """Cria lista de limite de tamanho das colunas do relatório line"""  # noqa: E501
        rtn = []
        cont = -1
        ult_pos = 0
        if larg_folha <= 0:
            larg_folha = self.largura - self.mm2p(self.borda_direita)
        for key, value in lista.items():
            if cont == -1:
                ult_pos = self.mm2p(key)
                cont = 0
            else:
                rtn.append([self.p2mm(ult_pos), self.mm2p(key) - ult_pos - 5])
                ult_pos = self.mm2p(key)
                cont = 1
        rtn.append([self.p2mm(ult_pos), larg_folha - ult_pos - 5])
        return rtn

    def print_string(self, coluna=0, linha=0, texto="", options={}):
        fontname = ""
        fontsize = 0
        alterar = False
        if 'fontname' in options or 'bold' in options or 'italic' in options:
            fontname = self.format_fontname(options)
            alterar = True
        else:
            fontname = self.fontname
        if 'fontsize' in options:
            fontsize = options['fontsize']
            alterar = True
        else:
            fontsize = self.fontsize
        if alterar:
            fontname_old = self.pdf._fontname
            fontsize_old = self.pdf._fontsize
            self.pdf.setFont(fontname, fontsize)
        self.pdf.drawString(coluna, linha, texto)
        if alterar:
            self.pdf.setFont(fontname_old, fontsize_old)

    def detail_list(self, lista, position, options={}):
        rtn = []
        if len(lista) == len(position):
            cont = 0
            for i in position:
                if cont + 1 in options:
                    opt = options[cont + 1]
                else:
                    opt = {}
                result = []
                result = i + [lista[cont]]
                result.append(opt)
                rtn.append(result)
                cont += 1
        return rtn
