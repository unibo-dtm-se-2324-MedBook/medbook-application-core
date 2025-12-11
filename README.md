# MedBook - Your Personal Medical Hub

MedBook is a privacy-first mobile app that brings all your health information together in one clean, organized space. No more folders stuffed with papers or photos scattered across devices - everything that matters to your health lives in **MedBook**, neatly structured and always at hand.

Here you will find:
- **Medication Schedule and Daily Reminder** - create a monthly schedule for your medications;
- **Secure Document Vault** - upload all your medical files;
- **Pill Risk Check** - get a check of potential pill risks using your sex, age, and country of origin. 

This repository contains the application code for the MedBook project.
The business documentation lives in a separate repository: [MedBook - business report](https://github.com/unibo-dtm-se-2324-MedBook/report)

---

## Contents
- [Technical Features](#technical-Features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Quality: Tests](#quality-linttypetests)
- [PyPI](#pypi)
- [Releases & Versioning](#releases--versioning)
- [License](#license)

---

## Technical Features
- Расписание приёма лекарств (отметка, напоминания)
- Хранение медицинских документов (Firebase)
- Авторизация пользователя
- Уведомления

## Project Structure
```
.gitattributes
.gitignore
poetry.toml
poetry.lock
pyproject.toml
pytest.ini
LICENSE

.github/

artefact/
├── assets/
├── service/ 
├── ui/
│ └── gui
│   ├── components/
│   └── _master page files_
├── utils/
└── __init__.py

tests/
├── test_model.py
├── unit
└── integration

```

## Architecture
Проект следует принципам **DDD** и **Hexagonal (Ports & Adapters)**:
- **domain/** — сущности, value objects, агрегаты, доменные сервисы, интерфейсы репозиториев.
- **application/** — use-cases (оркестрация доменной логики).
- **infrastructure/** — реализации портов: Firebase/OpenFDA, хранилища, клиенты.
- **ui/** — Flet-интерфейс, компоненты.

**Bounded Contexts**: `auth`, `med_schedule`, `documents`, `notifications`.  
Ключевые инварианты: уникальность слотов приёма, корректность дат/дозировок и т.п.

Poetry is configures in such a way that:

* a virtual environment is created automatically for this project, in the .venv directory
* dependencies are declared in a pyproject.toml file, and installed in the aforementioned environment
* the project can be published on PyPI, with a single command

Requirements
Python 3.11
Kivy 2.3

Development requirements
Coverage.py 7.4.0
Mypy 1.9.0
Pytest 8.1.0
Poetry 1.7.0

## Getting Started
### Download the project
Choose one of the following:
1. Option A — Download ZIP from GitHub
2. Option B — Clone with Git:
```
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
```

### Install Dependencies
1. Poetry will create a virtual environment and install all required packages:
```
poetry install
```
2. Production-only install: no developer tools:
```
poetry install --only main 
```
### Environment Variables (Secrets)
If you received a .env file (e.g., Firebase keys), place it in the project root (next to pyproject.toml).

Provide your environment variables (e.g., Firebase keys) via your platform’s secret manager or a .env file loaded before the app starts. Example variables:
-FIREBASE_API_KEY
-FIREBASE_AUTH_DOMAIN
-FIREBASE_PROJECT_ID
-FIREBASE_STORAGE_BUCKET
-FIREBASE_DB_URL

### Run the application
Use one of the options below:
1) Run by module (recommended fallback)
```
poetry run python -m artefact.ui.gui.main_page
```
2) Run via CLI command
```
poetry run medbook
```
### Tests + coverage
Ковередж уже включен автоматически в ран тестов, поэтому можно сделать просто:
```
poetry run pytest
```
Но если хочется html отчет, то код:
```
```


## Releases & Versioning

Версионирование: SemVer (MAJOR.MINOR.PATCH)

Теги: v0.x.y, GitHub Releases + CHANGELOG

## PyPI


## License

This project is distributed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.  

- You are free to use, modify, and share this code _for non-commercial purposes only_;  
- Attribution is required: _Anastasiia Bakhmutova (2025)_;
- Any commercial use without the author’s prior written permission is _strictly prohibited_.  

[Full license text](./LICENSE)

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
