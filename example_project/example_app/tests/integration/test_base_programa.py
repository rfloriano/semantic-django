from semantic.tests import SemanticTestCase

from example_project.example_app.smodels import BasePrograma


class TestBaseProgramaVirtuoso(SemanticTestCase):
    fixtures = ["example_app/fixtures/auth_user.json"]
    semantic_fixtures = [
        "example_app/fixtures/fixture_base_programa.ttl",
        "example_app/fixtures/fixture_base_programa_to_virtuoso_access.ttl"
    ]
    allow_virtuoso_connection = True

    def setUp(self):
        self.client.login(username='super', password='secret')

    def tearDown(self):
        self.client.logout()

    def test_filter_from_uri_with_exact(self):
        programa = BasePrograma.objects.filter(
            uri='http://semantica.globo.com/base/Programa_OneProgram'
        )
        self.assertEqual(len(programa), 1)

    def test_object_creation_with_required_data(self):
        programa = BasePrograma.objects.create(
            uri='http://semantica.globo.com/base/Programa_OneProgram',
            id_do_programa_na_webmedia="123",
            faz_parte_do_canal='http://semantica.globo.com/base/Canal_MeuCanal'
        )
        self.assertTrue(programa)

    def test_add_a_baseprograma_object_by_admin_and_need_find_in_admin_baseprograma_list(self):
        self.client.post('/admin/example_app/baseprograma/add/', {
            'uri': 'http://semantica.globo.com/base/Programa_MyProgram',
            'label': 'My Program',
            'faz_parte_do_canal': 'http://semantica.globo.com/base/Canal_MyChannel',
            'tem_edicao_do_programa': '123',
            '_save': 'Save',
        })
        response = self.client.get('/admin/example_app/baseprograma/')
        # FIXME: bug - A inserted programa not appeared in django admin list
        self.assertContains(response, 'http://semantica.globo.com/base/Programa_MyProgram')

    def test_object_creation_with_required_data_and_without_uri(self):
        program = BasePrograma.objects.create(
            id_do_programa_na_webmedia="123",
            faz_parte_do_canal='http://semantica.globo.com/base/Canal_MeuCanal'
        )
        self.assertTrue(program)
        # FIXME: bug - A program is generated with UUID URI, however, program.uri is empty
        self.assertIn('semantica.globo.com', program.uri)
