# 📚 Wikipedia Dataset Builder

**Turn Wikipedia articles into a structured dataset in seconds.**

A beginner-friendly web app built with Python and Streamlit.

## What it does

Enter any topic (for example *Artificial Intelligence*) and the app will:

1. Search Wikipedia for relevant articles
2. Extract key information from each article (summary, categories, URL, word count, references)
3. Show the results in an interactive table with quality checks
4. Let you download everything as a CSV file, ready for data analysis

## Features

- 🔎 **Wikipedia search** — find up to 5, 10, 20 or 50 articles for any topic
- 🤖 **Automatic data extraction** — summaries, categories, URLs, word counts and reference counts
- 📊 **Dataset preview** — interactive table with key metrics (articles, words, references)
- 🔎 **Article details** — inspect any single article, with a clickable Wikipedia link
- ✅ **Data quality analysis** — rows, columns, missing values and duplicates at a glance
- ⬇️ **CSV download** — export the dataset as `wikipedia_dataset.csv`
- 🛡️ **Friendly error handling** — invalid topics or connection problems never crash the app

## Technologies

- **Python** — core language
- **Streamlit** — web interface
- **Pandas** — dataset creation and analysis
- **Requests** — talking to the Wikipedia API
- **Wikipedia API** (MediaWiki Action API) — article search and data

## How to run

1. Make sure Python 3.9 or newer is installed.

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the link shown in the terminal (usually http://localhost:8501).

## Example

1. Type **Artificial Intelligence** in the sidebar search box.
2. Choose **10 articles** as the dataset size.
3. Click **🚀 Build Dataset** and watch the progress bar.
4. Explore the preview table, the article details and the quality report.
5. Click **⬇️ Download Dataset (CSV)** to save `wikipedia_dataset.csv`.

The resulting CSV contains one row per article with the columns:

`Title, URL, Summary, Categories, Word Count, References Count`

## Project structure

```
wikipedia-dataset-builder/
├── app.py                # Streamlit web interface
├── wikipedia_scraper.py  # Wikipedia search and data extraction
├── requirements.txt      # Python dependencies
└── README.md             # This file
```
