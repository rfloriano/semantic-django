
clean:
	@find . -name "*.pyc" -delete
setup:
	@pip install -r requirements.txt
	@sudo chmod 777 /usr/local/virtuoso-opensource/var/lib/virtuoso/db/

test-example-project:
	@echo "Running example project tests"
	@cd example_project; PYTHONPATH='..' VIRTUOSO_HOME=/usr/local/virtuoso-opensource  python manage.py test example_app --settings=example_project.settings_test
	@echo "----------"
	@echo

test-semantic-app:
	@echo "Running semantic app tests"
	@cd semantic; VIRTUOSO_HOME=/usr/local/virtuoso-opensource DJANGO_SETTINGS_MODULE=semantic.settings_test nosetests --verbosity=3 .

test-pep8:
	@pep8 example_project --ignore=E501,E126,E127,E128
	@#pep8 semantic --ignore=E501,E126,E127,E128

test: test-example-project test-semantic-app

syncdb:
	@cd example_project; PYTHONPATH='..' python manage.py syncdb

shell:
	@cd example_project; PYTHONPATH='..' python manage.py shell

server: syncdb
	@cd example_project; PYTHONPATH='..' python manage.py runserver
