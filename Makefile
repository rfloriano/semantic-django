clean:
	@find . -name "*.pyc" -delete
setup:
	@pip install -r requirements.txt

test:
	@cd example_project; PYTHONPATH='..' python manage.py test example_app