from semantic.tests import SemanticTestCase

from example_project.example_app.smodels import BasePrograma


class TestBasePrograma(SemanticTestCase):
    semantic_fixtures = ["example_app/fixtures/fixture_base_programa.ttl"]

    def test_filter_from_uri_with_exact(self):
        programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_uri(self):
        rock_in_rio = BasePrograma.objects.get(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(rock_in_rio.faz_parte_do_canal, u'http://semantica.globo.com/base/Canal_Multishow')
        self.assertEqual(rock_in_rio.foto_perfil, '')
        self.assertEqual(rock_in_rio.id_do_programa_na_webmedia, u'5116')
        self.assertEqual(rock_in_rio.label, u'Rock in Rio')
        self.assertEqual(rock_in_rio.tem_edicao_do_programa, '')
        self.assertEqual(rock_in_rio.uri, u'http://semantica.globo.com/base/Programa_Rock_in_Rio')

    def test_get_from_label_with_filter_startswith(self):
        programas = BasePrograma.objects.filter(label__startswith='Rock')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_endswith(self):
        programas = BasePrograma.objects.filter(label__endswith='Rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_istartswith(self):
        programas = BasePrograma.objects.filter(label__istartswith='rock')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_iendswith(self):
        programas = BasePrograma.objects.filter(label__iendswith='rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_greatest(self):
        programas = BasePrograma.objects.filter(id_do_programa_na_webmedia__gt='5115')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_greatest_or_equal(self):
        programas = BasePrograma.objects.filter(id_do_programa_na_webmedia__gte='5116')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_less_than(self):
        programas = BasePrograma.objects.filter(id_do_programa_na_webmedia__lt='5117')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_less_than_or_equal(self):
        programas = BasePrograma.objects.filter(id_do_programa_na_webmedia__lte='5116')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_exact(self):
        programas = BasePrograma.objects.filter(label__exact='Rock in Rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_iexact(self):
        programas = BasePrograma.objects.filter(label__iexact='rOcK iN rIo')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_regex(self):
        programas = BasePrograma.objects.filter(label__regex='Rock')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_iregex(self):
        programas = BasePrograma.objects.filter(label__iregex='rock')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_contains(self):
        programas = BasePrograma.objects.filter(label__contains='ck in Rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_label_with_filter_icontains(self):
        programas = BasePrograma.objects.filter(label__icontains='ck in rio')
        self.assertEqual(len(programas), 1)


