# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bayesian animal disease diagnosis REST API. Given an animal species and observed clinical signs, it calculates posterior probabilities for diseases using Bayes' theorem. Disease/sign likelihood data is stored in an Excel workbook (`data.xlsx`).

## Commands

```bash
# Run the API (serves on port 5000, Swagger UI at root)
python flask_app.py

# Run all unit tests
python -m unittest test_helper

# Run a single test class
python -m unittest test_helper.TestCalculateResults

# Install dependencies
pip install -r requirements.txt
```

## Architecture

- **flask_app.py** — App factory and API initialization. Registers two Flask-RESTx namespaces.
- **diagnosis_controller.py** — `/diagnosis/` namespace. POST endpoints for running Bayesian diagnoses (standard and custom).
- **data_controller.py** — `/data/` namespace. GET endpoints for retrieving animal/sign/disease reference data.
- **diagnosis_helper.py** — All business logic: validation, Bayesian calculation (`calculate_results`), normalization, and Excel data extraction.
- **helper_tests.py** — Unit tests (14 tests across 5 classes) covering validation, calculation, and normalization.
- **data.xlsx** — Source of truth. Each animal species has three sheets: main likelihood matrix, `_Abbr` (sign terminology + WikiData IDs), `_Codes` (disease WikiData IDs).

## Key Domain Concepts

- **Signs** have three states: `1` (present), `0` (not observed), `-1` (absent). The calculation handles each differently.
- **Priors** must sum to 100 and cover all diseases for the animal. If omitted, equal priors are generated.
- **Likelihoods** must be between 0 and 1 (exclusive).
- Valid animals: Cattle, Sheep, Goat, Camel, Horse, Donkey (case-insensitive input, capitalized internally).

## Tech Stack

Python 3.10, Flask, Flask-RESTx (Swagger docs), Flask-CORS, OpenPyXL.
