import requests
from bs4 import BeautifulSoup
import csv

def scrape_jobs(base_url, output_filename):
    # Initialize a list to store job data
    all_job_data = []

    page_number = 1  # Start from the first page
    while True:
        # Construct the page URL
        url = base_url + str(page_number)

        # Send a GET request to the webpage
        response = requests.get(url)

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all job title elements
        job_elements = soup.find_all('h6', class_='job-title ab-title-placeholder ab-cb-title-placeholder')
        
        # If no job elements are found, break the loop (no more pages)
        if not job_elements:
            break

        job_titles = [job.get_text(strip=True) for job in job_elements]

        # Find all company name elements
        company_elements = soup.find_all('span', class_='company-name')
        company_names = [company.get_text(strip=True) for company in company_elements]

        # Find all posted date elements
        date_elements = soup.find_all('span', class_='date date-with-icon')
        posted_dates = [date.get_text(strip=True) for date in date_elements]

        # Find all tech stack elements
        tech_stack_elements = soup.find_all('div', class_='tech-stack-wrap hide-for-small')
        tech_stacks = []
        for stack in tech_stack_elements:
            tech_items = stack.find_all('img')
            tech_stack = [item['title'] for item in tech_items if 'title' in item.attrs]
            tech_stacks.append(", ".join(tech_stack))

        # Combine the data into rows and add to all_job_data list
        all_job_data.extend(zip(job_titles, company_names, posted_dates, tech_stacks))

        # Move to the next page
        page_number += 1

    # Save all job data to a CSV file
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Job Title', 'Company Name', 'Posted Date', 'Tech Stack'])
        writer.writerows(all_job_data)

    print(f"Job data has been saved to '{output_filename}'")
