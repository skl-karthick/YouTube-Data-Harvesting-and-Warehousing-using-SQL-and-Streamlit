
# YouTube-Data-Harvesting-and-Warehousing-using-SQL-and-Streamlit

## 📘 Introduction

This project allows users to collect, store, analyze, and visualize YouTube data using the YouTube Data API. The collected data is stored in a MySQL database, and users can perform various queries and view visualizations through a Streamlit application.

### Domain : 📱 *Social Media*

### 🎨 Skills Takeaway :
__Python scripting, Data Collection, Streamlit, API integration, Data Management using SQL__

### 📘 Overview


### 🌾Data Collection

- Retrieve channel information, video details, playlists, and comments from YouTube.
- Use the YouTube Data API to fetch data.

### 📥 Database Storage

- Store collected data in a MySQL database.
- Use pandas for data transformation.
- Use  MySQL for storing data into database.

### 📊  Data Analysis

- Perform SQL queries on the YouTube channel data stored in the MySQL database.
- Answer specific questions about the YouTube channels using the stored data.

#### 📊 Data Visualization:

- Display visualizations in a Streamlit application.

## Installation

### Requirements

- Python 3.x
- Streamlit
- pandas
- mysql-connector-python

### Setup

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the MySQL database MySQL server. Create the necessary tables using the SQL commands in the `app2.py` script.

4. Get YouTube Data API credentials and set them up in your environment.

## Usage

1. Run the Streamlit application:
    ```sh
    streamlit run app2.py
    ```

2. Enter a YouTube channel ID or name in the input field in the "Data Collection" option from the sidebar menu.

3. Click the "View Details" button to fetch and display channel information.

4. Click the "Upload to MySQL" button to store channel data in the SQL database.


## Code Overview

### `app2.py`

- **Libraries**: Imports various libraries including Streamlit, pandas, mysql-connector-python.
- **Functions**: Defines functions to fetch data from YouTube, store data in MySQL.
- **Streamlit App**: Sets up the Streamlit application layout and user interactions for data collection, storage, analysis, and visualization.

Contact
### LinkedIn:(https://www.linkedin.com/in/karthick-kumar-s-374160241/)
### Email:skl.karthickkrish1996@gmail.com
### Git:(https://github.com/skl-karthick)

