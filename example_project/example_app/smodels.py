# -*- coding:utf-8 -*-
# This is an auto-generated Semantic Globo model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
# Feel free to rename the models, but don't rename semantic_graph values or field names.
#

from semantic.rdf import models
from semantic.rdf.models.manager import SemanticManager


class BasePrograma(models.SemanticModel):
    foto_perfil = models.UriField()
    id_do_programa_na_webmedia = models.UriField()
    faz_parte_do_canal = models.UriField()
    tem_edicao_do_programa = models.UriField()

    objects = SemanticManager()

    class Meta:
        db_table = u'http://semantica.globo.com/base/Programa'