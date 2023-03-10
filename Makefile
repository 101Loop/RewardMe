
# compress
compress:
	@echo "Compressing..."
	tailwindcss -i ./static/src/main.css -o ./static/src/output.css --minify

migrate:
	@echo "Migrating..."
	python manage.py migrate

migrations:
	@echo "Creating migration..."
	python manage.py makemigrations