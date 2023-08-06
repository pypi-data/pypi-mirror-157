import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MegaSena:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class LotoFacil:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class Quina:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class LotoMania:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class TimeMania:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/timemania/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class DuplaSena:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/duplasena/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class Federal:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/federal/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class Loteca:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/loteca/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class DiadeSorte:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

class SuperSet:

    def __init__(self,concurso=''):
        self.concurso = concurso

    def pesquisar(self):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/supersete/{self.concurso}"
        r = requests.get(url,verify=False)
        return r.status_code, r

    def todosDados(self):
        r = self.pesquisar()[1]
        r.headers['content-type']
        r.encoding
        r.text
        return r.json()

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']
