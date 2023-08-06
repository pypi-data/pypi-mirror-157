import pytest

from libpythonprodaanrod.spam.db import Conexao


@pytest.fixture(scope='session')
def conexao():
    # Setup
    conexao_obj = Conexao()
    yield conexao_obj
    # Tear Down
    conexao_obj.fechar()


@pytest.fixture()
def sessao(conexao):
    sessao_obj = conexao.gerar_sessa()
    yield sessao_obj
    sessao_obj.rollback()
    sessao_obj.fechar()
