from semantic.tests import SemanticTestCase


class TestBasePrograma(SemanticTestCase):
    fixtures = ["example_app/fixtures/auth_user.json"]
    semantic_fixtures = ["example_app/fixtures/fixture_base_programa.ttl"]

    def setUp(self):
        self.client.login(username='super', password='secret')

    def tearDown(self):
        self.client.logout()

    def test_if_can_edit_a_baseprograma_objects_in_admin(self):
        response = self.client.get('/admin/example_app/baseprograma/http_3A_2F_2Fsemantica.globo.com_2Fbase_2FPrograma_5FRock_5Fin_5FRio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input id="id_faz_parte_do_canal" type="text" name="faz_parte_do_canal" value="http://semantica.globo.com/base/Canal_Multishow" maxlength="200" />')
        self.assertContains(response, '<input id="id_foto_perfil" type="text" name="foto_perfil" maxlength="200" />')
        self.assertContains(response, '<input id="id_tem_edicao_do_programa" type="text" name="tem_edicao_do_programa" maxlength="200" />')
        self.assertContains(response, '<input id="id_id_do_programa_na_webmedia" type="text" class="vIntegerField" value="5116" name="id_do_programa_na_webmedia" />')
        self.assertContains(response, '<input id="id_label" type="text" name="label" value="Rock in Rio" maxlength="200" />')
        self.assertContains(response, '<input id="id_uri" type="text" name="uri" value="http://semantica.globo.com/base/Programa_Rock_in_Rio" maxlength="200" />')

    def test_if_can_add_baseprograma_objects_in_admin(self):
        response = self.client.get('/admin/example_app/baseprograma/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input id="id_faz_parte_do_canal" type="text" name="faz_parte_do_canal" maxlength="200" />')
        self.assertContains(response, '<input id="id_foto_perfil" type="text" name="foto_perfil" maxlength="200" />')
        self.assertContains(response, '<input id="id_tem_edicao_do_programa" type="text" name="tem_edicao_do_programa" maxlength="200" />')
        self.assertContains(response, '<input id="id_id_do_programa_na_webmedia" type="text" class="vIntegerField" name="id_do_programa_na_webmedia" />')
        self.assertContains(response, '<input id="id_label" type="text" name="label" maxlength="200" />')
        self.assertContains(response, '<input id="id_uri" type="text" name="uri" maxlength="200" />')

    def test_field_label_has_label_label(self):
        # regression test related to bug introduced in b1bb72e6f386bdf25e35d69d01ef1da417e4b20e
        response = self.client.get('/admin/example_app/baseprograma/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<label for="id_uri" class="required">Uri:</label>')
