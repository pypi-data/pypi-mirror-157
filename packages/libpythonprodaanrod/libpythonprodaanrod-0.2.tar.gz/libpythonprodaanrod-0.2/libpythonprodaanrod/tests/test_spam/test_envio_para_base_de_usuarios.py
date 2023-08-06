from libpythonprodaanrod.spam.enviador_de_email import Enviador
from libpythonprodaanrod.spam.main import EnviadorDeSpam


def test_envio_de_spam(sessao):
    enviador_de_spam = EnviadorDeSpam(sessao, Enviador())
    enviador_de_spam.enviar_emails(
        'daanrod93@gmail.com',
        'Vambora!',
        'Conseguimo primo'
    )
