import pytest

from libpythonprodaanrod.spam.enviador_de_email import Enviador, EmailInvalido


def test_criar_enviador_de_email():
    enviador = Enviador()
    assert enviador is not None


@pytest.mark.parametrize(
    'remetente',
    ['daanrod93@gmail.com', 'sharp.danzao@gmail.com']
)
def test_remetente(remetente):
    enviador = Enviador()
    resultado = enviador.enviar(
        remetente,
        'sharp.aedes@gmail.com',
        'Vambora!',
        'Recebaaaaaaaaa'
    )
    assert remetente in resultado


@pytest.mark.parametrize(
    'remetente',
    ['', 'sharp']
)
def test_remetente_invalido(remetente):
    enviador = Enviador()
    with pytest.raises(EmailInvalido):
        enviador.enviar(
            remetente,
            'sharp.aedes@gmail.com',
            'Vambora!',
            'Recebaaaaaaaaa'
        )
