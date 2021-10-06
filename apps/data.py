from datetime import timedelta
from decouple import config
import psycopg2
import pandas as pd
import io
from PIL import Image
import requests


#create all the SQL queries to pull the data from Postgresql
media_info = ''' 
    SELECT *
    FROM light_media_info
'''

media_insights = ''' 
    SELECT *
    FROM light_media_insights
'''

user_info = ''' 
    SELECT *
    FROM light_user_info
'''

user_insights_audience_city = ''' 
    SELECT *
    FROM light_user_insights_audience_city
'''

user_insights_audience_country = ''' 
    SELECT *
    FROM light_user_insights_audience_country
'''

user_insights_audience_gender_age = ''' 
    SELECT *
    FROM light_user_insights_audience_gender_age
'''

user_insights_daily = ''' 
    SELECT *
    FROM light_user_insights_daily
'''

conn = config("DATABASE_URL")
if conn.startswith("postgres://"):
    conn = conn.replace("postgres://", "postgresql://", 1)

conn = psycopg2.connect(conn)
conn.autocommit = True 

def read_sql_inmem_uncompressed(query, conn):
    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
       query=query, head="HEADER"
    )
    #conn = db_engine.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store)
    return df


df_media_info = read_sql_inmem_uncompressed(media_info, conn)
df_media_insights = read_sql_inmem_uncompressed(media_insights, conn)
df_user_info = read_sql_inmem_uncompressed(user_info, conn)
df_user_insights_audience_city = read_sql_inmem_uncompressed(user_insights_audience_city, conn)
df_user_insights_audience_country = read_sql_inmem_uncompressed(user_insights_audience_country, conn)
df_user_insights_audience_gender_age = read_sql_inmem_uncompressed(user_insights_audience_gender_age, conn)
df_user_insights_daily = read_sql_inmem_uncompressed(user_insights_daily, conn)



#convert all datetimes into datetimes
df_media_info["created_date"] = pd.to_datetime(df_media_info["created_date"])
df_media_info["timestamp"] = pd.to_datetime(df_media_info["timestamp"])
df_user_info["created_date"] =  pd.to_datetime(df_user_info["created_date"])
df_media_insights["created_date"] =  pd.to_datetime(df_media_insights["created_date"])
df_user_insights_daily["created_date"] =  pd.to_datetime(df_user_insights_daily["created_date"])
df_user_insights_daily["end_timestamp"] =  pd.to_datetime(df_user_insights_daily["end_timestamp"])
df_user_insights_audience_city["created_date"] =  pd.to_datetime(df_user_insights_audience_city["created_date"])
df_user_insights_audience_city["end_timestamp"] =  pd.to_datetime(df_user_insights_audience_city["end_timestamp"])
df_user_insights_audience_country["created_date"] =  pd.to_datetime(df_user_insights_audience_country["created_date"])
df_user_insights_audience_country["end_timestamp"] =  pd.to_datetime(df_user_insights_audience_country["end_timestamp"])
df_user_insights_audience_gender_age["created_date"] =  pd.to_datetime(df_user_insights_audience_gender_age["created_date"])
df_user_insights_audience_gender_age["end_timestamp"] =  pd.to_datetime(df_user_insights_audience_gender_age["end_timestamp"])

#convert all dates and times to EST (timestamp is in UTC)
df_media_info["created_date"] = df_media_info["created_date"] - timedelta(hours = 5)
df_media_info["timestamp"] = df_media_info["timestamp"] - timedelta(hours = 5)
df_user_info["created_date"] = df_user_info["created_date"] - timedelta(hours = 5)
df_media_insights["created_date"] = df_media_insights["created_date"] - timedelta(hours = 5)
df_user_insights_daily["created_date"] = df_user_insights_daily["created_date"] - timedelta(hours = 5)
df_user_insights_daily["end_timestamp"] = df_user_insights_daily["end_timestamp"] - timedelta(hours = 5)
df_user_insights_audience_city["created_date"] = df_user_insights_audience_city["created_date"] - timedelta(hours = 5)
df_user_insights_audience_city["end_timestamp"] = df_user_insights_audience_city["end_timestamp"] - timedelta(hours = 5)
df_user_insights_audience_country["created_date"] = df_user_insights_audience_country["created_date"] - timedelta(hours = 5)
df_user_insights_audience_country["end_timestamp"] = df_user_insights_audience_country["end_timestamp"] - timedelta(hours = 5)
df_user_insights_audience_gender_age["created_date"] = df_user_insights_audience_gender_age["created_date"] - timedelta(hours = 5)
df_user_insights_audience_gender_age["end_timestamp"] = df_user_insights_audience_gender_age["end_timestamp"] - timedelta(hours = 5)

#convert datetime into date, time and hour
df_user_info["created_date_date"] = df_user_info["created_date"].dt.date
df_user_info["created_date_time"] = df_user_info["created_date"].dt.time
df_user_info["created_date_hour"] = df_user_info["created_date"].dt.hour

df_media_info["created_date_date"] = df_media_info["created_date"].dt.date
df_media_info["created_date_time"] = df_media_info["created_date"].dt.time
df_media_info["created_date_hour"] = df_media_info["created_date"].dt.hour

df_media_insights["created_date_date"] = df_media_insights["created_date"].dt.date
df_media_insights["created_date_time"] = df_media_insights["created_date"].dt.time
df_media_insights["created_date_hour"] = df_media_insights["created_date"].dt.hour

df_media_info["timestamp_date"] = df_media_info["timestamp"].dt.date
df_media_info["timestamp_time"] = df_media_info["timestamp"].dt.strftime("%H:%M")

df_user_insights_daily["created_date_date"] = df_user_insights_daily["created_date"].dt.date
df_user_insights_daily["created_date_time"] = df_user_insights_daily["created_date"].dt.time

df_user_insights_audience_city["created_date_date"] = df_user_insights_audience_city["created_date"].dt.date
df_user_insights_audience_city["created_date_time"] = df_user_insights_audience_city["created_date"].dt.time
df_user_insights_audience_country["created_date_date"] = df_user_insights_audience_country["created_date"].dt.date
df_user_insights_audience_country["created_date_time"] = df_user_insights_audience_country["created_date"].dt.time
df_user_insights_audience_gender_age["created_date_date"] = df_user_insights_audience_gender_age["created_date"].dt.date
df_user_insights_audience_gender_age["created_date_time"] = df_user_insights_audience_gender_age["created_date"].dt.time

#get the weekday and hour from media insights dataframe to calculate the reach distributions
df_media_insights["created_date_weekday"] = df_media_insights["created_date"].dt.weekday
df_media_insights["created_date_weekday"] = df_media_insights["created_date_weekday"].map({
    0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5:"Sat", 6: "Sun"}
    )

#get how long each post has been live for
df_media_insights = df_media_insights.merge(df_media_info[["media_id", "timestamp", "timestamp_date"]].drop_duplicates(), on = "media_id", how = "left")
df_media_insights["duration_live"] = (df_media_insights["created_date"] - df_media_insights["timestamp"])
df_media_insights["hours_live"] = df_media_insights["duration_live"].dt.days * 24 + round(df_media_insights["duration_live"].dt.seconds / 3600,0).astype(int)


#import country codes
# os.chdir("/mnt/c/Users/tom_p/Spira_Analytics/Nomad_Pursuit/Instagram_Dashboard/Dashboard")
df_country_codes = pd.read_csv("https://gist.githubusercontent.com/HarishChaudhari/4680482/raw/b61a5bdf5f3d5c69399f9d9e592c4896fd0dc53c/country-code-to-currency-code-mapping.csv")

df_stopwords = pd.read_csv("https://gist.githubusercontent.com/sebleier/554280/raw/7e0e4a1ce04c2bb7bd41089c9821dbcf6d0c786c/NLTK's%2520list%2520of%2520english%2520stopwords",
                        header = None)
df_stopwords.columns = ["stopwords"]




#create the function crop to instagram post images
#want to show each post as a uniform square instead of a varying 4 sided polygon
def crop_images(media_url):
    starting_image = Image.open(io.BytesIO(requests.get(media_url).content))
    image_width, image_height = starting_image.size
    image_dim = min(image_width, image_height)
    image_area = (0, 0, image_dim, image_dim)
    cropped_image = starting_image.crop(image_area)   

    return cropped_image



MAX_DATETIME = df_media_info["created_date"].max()
MAX_DATETIME_DATE = df_media_info["created_date"].dt.date.max()
MAX_DATETIME_HOUR = MAX_DATETIME.hour

#create a list of the 6 most recent posts
media_images_list = df_media_info[["media_id", "created_date", "timestamp"]].drop_duplicates().sort_values(by = ["created_date", "timestamp"]).tail(6)["media_id"].tolist()

#create a dataframe of these 6 posts
df_media_images = df_media_info.loc[(df_media_info["media_id"].isin(media_images_list)) & (df_media_info["created_date"] == MAX_DATETIME), ["media_id", "media_url", "media_type", "thumbnail_url", "timestamp", "timestamp_date", "timestamp_time", "likes_count", "comments_count", "caption"]]

#if media type is a video then use the thumbnail_url instead of the media url to get the image
df_media_images.loc[df_media_images["media_type"] == "VIDEO", "media_url"] = df_media_images.loc[df_media_images["media_type"] == "VIDEO", "thumbnail_url"].copy()

#save only the fields that are needed
df_media_images = df_media_images[["media_id", "media_url", "timestamp", "timestamp_date", "timestamp_time", "likes_count", "comments_count", "caption"]].copy()

df_media_images["cropped_image"] = df_media_images["media_url"].apply(lambda x: crop_images(x))


#for the media_posts and post_performance page add on reach, impressions, engagement and saved to display these metrics
df_media_images = df_media_images.merge(df_media_insights.loc[(df_media_insights["created_date_date"] == MAX_DATETIME_DATE) & (df_media_insights["created_date_hour"] == MAX_DATETIME_HOUR).copy(), ["media_id", "reach", "impressions", "engagement", "saved"]],
                            how = "left", on = "media_id")

#and weekday
df_media_images["timestamp_weekday_number"] = df_media_images["timestamp"].dt.weekday
df_media_images["timestamp_weekday"] = df_media_images["timestamp_weekday_number"].map({0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5:"Sat", 6: "Sun"})


