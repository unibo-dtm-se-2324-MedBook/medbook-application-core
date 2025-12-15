# MedBook - Your Personal Medical Hub

MedBook is a privacy-first mobile app that brings all your health information together in one clean, organized space. No more folders stuffed with papers or photos scattered across devices - everything that matters to your health lives in **MedBook**, neatly structured and always at hand.

Here you will find:
- **Medication Schedule and Daily Reminder** - create a monthly schedule for your medications;
- **Secure Document Vault** - upload all your medical files;
- **Pill Risk Check** - get a check of potential pill risks using your sex, age, and country of origin. 

This repository contains the application code for the MedBook project.
The business documentation lives in a separate repository: [MedBook - business report](https://github.com/unibo-dtm-se-2324-MedBook/medbook-business-report)

---

## Contents
- [Technical Features](#technical-Features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Testing and Code Coverage](#testing-and-code-coverage)
- [Available on PyPI and GitHub](#available-on-pypi-and-gitHub)
- [License](#license)

---

## Technical Features
Built a full‑stack, multi‑page application with routed pages using Python and Flet front-end:
- User authentication system using Firebase Authentication;
- Interactive medication schedule using the cloud‑based Realtime Database;
- Daily Reminder at 06:00: timetable triggers in‑app and push reminders;
- Document Storage using Firebase Storage to upload and retrieval of lab results and prescriptions;
- Pill Risk Check: call a third‑party medical API (OpenFDA API) to flag contraindications. 

In the project Poetry is used to configure in such a way that:
* a virtual environment is created automatically;
* dependencies are declared in a pyproject.toml file, and installed in the aforementioned environment;
* the project can be published on PyPI, with a single command.

## Requirements
```
Python = ">=3.12,<4.0"
Poetry >= "2.0.0,<3.0.0"

dependencies = [
	"flet==0.25.2",
	"pyrebase4==4.8.0",
	"firebase-admin==6.6.0",
	"setuptools (>=80.9.0,<81.0.0)"
]
dev.dependencies = [
	pytest = "^8.1.0"
	coverage = "^7.4.0"
	pytest-cov = "^7.0.0"
]
```
---

## Project Structure
```
.gitattributes
.gitignore
poetry.toml          # Poetry configuration
poetry.lock
pyproject.toml       # Project manifest
pytest.ini           # Pytest configuration
LICENSE

.github/             # CI workflows

artefact/                     # Folder with artefact code
├── assets/                   # Static files: images, icons, fonts, etc
├── service/                  # Backend-facing services (Firebase auth, Storage, DataBase, external APIs, etc)
├── ui/
│ └── gui                     # GUI implementation
│   ├── components/           # Reusable UI widgets (header, navigation bar)
│   └── _master page files_   # Page screens (LoginPage, SettingsPage, etc)
├── utils/                    # Helpers & utilities (validation, constants, formatting)
└── __init__.py

tests/               # Folder with tests
├── test_model.py
└── unit/            # Folder with unit-tests

```
---

## Getting Started
### Download the project
Choose one of the following:
1. Option A — Download ZIP from GitHub
2. Option B — Clone with Git:
```
git clone https://github.com/unibo-dtm-se-2324-MedBook/medbook-application-core.git
cd medbook-application-core
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
To run the application end to end, you need:
* a Firebase project (create _Realtime Database, Authentication, and Storage_)
* configure the required secrets as environment variables, such as _Firebase admin key_, _Firebase key_, _Firebase service account_.

### Run the application
Use one of the options below:
1) Run by module
```
poetry run python artefact/__init__.py
```
2) Run via CLI command
```
poetry run medbook
```
---

## Testing and Code Coverage
This project includes a comprehensive unit test suite with a current code coverage of ~81%.
A textual coverage summary is printed automatically when running the standard test task:
```
poetry run pytest
```
 To generate an HTML coverage report, use the next code line:
```
poetry run pytest --cov=artefact --cov-report=term-missing --cov-report=html
```

## Available on PyPI and GitHub

This project’s source code is hosted on GitHub, and a packaged release is also published on PyPI.
- **PyPI (package)**: [medbook-medical-hub](https://pypi.org/project/medbook-medical-hub/)  
  *Note:* the PyPI source distribution excludes the test suite to keep the package lightweight.
- **GitHub (full source with tests)**: [MedBook](https://github.com/unibo-dtm-se-2324-MedBook/medbook-application-core)

## License

This project is distributed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.  

- You are free to use, modify, and share this code _for non-commercial purposes only_;  
- Attribution is required: _Anastasiia Bakhmutova (2025)_;
- Any commercial use without the author’s prior written permission is _strictly prohibited_.  

[Full license text](./LICENSE)

![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
