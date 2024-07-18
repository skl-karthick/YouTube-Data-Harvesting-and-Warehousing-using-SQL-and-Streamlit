# import visualization tools 
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu


# integrate and utilize Google services in your Python applications effectively
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Convert datetime into iso date formate 
from datetime import datetime

# Duration from ISO 8601 format
import re

#import mysql tools from 
import mysql.connector
import pandas as pd


#Example ISO date string
iso_date_str = "2024-06-08T12:34:56Z"
iso_date = datetime.fromisoformat(iso_date_str.replace("Z", "+00:00"))
sql_date_str = iso_date.strftime('%Y-%m-%d %H:%M:%S')

# Function to connect to YouTube API
def api_connect():
    api_service_name = "youtube"
    api_version = "v3"
    api_id = "AIzaSyAqotxMlAs5duOxhm_tObZUX4VHlt6_8Ic"
    youtube = build(api_service_name, api_version, developerKey=api_id)
    return youtube

youtube = api_connect()

# Function to Retrieve channel information from Youtube;
def get_channel_info(channel_id):
    try:
        request=youtube.channels().list(
                                    part="snippet,contentDetails,statistics",
                                    id=channel_id
                                    )
        response=request.execute()

        for i in response["items"]:
            channel_data=dict(
                    channel_Name=i["snippet"]["title"],
                    Channel_Id=i["id"],
                    Channel_Description=i["snippet"]["description"],
                    Channel_Thumbnail=i['snippet']['thumbnails']['default']['url'],
                    Channel_Playlist_id=i["contentDetails"]["relatedPlaylists"]["uploads"],
                    Channel_Subscribers=i["statistics"]["subscriberCount"],
                    Channel_View_Count=i["statistics"]["viewCount"],
                    Channel_Video_count=i["statistics"]["videoCount"],
                    Channel_publishedat=i['snippet']['publishedAt'])

            return channel_data
    except HttpError as e:
        if e.resp.status == 403 and 'quotaExceeded' in str(e):
            print("Quota exceeded. Please try again later.")
        else:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    
#Function to Retrieve video information of all video IDS from Youtube
def get_video_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
                                    part="contentDetails").execute()
    Playlist_Id=response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    next_page_token=None
    while True:
        respose1=youtube.playlistItems().list(
                                                part="snippet",
                                                playlistId=Playlist_Id,
                                                maxResults=50,
                                                pageToken=next_page_token,
                                                ).execute()
        for i in range(len(respose1["items"])):
                video_ids.append(respose1["items"][i]["snippet"]["resourceId"]["videoId"])
        next_page_token=respose1.get("nextPageToken")
        if next_page_token is None:
            break  
    return  video_ids


#Function to convert Duration from ISO 8601 format to HH:MM:SS format;
def convert_duration(duration):
    regex = r'PT(\d+H)?(\d+M)?(\d+S)?'
    match = re.match(regex, duration)
    if not match:
            return '00:00:00'
    hours, minutes, seconds = match.groups()
    hours = int(hours[:-1]) if hours else 0
    minutes = int(minutes[:-1]) if minutes else 0
    seconds = int(seconds[:-1]) if seconds else 0
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60), int(total_seconds % 60))


def get_video_info(video_ids):
    video_data = []
    for video_id in video_ids:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()

        for item in response.get("items", []):
            data = {
                "Channel_Id": item["snippet"]["channelId"],
                "Video_Id": item["id"],
                "Video_Name": item["snippet"]["title"],
                "Video_Description": item["snippet"]["description"],
                "Video_Thumbnails": item["snippet"]["thumbnails"]["default"]["url"],
                "Video_Tags": ",".join(item["snippet"].get("tags", ["na"])),
                "Video_PublishedAt": item["snippet"]["publishedAt"],
                "Video_Duration": convert_duration(item["contentDetails"]["duration"]),
                "Video_ViewCount": item["statistics"].get("viewCount"),
                "Video_LikeCount": item["statistics"].get("likeCount"),
                "Video_FavoriteCount": item["statistics"].get("favoriteCount"),
                "Comment_Count": item["statistics"].get("commentCount"),
                "Caption": item["contentDetails"]["caption"]
            }
            video_data.append(data)
    return video_data 

#Function to get playlist information
def get_playlist_ids(channel_id):
    next_page_token = None
    all_data = []
    try:
        while True:
            request = youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                data = dict(
                    Playlist_Id=item["id"],
                    Playlist_name=item["snippet"]["title"],
                    channel_id=item["snippet"]["channelId"],
                    channel_name=item["snippet"]["channelTitle"],
                    videos_count=item["contentDetails"]["itemCount"]
                )
                all_data.append(data)

            next_page_token = response.get("nextPageToken")
            if next_page_token is None:
                break

    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    return all_data 




# Function to retrieve comment information from YouTube
def get_comment_info(video_ids):
    comment_data = []
    
    for video_id in video_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response = request.execute()

            for item in response["items"]:
                snippet = item["snippet"]
                top_comment = snippet["topLevelComment"]["snippet"]
                data = {
                    "Comment_id": item["id"],
                    "Video_id": snippet["videoId"],
                    "Comment_Text": top_comment["textDisplay"],
                    "Comment_Author": top_comment["authorDisplayName"]
                }
                comment_data.append(data)
        
        except:
            pass
            
    
    return comment_data

# Establish a connection to the MySQL database
db = mysql.connector.connect(host="localhost", user="root", password="krish5935",autocommit=True)
cursor = db.cursor(buffered=True)
cursor.execute('CREATE DATABASE IF NOT EXISTS s1')
cursor.execute('USE s1')

# Setting up the Streamlit sidebar menu with options
with st.sidebar:
    selected = st.selectbox(
        "Main Menu",
        ["Home", "Channel Information", "Upload to MySQL Database", "Analysis Using SQL","Conclusion"]
    )

# Setting up the options for "Home" in Streamlit page
if selected == "Home":
    st.title(':red[You]Tube:blue[Data Harvesting & Warehousing using SQL]')
    st.write("Welcome to the YouTube Data Harvesting and Warehousing application!")
    st.subheader(':blue[Domain:] Social Media')
    st.subheader(':blue[Overview:]')
    st.markdown('''
        Create a dashboard with Streamlit to fetch YouTube channel data via the YouTube API.
        Store this data in a MySQL database for efficient querying and visualization within the App.
    ''')
    st.subheader(':blue[Skill Take Away:]')
    st.markdown('''
        - Python scripting using pandas.
        - Youtube Data Collection [accuracy, completeness, reliability of gathered information through rigorous verification against predefined benchmarks and quality standards]
        - Data migration using a SQL database [Data Migration Overview, Process Description, Schema Mapping, Transformation and Cleaning, Validation and Testing]
        - Streamlit application for visualizations.
    ''')
    st.subheader(':blue[About:]')
    st.markdown('''

    Hello! I'm Karthick Kumar, a B.E graduate in Electronics and Communication Engineering
    with 2.5 years of experience in the healthcare sector. I have since transitioned into 
    the data analytics domain, driven by a strong passion for data science. Currently, 
    I am embarking on an exciting journey into this field. My project, titled "YouTube Data Harvesting and Warehousing
    using SQL," marks my initial foray into data science. Through this project, I have explored the extensive world of 
    YouTube data to extract valuable insights. This experience has fueled my enthusiasm for data-driven decision-making 
    and significantly enhanced my proficiency in data extraction techniques and database management.
    ''')
    st.subheader(':blue[Contact:]')
    st.markdown('''
        - LinkedIn:https://www.linkedin.com/in/karthick-kumar-s-374160241/
        - Email: skl.karthickkrish1996@gmail.com
        - Github:https://github.com/skl-karthick
        -                         
    ''')
# Channel Information page
if selected == "Channel Information":
    st.subheader(':blue[Channel Information]')
    st.markdown('''
        - Provide channel ID in the input field.
        - Clicking 'View Details' will display an overview of the YouTube channel.
        - Clicking 'Upload to MySQL database' will store the extracted information.
    ''')
    st.markdown('''
        :red[note:] ***You can get the channel ID:***
        Open YouTube -> Go to any channel -> Go to About -> Share Channel -> Copy the Channel ID
    ''')
    
    channel_ID = st.text_input("**Enter the channel ID below:**")
    
    if st.button("View Details"):
        with st.spinner('Extraction in progress...'):
            extracted_details = get_channel_info(channel_id=channel_ID)
            try:
                extracted_details = get_channel_info(channel_id=channel_ID)
                st.write('Verify if you have chosen the correct channel ID')
                st.write('**:blue[Channel_Thumbnail]**:')
                st.image(extracted_details['Channel_Thumbnail'])
                st.write('**:blue[Channel Name]**:', extracted_details['channel_Name'])
                st.write('**:blue[Description]**:', extracted_details['Channel_Description'])
                st.write('**:blue[Total Videos]**:', extracted_details['Channel_Video_count'])
                st.write('**:blue[Subscriber Count]**:', extracted_details['Channel_Subscribers'])
                st.write('**:blue[Total Views]**:', extracted_details['Channel_View_Count'])
            except HttpError as e:
                if e.resp.status == 403 and e.error_details[0]["reason"] == 'quotaExceeded':
                    st.error("API Quota exceeded. Please try again later.")
            except:
                st.error("Please ensure to provide a valid channel ID")

# Setting up the options for "Upload to MySQL Database" in Streamlit page
if selected == "Upload to MySQL Database":
    st.subheader(':blue[Upload Channel, Playlist, Videos, and Comments Information to MySQL Database]')
    st.markdown('''
        - Provide the channel ID in the input field below.
        - Clicking 'Upload to MySQL Database' will store the extracted channels, playlists, videos, and comments in the MySQL database.
    ''')
    channel_ID = st.text_input("**Enter the channel ID in the box below:**")

    if st.button("Upload to MySQL Database"):
        with st.spinner('Upload in progress...'):
            cursor = db.cursor()
            try:
                # Creating channel table in SQL database
                create_query = '''
                    CREATE TABLE IF NOT EXISTS channels (
                    channel_Name VARCHAR(255),
                    channel_id VARCHAR(255),
                    channel_description TEXT,
                    channel_thumbnail TEXT,
                    channel_playlist_id VARCHAR(255),
                    channel_subscribers INT,
                    channel_view_count INT,
                    channel_video_count INT,
                    Channel_publishedat datetime
                    )
                '''   
                cursor.execute(create_query)

                # Get channel information
                channel_info = get_channel_info(channel_id=channel_ID) 
                # Create a DataFrame
                ch_df = pd.DataFrame([channel_info])
                st.dataframe(ch_df)
                # Insert channel information into the table
                for index, row in ch_df.iterrows():
                    sql = '''
                        INSERT IGNORE INTO channels (
                            channel_Name,
                            Channel_Id,
                            Channel_Description,
                            Channel_Thumbnail,
                            channel_playlist_id,
                            Channel_Subscribers,
                            Channel_View_Count,
                            Channel_Video_count,
                            Channel_publishedat
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    val = (
                        row["channel_Name"],
                        row["Channel_Id"],
                        row["Channel_Description"],
                        row["Channel_Thumbnail"],
                        row["Channel_Playlist_id"],
                        row["Channel_Subscribers"],
                        row["Channel_View_Count"],
                        row["Channel_Video_count"],
                        row["Channel_publishedat"]
                    )
                    cursor.execute(sql, val)
                    st.success('Channel information uploaded successfully.')
                    print('Channel information uploaded successfully.')

            except Exception as e:
                st.error(f'An error occurred: {e}')

        cursor = db.cursor() 

        try:   
            # Creating playlist table in SQL database 
            create_query = '''
                CREATE TABLE IF NOT EXISTS playlist (
                    Playlist_id VARCHAR(255),
                    Playlist_name VARCHAR(255),
                    channel_id VARCHAR(255),
                    channel_name VARCHAR(255),
                    videos_count INT
                )
            '''
            cursor.execute(create_query)

            # Get playlist information
            playlist_info = get_playlist_ids(channel_id=channel_ID) 

            # Create a DataFrame
            pl_df = pd.DataFrame(playlist_info)
            st.dataframe(pl_df)
            # Insert data into the table
            for i, row in pl_df.iterrows():
                query = '''
                    INSERT IGNORE INTO playlist (
                        Playlist_Id,
                        Playlist_name,
                        channel_id,
                        channel_name,
                        videos_count
                    ) VALUES (%s, %s, %s, %s, %s)
                    '''
                values = (
                    row["Playlist_Id"],
                    row["Playlist_name"],
                    row["channel_id"],
                    row["channel_name"],
                    row["videos_count"])
                cursor.execute(query, values)
            st.success('Playlist information uploaded successfully.')
            print('Playlist information uploaded successfully.')

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            db.rollback()

        cursor = db.cursor()

        try:
            # Creating the Video table in the SQL database
            create_query = '''
            CREATE TABLE IF NOT EXISTS Videos(
                Channel_Id VARCHAR(255),
                Video_Id VARCHAR(255),
                Video_Name VARCHAR(255),
                Video_Description TEXT,
                Video_Thumbnails TEXT,
                Video_Tags TEXT,
                Video_PublishedAt DATETIME,
                Video_Duration TIME,
                Video_ViewCount INT,
                Video_LikeCount INT,
                Video_FavoriteCount INT,
                Comment_Count INT,
                Caption VARCHAR(250)
            )
            '''
            cursor.execute(create_query)

            # Getting video_ids from channel_id
            video_ids = get_video_ids(channel_id=channel_ID)
            # Get video information
            videos_info = get_video_info(video_ids)

            # Create a DataFrame
            vi_df = pd.DataFrame(videos_info)
            st.dataframe(vi_df)

            # Insert data into the table
            for i, row in vi_df.iterrows():
                query = '''
                INSERT IGNORE INTO Videos(
                    Channel_Id,
                    Video_Id,
                    Video_Name,
                    Video_Description,
                    Video_Thumbnails,
                    Video_Tags,
                    Video_PublishedAt,
                    Video_Duration,
                    Video_ViewCount,
                    Video_LikeCount,
                    Video_FavoriteCount,
                    Comment_Count,
                    Caption
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                values = (
                    row["Channel_Id"],
                    row["Video_Id"],
                    row["Video_Name"],
                    row["Video_Description"],
                    row["Video_Thumbnails"],
                    row["Video_Tags"],
                    row["Video_PublishedAt"],
                    row["Video_Duration"],
                    row["Video_ViewCount"],
                    row["Video_LikeCount"],
                    row["Video_FavoriteCount"],
                    row["Comment_Count"],
                    row["Caption"]
                )
                cursor.execute(query, values)
            st.success('Videos information uploaded successfully.')
            print('Videos information uploaded successfully.')

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            db.rollback()

        # Creating comments table in SQL database 
        cursor = db.cursor()

        try:
            create_query = '''
            CREATE TABLE IF NOT EXISTS comments (
                    Comment_id VARCHAR(255),
                    Video_id VARCHAR(255),
                    Comment_Text TEXT,
                    Comment_Author VARCHAR(255)
                )
            '''
            cursor.execute(create_query)  

            # Getting video_id form channel_id
            comment_ids = get_video_ids(channel_id=channel_ID)
            # Get channel information
            comment_info = get_comment_info(video_ids)

            # Create a DataFrame
            cm_df = pd.DataFrame(comment_info)
            st.dataframe(cm_df)

            # Inserting data into the comments table
            for i, row in cm_df.iterrows():
                query = '''
                INSERT IGNORE INTO comments (
                    Comment_id,
                    Video_id,
                    Comment_Text,
                    Comment_Author)
                VALUES (%s, %s, %s, %s)
                '''
                values = (
                        row["Comment_id"],
                        row["Video_id"],
                        row["Comment_Text"],
                        row["Comment_Author"])
                cursor.execute(query, values)

            print('Comments information uploaded successfully.')
            st.success('Comments information uploaded successfully.')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            db.rollback()

# Function to excute Query of 1st Question 
def sql_question_1():
    
    try:
        query ='''
        SELECT v.Video_Name, c.channel_Name
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id;
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q1_df = pd.DataFrame(results, columns=['channel_Name', 'Video_Title'])
            st.dataframe(Q1_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")

def sql_question_2():
    
    try:
        query ='''
        SELECT c.channel_Name, COUNT(v.Video_Id) AS video_count
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            GROUP BY c.channel_Name
            ORDER BY video_count DESC
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q2_df = pd.DataFrame(results, columns=['channel_Name', 'No of v.count'])
            st.dataframe(Q2_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")

def sql_question_3():
    
    try:
        query ='''
        SELECT v.Video_Name, c.channel_Name, v.Video_ViewCount
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            ORDER BY v.Video_ViewCount DESC
            LIMIT 10;
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q3_df = pd.DataFrame(results, columns=['Video_Title','channel_Name', 'No of views.count'])
            st.dataframe(Q3_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")        



def sql_question_4():
    
    try:
        query ='''
        SELECT Video_Name, Comment_Count
            FROM Videos
            ORDER BY Comment_Count DESC;
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q4_df = pd.DataFrame(results, columns=['Video_Title', 'Comment_Count'])
            st.dataframe(Q4_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}") 

def sql_question_5():
    
    try:
        query ='''
        SELECT v.Video_Name, c.channel_Name, v.Video_LikeCount
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            ORDER BY v.Video_LikeCount DESC;
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q5_df = pd.DataFrame(results, columns=['Video_Title', 'v.Like_Count','channel_Name'])
            st.dataframe(Q5_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")

def sql_question_6():
    
    try:
        query ='''
        SELECT Video_Name, Video_LikeCount
            FROM Videos
            ORDER BY Video_LikeCount DESC;
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q6_df = pd.DataFrame(results, columns=['Video_Title', 'v.Like_Count'])
            st.dataframe(Q6_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err: 
        st.error(f"Error executing query: {err}") 

def sql_question_7():
    
    try:
        query ='''
        SELECT channel_Name, channel_view_count
            FROM channels
            ORDER BY channel_view_count DESC;
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q7_df = pd.DataFrame(results, columns=['channel_Name', 'Total_Views'])
            st.dataframe(Q7_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err: 
        st.error(f"Error executing query: {err}")

def sql_question_8():
    
    try:
        query ='''
        SELECT DISTINCT c.channel_Name
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            WHERE YEAR(v.Video_PublishedAt) = 2022
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q8_df = pd.DataFrame(results, columns=['channel_Name'])
            st.dataframe(Q8_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err: 
        st.error(f"Error executing query: {err}")

def sql_question_9():
    
    try:
        query ='''
        SELECT c.channel_Name, AVG(TIME_TO_SEC(v.Video_Duration)) AS Average_Duration
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            GROUP BY c.channel_Name;
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q9_df = pd.DataFrame(results, columns=['Channel_Name', 'Avg_Duration'])
            st.dataframe(Q9_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err: 
        st.error(f"Error executing query: {err}")  


def sql_question_10():
    
    try:
        query ='''
        SELECT v.Video_Name, c.channel_Name, v.Comment_Count
            FROM Videos v
            JOIN channels c ON v.Channel_Id = c.channel_Id
            ORDER BY v.Comment_Count DESC
            LIMIT 10;
        '''

        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            Q10_df = pd.DataFrame(results, columns=['Video_Title', 'Channel_Name','Comment_Count'])
            st.dataframe(Q10_df)
        else:
            st.write("No data found for the query.")
    except mysql.connector.Error as err: 
        st.error(f"Error executing query: {err}")         

        
# Setting up the options for "Analysis Using SQL" in Streamlit page
if selected == "Analysis Using SQL":
    st.subheader(':blue[Analysis Using SQL]')
    st.markdown('''
        Here, you can perform various SQL-based analyses on the YouTube data stored in your MySQL database.
    ''')
    Questions = [
        'Select your Question',
        '1. What are the names of all the videos and their corresponding channels?',
        '2. Which channels have the most number of videos, and how many videos do they have?',
        '3. What are the top 10 most viewed videos and their respective channels?',
        '4. How many comments were made on each video, and what are their corresponding video names?',
        '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
        '7. What is the total number of views for each channel, and what are their corresponding channel names?',
        '8. What are the names of all the channels that have published videos in the year 2022?',
        '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10. Which videos have the highest number of comments, and what are their corresponding channel names?'
    ]
    
    Selected_Question = st.selectbox('', options=Questions)
    
    if Selected_Question == '1. What are the names of all the videos and their corresponding channels?':
        sql_question_1()
    elif Selected_Question == '2. Which channels have the most number of videos, and how many videos do they have?':
        sql_question_2()
    elif Selected_Question == '3. What are the top 10 most viewed videos and their respective channels?':
        sql_question_3()
    elif Selected_Question == '4. How many comments were made on each video, and what are their corresponding video names?':
        sql_question_4()
    elif Selected_Question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        sql_question_5()
    elif Selected_Question == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write('**:red[Note]:- Dislike property was made private as of December 13, 2021.**')
        sql_question_6()
    elif Selected_Question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        sql_question_7()
    elif Selected_Question == '8. What are the names of all the channels that have published videos in the year 2022?':
        sql_question_8()
    elif Selected_Question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        sql_question_9()
    elif Selected_Question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        sql_question_10()


if selected == "Conclusion":
  st.title(':red[You]Tube:blue[Insights]') 

  st.write("**:red[Our Journey:]**")
  st.subheader("*:blue[Objective:]")
  st.markdown("Develop a streamlit application to empower users with YouTube channel data collection and management.")
  st.subheader("*:blue[Tools:]")
  st.markdown("- Streamlit (user-friendly web interface)")
  st.markdown("- YouTube Data API (data retrieval)")
  st.markdown("- python (scraping)")
  st.markdown("- MySQL (efficient data storage)")

  st.write("**Key Milestones:**")
  st.markdown("- Constructed a Streamlit dashboard to fetch YouTube channel details (name, subscriber count, description) via the YouTube Data API.")
  st.markdown("- Implemented seamless data storage in a MySQL database, encompassing channel information, playlists, video details (with readable durations), and planned comment functionality.")

  st.write("**Value Proposition:**")
  st.markdown("This application empowers researchers and content creators by providing a valuable tool for analyzing YouTube channel data. Streamlit's intuitive interface simplifies data collection and storage, enabling deeper exploration through SQL queries.")

  st.write("**Envisioning the Future:**")
  st.markdown("- Integrate functionalities to collect and store YouTube video comments, enriching the data landscape.")
  st.markdown("- Develop an 'Analysis Using SQL' section within the application, facilitating direct interaction with the database and interactive data visualization using charts and graphs.")

  st.write("**The Bigger Picture:**")
  st.markdown("This project serves as the foundation for a comprehensive platform designed for YouTube channel data management and analysis. With planned enhancements, it has the potential to evolve into a powerful tool for extracting valuable insights from the vast amount of information available on YouTube.")




    




                


                



            



