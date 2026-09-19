"""
Wikipedia Dataset Builder - Main Streamlit Application
======================================================
Search Wikipedia, extract article information, preview it in a table
and download the result as a CSV file.

Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from wikipedia_scraper import build_dataset

# -----------------------------------------------------------------
# 1. Page configuration (must be the first Streamlit command)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Wikipedia Dataset Builder",
    page_icon="📚",
    layout="wide",
)

# -----------------------------------------------------------------
# 2. Custom styling - header, cards and topic chip
# -----------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Big gradient header on top of the dashboard */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .main-header p {
        margin: 0.4rem 0 0 0;
        font-size: 1.05rem;
        opacity: 0.9;
    }

    /* Small feature cards on the welcome screen */
    .feature-card {
        background: rgba(37, 99, 235, 0.07);
        border: 1px solid rgba(37, 99, 235, 0.25);
        border-radius: 12px;
        padding: 1.4rem 1rem;
        text-align: center;
        height: 100%;
    }
    .feature-card .icon { font-size: 2rem; }
    .feature-card h3 {
        margin: 0.5rem 0 0.3rem 0;
        font-size: 1.05rem;
    }
    .feature-card p {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.75;
    }

    /* Small rounded chip shown above the results */
    .topic-chip {
        display: inline-block;
        background: rgba(37, 99, 235, 0.12);
        border: 1px solid rgba(37, 99, 235, 0.35);
        border-radius: 999px;
        padding: 0.25rem 0.9rem;
        font-size: 0.95rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 3. Session state - keeps the dataset between user interactions
# -----------------------------------------------------------------
if "dataset" not in st.session_state:
    st.session_state.dataset = None      # DataFrame with the results
if "search_topic" not in st.session_state:
    st.session_state.search_topic = ""   # topic of the last search
if "just_built" not in st.session_state:
    st.session_state.just_built = False  # shows the success message once

DATASET_SIZES = ["5 articles", "10 articles", "20 articles", "50 articles"]

# -----------------------------------------------------------------
# 4. Sidebar - search and settings
# -----------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:0.4rem 0 0.2rem 0;">
            <div style="font-size:2rem;">📚</div>
            <div style="font-weight:700; font-size:1.05rem;">
                Wikipedia Dataset Builder
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### 🔎 Search Wikipedia")
    query = st.text_input(
        "Enter a topic, keyword, or Wikipedia article",
        placeholder="Artificial Intelligence",
    )

    # "10 articles" -> 10 (the number is the first word of the label)
    size_label = st.selectbox("Dataset size", DATASET_SIZES, index=1)
    article_limit = int(size_label.split()[0])

    build_clicked = st.button(
        "🚀 Build Dataset", type="primary", width="stretch"
    )

    st.divider()
    clear_clicked = st.button(
        "🔄 Clear Dataset",
        width="stretch",
        disabled=st.session_state.dataset is None,
    )

# -----------------------------------------------------------------
# 5. Dashboard header (always visible)
# -----------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>📚 Wikipedia Dataset Builder</h1>
        <p>Turn Wikipedia articles into a structured dataset in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------
# 6. Button actions
# -----------------------------------------------------------------
if clear_clicked:
    # Go back to the initial welcome screen
    st.session_state.dataset = None
    st.session_state.search_topic = ""
    st.session_state.just_built = False
    # Rerun so the sidebar immediately shows the disabled Clear button
    st.rerun()

if build_clicked:
    topic = query.strip()

    if not topic:
        st.warning("⚠️ Please enter a topic before building a dataset.")
    else:
        progress_bar = st.progress(0, text="🔎 Searching Wikipedia...")

        def update_progress(current, total, title):
            """Called by the scraper after every article."""
            percent = int(current / total * 100)
            progress_bar.progress(
                percent,
                text=(
                    f"📖 Collecting article information... "
                    f"({current}/{total}) — {title}"
                ),
            )

        connection_problem = False
        try:
            dataset = build_dataset(
                topic, article_limit, progress_callback=update_progress
            )
        except ConnectionError:
            dataset = pd.DataFrame()
            connection_problem = True
            progress_bar.empty()
            st.error(
                "⚠️ Could not connect to Wikipedia. "
                "Please check your internet connection and try again."
            )
        except Exception:
            dataset = pd.DataFrame()
            connection_problem = True
            progress_bar.empty()
            st.error("⚠️ Something went wrong while building the dataset. Please try again.")

        if dataset.empty:
            # Bad topic or no matching articles
            st.session_state.dataset = None
            st.session_state.search_topic = ""
            progress_bar.empty()
            if not connection_problem:
                st.info("⚠️ No Wikipedia articles found. Try another topic.")
        else:
            progress_bar.progress(100, text="🎉 Dataset ready!")
            # Save the result and rerun the app, so the whole page
            # (including the sidebar buttons) shows the new state
            st.session_state.dataset = dataset
            st.session_state.search_topic = topic
            st.session_state.just_built = True
            st.rerun()

# -----------------------------------------------------------------
# 7. Main content
# -----------------------------------------------------------------
if st.session_state.dataset is None:
    # ---------- Welcome screen (no dataset yet) ----------
    st.markdown("## Build Your Wikipedia Dataset")
    st.write(
        "Search Wikipedia topics and automatically convert article "
        "information into a structured dataset."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">📖</div>
                <h3>Wikipedia Articles</h3>
                <p>Find relevant articles for any topic or keyword.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">🔍</div>
                <h3>Automatic Extraction</h3>
                <p>Summaries, categories, links and stats are extracted for you.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon">📊</div>
                <h3>Ready-to-Download Dataset</h3>
                <p>Preview, check the quality and export everything as CSV.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "💡 Tip: type a topic like **Artificial Intelligence** in the sidebar "
        "and press **🚀 Build Dataset**."
    )

else:
    # ---------- Results screen ----------
    dataset_df = st.session_state.dataset
    topic = st.session_state.search_topic

    # One-time success message shown right after building
    if st.session_state.just_built:
        st.success(f"🎉 Dataset ready! {len(dataset_df)} articles collected.")
        st.session_state.just_built = False

    st.markdown(
        f'<span class="topic-chip">🔎 Topic: <b>{topic}</b> — '
        f"{len(dataset_df)} articles</span>",
        unsafe_allow_html=True,
    )

    # ---------- Key metrics ----------
    st.markdown("## 📊 Dataset Preview")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Articles", f"{len(dataset_df):,}")
    metric_cols[1].metric("Columns", dataset_df.shape[1])
    metric_cols[2].metric("Total Words", f"{int(dataset_df['Word Count'].sum()):,}")
    metric_cols[3].metric(
        "Total References", f"{int(dataset_df['References Count'].sum()):,}"
    )

    # ---------- Interactive preview table (width stretches by default) ----------
    st.dataframe(
        dataset_df,
        height=380,
        hide_index=True,
    )

    # ---------- Article details ----------
    with st.expander("🔎 View Article Details"):
        article_titles = dataset_df["Title"].tolist()
        selected_title = st.selectbox("Choose an article", article_titles)
        article = dataset_df[dataset_df["Title"] == selected_title].iloc[0]

        left, right = st.columns([3, 2])

        with left:
            st.subheader(article["Title"])
            if article["Summary"]:
                st.write(article["Summary"])
            else:
                st.write("_No summary available for this article._")

        with right:
            url = article["URL"]
            if url:
                # Markdown link -> the URL becomes clickable
                st.markdown(f"**🔗 Wikipedia URL:** [{url}]({url})")
            else:
                st.markdown("**🔗 Wikipedia URL:** _Not available_")

            categories = article["Categories"]
            if categories:
                st.markdown(f"**🏷️ Categories:** {categories}")
            else:
                st.markdown("**🏷️ Categories:** _None found_")

            st.metric("Word Count", f"{int(article['Word Count']):,}")
            st.metric("References", int(article["References Count"]))

    # ---------- Data quality ----------
    st.markdown("## ✅ Dataset Quality")

    # Empty cells count as missing values
    missing_values = int(
        dataset_df.isna().sum().sum() + (dataset_df == "").sum().sum()
    )
    duplicate_rows = int(dataset_df.duplicated().sum())

    quality_cols = st.columns(4)
    quality_cols[0].metric("Total Rows", len(dataset_df))
    quality_cols[1].metric("Columns", dataset_df.shape[1])
    quality_cols[2].metric("Missing Values", missing_values)
    quality_cols[3].metric("Duplicate Rows", duplicate_rows)

    if missing_values == 0:
        st.success("Excellent! No missing values found.")
    else:
        st.warning(f"⚠️ {missing_values} missing value(s) found in the dataset.")

    if duplicate_rows == 0:
        st.success("No duplicate rows found.")
    else:
        st.warning(f"⚠️ {duplicate_rows} duplicate row(s) found.")

    # ---------- Download ----------
    st.markdown("## ⬇️ Download")

    # utf-8-sig makes the file open nicely in Excel as well
    csv_bytes = dataset_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Download Dataset (CSV)",
        data=csv_bytes,
        file_name="wikipedia_dataset.csv",
        mime="text/csv",
        type="primary",
        width="stretch",
    )

# -----------------------------------------------------------------
# 8. Footer
# -----------------------------------------------------------------
st.divider()
st.caption("Data source: Wikipedia (MediaWiki API) · Built with Streamlit & Pandas")
