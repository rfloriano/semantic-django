clean:
	@find . -name "*.pyc" -delete
setup:
	@pip install -r requirements.txt

test-example-project:
	@echo "Running example project tests"
	@cd example_project; PYTHONPATH='..' python manage.py test example_app --settings=example_project.settings_test
	@echo "----------"
	@echo

test-semantic-app:
	@echo "Running semantic app tests"
	@cd semantic; DJANGO_SETTINGS_MODULE=semantic.settings_test nosetests .

test: test-example-project test-semantic-app

syncdb:
	@cd example_project; PYTHONPATH='..' python manage.py syncdb

shell:
	@cd example_project; PYTHONPATH='..' python manage.py shell

server: syncdb
	@cd example_project; PYTHONPATH='..' python manage.py runserver
