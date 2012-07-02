# -*- coding:utf-8 -*-
# This is an auto-generated Semantic Globo model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
# Feel free to rename the models, but don't rename semantic_graph values or field names.
#

from semantic.rdf import models


class BasePrograma(models.SemanticModel):
    foto_perfil = models.LiteralField(max_length=200)
    id_do_programa_na_webmedia = models.IntegerField()
    faz_parte_do_canal = models.URIField()
    tem_edicao_do_programa = models.LiteralField(max_length=200)

    class Meta:
        graph = u'http://semantica.globo.com/base/Programa'
