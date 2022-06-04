# [SAIL YearBook Portal](https://www.iitg.ac.in/yearbook)

The clean, fast and right way to start a `Django 2.2.20` powered website.

## Getting Started

Setup project environment with [virtualenv](https://virtualenv.pypa.io) and [pip](https://pip.pypa.io).

```bash
$ git clone https://github.com/Student-Alumni-Interaction-Linkage-IITG/YearBook.git
$ virtualenv project-env
$ source project-env/bin/activate
$ cd YearBook/
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```

## Features

* Basic Django scaffolding (commands, templatetags, statics, media files, etc).
* Split settings for specific environment settings (localhost, production, etc) in `yearbook/settings.py`.
* Simple logging setup ready for production envs.

## Contributing

Send a pull request with clear details including the brief documnetation and a picture ( in case of any frontend changes ).

## Contributors

<!-- <a href = "https://github.com/Student-Alumni-Interaction-Linkage-IITG/YearBook/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo = Student-Alumni-Interaction-Linkage-IITG/YearBook"/>
</a> -->
