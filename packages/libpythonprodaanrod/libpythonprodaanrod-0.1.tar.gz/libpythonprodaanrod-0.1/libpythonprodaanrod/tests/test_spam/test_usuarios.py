from libpythonprodaanrod.spam.modelos import Usuario


def test_salvar_usuario(sessao):
    usuario = Usuario(nome='Danilo')
    sessao.salvar(usuario)
    assert isinstance(usuario.id, int)
    sessao.rollback()
    sessao.fechar()


def test_listar_usuario(sessao):
    usuarios = [Usuario(nome='Danilo'), Usuario(nome='Joyce')]
    for usuario in usuarios:
        sessao.salvar(usuario)
    assert usuarios == sessao.listar()
