from semantic.tests import SemanticTestCase

from example_app.smodels import BasePrograma


class TestBasePrograma(SemanticTestCase):
    fixtures = ["example_app/fixtures/auth_user.json"]
    semantic_fixtures = ["example_app/fixtures/fixture.n3"]

    def setUp(self):
        self.client.login(username='super', password='secret')

    def tearDown(self):
        self.client.logout()

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

    def test_if_can_edit_a_baseprograma_objects_in_admin(self):
        response = self.client.get('/admin/example_app/baseprograma/http_3A_2F_2Fsemantica.globo.com_2Fbase_2FPrograma_5FRock_5Fin_5FRio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input id="id_faz_parte_do_canal" type="text" name="faz_parte_do_canal" value="http://semantica.globo.com/base/Canal_Multishow" maxlength="200" />')
        self.assertContains(response, '<input id="id_foto_perfil" type="text" name="foto_perfil" maxlength="200" />')
        self.assertContains(response, '<input id="id_tem_edicao_do_programa" type="text" name="tem_edicao_do_programa" maxlength="200" />')
        self.assertContains(response, '<input id="id_id_do_programa_na_webmedia" type="text" class="vIntegerField" value="5116" name="id_do_programa_na_webmedia" />')
        self.assertContains(response, '<input id="id_label" type="text" name="label" value="Rock in Rio" maxlength="200" />')
        self.assertContains(response, '<input id="id_uri" type="text" name="uri" value="http://semantica.globo.com/base/Programa_Rock_in_Rio" maxlength="200" />')

    def test_field_label_has_label_label(self):
        # regression test related to bug introduced in b1bb72e6f386bdf25e35d69d01ef1da417e4b20e
        response = self.client.get('/admin/example_app/baseprograma/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<label for="id_uri" class="required">Uri:</label>')

    def test_if_can_add_baseprograma_objects_in_admin(self):
        response = self.client.get('/admin/example_app/baseprograma/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input id="id_faz_parte_do_canal" type="text" name="faz_parte_do_canal" maxlength="200" />')
        self.assertContains(response, '<input id="id_foto_perfil" type="text" name="foto_perfil" maxlength="200" />')
        self.assertContains(response, '<input id="id_tem_edicao_do_programa" type="text" name="tem_edicao_do_programa" maxlength="200" />')
        self.assertContains(response, '<input id="id_id_do_programa_na_webmedia" type="text" class="vIntegerField" name="id_do_programa_na_webmedia" />')
        self.assertContains(response, '<input id="id_label" type="text" name="label" maxlength="200" />')
        self.assertContains(response, '<input id="id_uri" type="text" name="uri" maxlength="200" />')


class TestBaseProgramaAccessingaVirtuoso(SemanticTestCase):

    semantic_fixtures = ["example_app/fixtures/fixture.n3"]

    allow_virtuoso_connection = True

    def test_filter_from_uri_with_exact(self):
        programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(len(programas), 1)
