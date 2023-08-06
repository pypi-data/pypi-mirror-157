from time import sleep


class Conexao:
    def __init__(self):
        sleep(2)

    def gerar_sessa(self):
        return Sessao()

    def fechar(self):
        pass


class Sessao:
    contador = 0
    usuarios = []

    def salvar(self, usuario):
        Sessao.contador += 1
        usuario.id = Sessao.contador
        self.usuarios.append(usuario)

    def listar(self):
        return self.usuarios

    def rollback(self):
        self.usuarios.clear()

    def fechar(self):
        pass
