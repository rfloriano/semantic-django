# -*- coding:utf-8 -*-
# This is an auto-generated Semantic Globo model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
# Feel free to rename the models, but don't rename semantic_graph values or field names.
#

from semantic.rdf import models


class BasePrograma(models.SemanticModel):
    label = models.CharField(graph='rdfs', max_length=200)
    foto_perfil = models.CharField(graph='base', max_length=200, blank=True)
    id_do_programa_na_webmedia = models.IntegerField(graph='base')
    faz_parte_do_canal = models.URIField(graph='base')
    tem_edicao_do_programa = models.CharField(graph='base', max_length=200, blank=True)

    class Meta:
        # FIXME: Remove this abstract property
        # abstract = True
        managed = False
        graph = 'http://semantica.globo.com/'
        namespace = 'http://semantica.globo.com/base/Programa'

    def __unicode__(self):
        return self.uri


class Apresentador(models.SemanticModel):
    name = models.CharField(graph='rdfs', max_length=200)
    #programa = models.ForeignUri('BasePrograma', graph='base')

    class Meta:
        # FIXME: Remove this abstract property
        # abstract = True
        managed = False
        graph = 'http://semantica.globo.com/'
        namespace = 'http://semantica.globo.com/base/Apresentador'
