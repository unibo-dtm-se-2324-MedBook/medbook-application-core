# MedBook

Кросс-платформенное Flet-приложение для ведения медицинских записей: расписание лекарств, документы, уведомления.
This repository contains the code of your project work

## Contents
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Quality: Lint/Type/Tests](#quality-linttypetests)
- [Releases & Versioning](#releases--versioning)
- [Contributing](#contributing)
- [License](#license)

## Features
- Расписание приёма лекарств (отметка, напоминания)
- Хранение медицинских документов (Firebase)
- Авторизация пользователя
- Уведомления

## Project Structure
artefact/
  domain/
  application/
  infrastructure/
  ui/
    gui/
      components/
    cli/
tests/
.github/
pyproject.toml

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
```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
```

### Install Dependencies
1. Poetry will create a virtual environment and install all required packages:
```bash
poetry install
```
2. Production-only install: no developer tools:
```bash
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
```bash
poetry run python -m artefact.ui.gui.main_page
```
2) Run via CLI command
```bash
poetry run medbook
```
### Tests + coverage
Ковередж уже включен автоматически в ран тестов, поэтому можно сделать просто:
```bash
poetry run pytest
```
Но если хочется html отчет, то код:
```bash
```


## Releases & Versioning

Версионирование: SemVer (MAJOR.MINOR.PATCH)

Теги: v0.x.y, GitHub Releases + CHANGELOG


## 📜 License

This project is distributed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.  

- You are free to use, modify, and share this code **for non-commercial purposes only**;  
- Attribution is required: **Anastasiia Bakhmutova (2025)**;
- Any commercial use without the author’s prior written permission is **strictly prohibited**.  

[Full license text](./LICENSE)

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
