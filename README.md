# UPSC PYQ Scraper

Simple Streamlit app to fetch UPSC prelims PYQs by subject and year from SuperKalam and export them as a Word document.

## Features

- Select subject and year from UI
- Fetch questions with options, answer and explanation
- Preview inside app
- Download as `.docx`
- Auto-save local copy in `output/<subject>/<year>.docx`

## Project Files

- `app.py` - Streamlit app
- `scraper.py` - Fetch + parse logic
- `batch_scrape.py` - optional CLI script for multiple years/subjects

## Setup

1. Create virtual environment:

```powershell
python -m venv venv
```

2. Activate:

```powershell
.\venv\Scripts\activate
```

3. Install packages:

```powershell
pip install -r requirements.txt
```

4. Run app:

```powershell
streamlit run app.py
```

## Notes

- If Word export fails due to bad characters from source text, the app already cleans invalid XML characters.

