import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import datetime
from scrapper import scrape_jobs  # Import the scrape_jobs function from scrapper.py

# Function to handle Bulgarian dates and format as YYYY-MM-DD
def parse_bulgarian_date(date_str):
    # Bulgarian to English month mappings
    months_bg_to_en = {
        "ян.": "Jan", "фев.": "Feb", "март": "Mar", "апр.": "Apr", 
        "май": "May", "юни": "Jun", "юли": "Jul", "авг.": "Aug", 
        "сеп.": "Sep", "окт.": "Oct", "ноем.": "Nov", "дек.": "Dec"
    }
    
    # Replace Bulgarian month names with English equivalents
    for bg_month, en_month in months_bg_to_en.items():
        date_str = date_str.replace(bg_month, en_month)
    
    # Add the current year to the date for parsing purposes
    current_year = datetime.datetime.now().year
    date_str = f"{date_str} {current_year}"
    
    # Convert to datetime format
    parsed_date = pd.to_datetime(date_str, format="%d %b %Y", errors='coerce')
    
    # Return the date in "YYYY-MM-DD" format if parsed successfully
    return parsed_date.strftime('%Y-%m-%d') if not pd.isna(parsed_date) else None

# Usage in the load_data function
@st.cache_data
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    # Apply the updated date parsing function to the 'Posted Date' column
    data['Posted Date'] = data['Posted Date'].apply(parse_bulgarian_date)
    return data

# Sidebar filters
def add_filters(data):
    st.sidebar.header("Filter Options")
    
    # Job Title filter
    job_title_filter = st.sidebar.text_input("Search by Job Title")
    
    # Company filter
    company_filter = st.sidebar.selectbox("Select Company", ["All"] + list(data['Company Name'].unique()))

    # Start date filter
    start_date_filter = st.sidebar.date_input("Start Date", value=datetime.date(2024, 1, 1))
    
    # End date filter
    end_date_filter = st.sidebar.date_input("End Date", value=datetime.date(2024, 12, 31))
    
    # Tech Stack filter
    tech_stack_filter = st.sidebar.multiselect("Select Tech Stack", data['Tech Stack'].str.split(', ').explode().unique())
    
    # Apply filters
    if job_title_filter:
        data = data[data['Job Title'].str.contains(job_title_filter, case=False)]
    if company_filter != "All":
        data = data[data['Company Name'] == company_filter]
    if tech_stack_filter:
        data = data[data['Tech Stack'].apply(lambda x: any(stack in x for stack in tech_stack_filter))]
    
    return data

# Function to scrape jobs for a specific category
def scrape_jobs_for_category(selected_category, selected_csv):
    job_categories = {
        "Backend": "https://dev.bg/company/jobs/back-end-development/sofiya/?_job_location=sofiya&_paged=",
        "Frontend": "https://dev.bg/company/jobs/front-end-development/sofiya/?_job_location=sofiya&_paged=",
        "Fullstack": "https://dev.bg/company/jobs/full-stack-development/sofiya/?_job_location=sofiya&_paged=",
        "Pm_ba": "https://dev.bg/company/jobs/pm-ba-and-more/sofiya/?_job_location=sofiya&_paged=",
        "Quality_assurance": "https://dev.bg/company/jobs/quality-assurance/sofiya/?_job_location=sofiya&_paged=",
        "Infrastructure": "https://dev.bg/company/jobs/operations/sofiya/?_job_location=sofiya&_paged=",
        "Data_science": "https://dev.bg/company/jobs/data-science/sofiya/?_job_location=sofiya&_paged=",
        "Ui_ux_arts": "https://dev.bg/company/jobs/ui-ux-and-arts/sofiya/?_job_location=sofiya&_paged=",
        "Technical_support": "https://dev.bg/company/jobs/technical-support/sofiya/?_job_location=sofiya&_paged="
    }

    # Scrape job data for the selected category
    url = job_categories[selected_category]
    scrape_jobs(url, selected_csv)

# Function to scrape all categories on startup or restart
def scrape_and_create_csvs():
    job_categories = {
        "backend": "https://dev.bg/company/jobs/back-end-development/sofiya/?_job_location=sofiya&_paged=",
        "frontend": "https://dev.bg/company/jobs/front-end-development/sofiya/?_job_location=sofiya&_paged=",
        "fullstack": "https://dev.bg/company/jobs/full-stack-development/sofiya/?_job_location=sofiya&_paged=",
        "pm_ba": "https://dev.bg/company/jobs/pm-ba-and-more/sofiya/?_job_location=sofiya&_paged=",
        "quality_assurance": "https://dev.bg/company/jobs/quality-assurance/sofiya/?_job_location=sofiya&_paged=",
        "infrastructure": "https://dev.bg/company/jobs/operations/sofiya/?_job_location=sofiya&_paged=",
        "data_science": "https://dev.bg/company/jobs/data-science/sofiya/?_job_location=sofiya&_paged=",
        "ui_ux_arts": "https://dev.bg/company/jobs/ui-ux-and-arts/sofiya/?_job_location=sofiya&_paged=",
        "technical_support": "https://dev.bg/company/jobs/technical-support/sofiya/?_job_location=sofiya&_paged="
    }

    # Scrape jobs for all categories
    for category, url in job_categories.items():
        csv_file = f'{category}_jobs.csv'
        scrape_jobs(url, csv_file)

# Main app function
def main():
    st.title("Job Scraping Dashboard")

    # Check if CSV files exist, and run the scraper if not
    if not any(f.endswith('_jobs.csv') for f in os.listdir('.')):
        st.write("No CSV files found. Scraping data on first startup...")
        scrape_and_create_csvs()

    # List all available CSV files in the current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('_jobs.csv')]
    job_categories = {f.replace('_jobs.csv', '').capitalize(): f for f in csv_files}

    # Dropdown menu to select a job category
    selected_category = st.sidebar.selectbox("Select Job Category", list(job_categories.keys()))

    # Load the corresponding CSV file
    selected_csv = job_categories[selected_category]
    data = load_data(selected_csv)

    # Button to scrape data for the selected category
    if st.button("Scrape New Job Data"):
        scrape_jobs_for_category(selected_category, selected_csv)
        data = load_data(selected_csv)  # Reload the data after scrapping
    
    # Apply filters
    filtered_data = add_filters(data)

    # Check if search results are empty
    if filtered_data.empty:
        st.write(f"No job offers found matching your search in {selected_category}.")
    else:
        # Show filtered data in a table
        st.write(f"Showing {len(filtered_data)} job offers for {selected_category}:")
        st.dataframe(filtered_data)

        # Bar chart: Number of jobs per company (limit to top N companies)
        st.subheader(f"Top Companies by Job Offers in {selected_category}")

        # Limit to top N companies, e.g., top 10
        top_n = 10
        job_counts = filtered_data['Company Name'].value_counts().nlargest(top_n)

        # Check if job_counts is empty
        if job_counts.empty:
            st.write(f"No job data available for {selected_category}.")
        else:
            # Create the interactive Plotly bar chart
            fig = px.bar(
                job_counts,
                x=job_counts.index,
                y=job_counts.values,
                labels={'x': 'Company Name', 'y': 'Number of Jobs'},
                text=job_counts.values  # Add job counts as text on the bars
            )

            # Customize the layout to place the text inside the bars
            fig.update_traces(texttemplate='%{text}', textposition='auto')
            fig.update_layout(
                xaxis_tickangle=-45,  # Rotate the x-axis labels
                height=500,           # Adjust height of the chart
                title=f"Top Companies by Job Offers in {selected_category}",
            )

            # Display the Plotly figure
            st.plotly_chart(fig)

        # Pie chart: Tech Stack distribution (limit to top N tech stacks)
        st.subheader(f"Top Tech Stack Distribution in {selected_category}")

        # Limit to top N tech stacks, e.g., top 10
        tech_counts = filtered_data['Tech Stack'].str.split(', ').explode().value_counts().nlargest(top_n)

        # Check if tech_counts is empty
        if tech_counts.empty:
            st.write(f"No tech stack data available for {selected_category}.")
        else:
            fig, ax = plt.subplots()
            ax.pie(tech_counts, labels=tech_counts.index, autopct='%1.1f%%', startangle=30)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            st.pyplot(fig)

if __name__ == "__main__":
    main()
