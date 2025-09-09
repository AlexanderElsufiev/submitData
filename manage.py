
# ЗАПУСК = python manage.py runserver
# ВВОД ДАННЫХ   = http://127.0.0.1:8000/api/submit/
# ЧТЕНИЕ ВСЕХ ПЕРЕВАЛОВ ДАННОГО ПОЛЬЗОВАТЕЛЯ
#               = http://127.0.0.1:8000/api/submitData/?user__email=proba@email.tld1
# ЧТЕНИЕ КОНКРЕТНОГО ПЕРЕВАЛА
#               = http://127.0.0.1:8000/api/submitData/4/



# УДАЛЕНИЕ ПЛОХИХ МИГРАЦИЙ =   python manage.py migrate api zero --fake

# http://127.0.0.1:8000/api/submitData/ - не работает пока

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
