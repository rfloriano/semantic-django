# -*- coding:utf-8 -*-

import logging

from django.conf import settings


def setup_logs(name, arquivo):
    """
    setup_logs seta informacoes comuns a todos os logs
    Usaremos a classe TimedRotatingFileHandler para rotacionar
    baseado em tempo. Está configurado para todo dia meia-noite
    rotacionar, sem limite de logs rotacionados (nao deleta)
    Também configuramos pra nao propagar pro root logger e poluir eventuais
    logs de outras apps.
    params:
    name = nome do logger, se vier vazio ou none retorna o root logger
    arquivo = nome do arquivo com o path incluido
    """
    var_log = logging.getLogger(name)

    var_log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s')
    # midnight faz com que rotacione todo dia a meia noite e o parametro 0 eh que NAO deve limitar o numero de logs
    # rotacionados.
    handler = logging.FileHandler(arquivo, encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    var_log.addHandler(handler)
    # nao propagar pros loggers superiores (root logger)
    var_log.propagate = 1
    return var_log

# Setando o log que a app-semantica vai utilizar.
log_semantica = setup_logs("sparql", settings.SPARQL_LOG_FILENAME)
settings.log_semantica = log_semantica
