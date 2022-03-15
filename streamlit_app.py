import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import json
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import warnings 
warnings.filterwarnings('ignore')
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.figure import Figure
import re
from io import StringIO
import random
from streamlit_folium import folium_static
import folium
from folium import Choropleth, Circle, Marker
import folium.plugins as plugins
from folium.plugins import HeatMap, MarkerCluster, HeatMapWithTime

import geopandas as gpd
import string
from pandas.io.json import json_normalize
from geopy.geocoders import Nominatim 
import requests
import math


import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob


import zipfile


from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)
f=pd.read_csv('word_frequency.csv')

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

def update_frequcny(ad):
    kwords=[]
    regex='<div class="c7O9k">((\w| |-|:)+)'
    a=re.findall(regex,ad)
    #turn into list
    lst=[]
    lst2=[]
    num=0
    for ele in a:
        lst.append([ele[0]][0].strip())
    #remove basic information
    substring = ':'
    for ele in lst:
        if ele.startswith('Male')==False and ele.startswith('Female')==False and ele.endswith('years old')==False and (substring in ele)==False:
            lst2.append(ele)
    lst_first_appear=[]
    #find out word appearing for the first time
    for ele in lst2:
        if ele not in list(f['word']):
            lst_first_appear.append(ele)
    lst3=lst_first_appear
    #Google trend key word list prep
    if len(lst3)>=5:
        for num in range(5):
            word=random.choice(lst3)
            lst3.remove(word)
    else:
        kwords=lst_first_appear
    kwords.append('Used Vehicles')
    #Google trend api
    dict_google=dict(pytrends.get_historical_interest(kwords, year_start=2022, month_start=3, day_start=6, hour_start=0, year_end=2022, month_end=3, day_end=8).iloc[-1])
    #normalize the value
    del dict_google['isPartial']
    if dict_google['Used Vehicles']==0:
        dict_google['Used Vehicles']=1
    for key in dict_google.keys():
        num=int(dict_google[key])*67/dict_google['Used Vehicles']
        dict_google[key]=num
    #Value for existed tags
    existed_dict={}
    for ele in lst2:
        if ele in list(f['word']):
            existed_dict[ele]=list(f.loc[f['word'] == ele]['Google_Trend _Frequency'])[0]
    if len(dict_google)!=0:
        for key in dict_google.keys():
            existed_dict[key]=dict_google[key]
    return existed_dict


def extract_inference(ad):
    #extract_tags
    regex='<div class="c7O9k">((\w| |-|:)+)'
    a=re.findall(regex,ad)
    #turn into list
    lst=[]
    num=0
    for ele in a:
        lst.append([ele[0]][0].strip())
    #frequency_dict

    frq_dic=update_frequcny(ad)

    #extract specific tags we want
    age=''
    gender=''
    music=[]
    income=''
    marrial_status=''
    parental_status=''
    for i in lst:
        if i.startswith('Household Income: '):
            income=i.split(': ')[1].lower()
        if i.startswith('Marital Status: '):
            marrial_status=i.split(': ')[1].lower()
        if i.startswith('Parental Status: '):
            parental_status=i.split(': ')[1].lower()
        if i.endswith('Music'):
             music.append(i)
        if i.endswith('years old'):
            age=i.lower()
        if i=='Male'or i=='Female':
            gender=i.lower()
    for ele in music:
        if ele=='Music':
            music.remove('Music')
    games=[i for i in lst if i.endswith('Games')]
    for ele in music:
        if ele=='Games':
            games.remove('Games')
    lst_2=[]
    for ele in lst[2:]:
        if ':' not in ele:
            if ele not in games and ele not in music and ele!='Music' and ele!='Game':
                lst_2.append(ele.lower())
    #lst_habit=[]
    #num_list=[]
    #for num in range(7):    
    #    ind=random.randrange(len(lst_2))
    #    if ind in num_list:
    #        num=num-1
    #    else:
    #        num_list.append(ind)
    #        lst_habit.append(lst_2[ind].lower())
    lst_habit=[]
    if len(frq_dic)>=5:
        for num in range(5):
            a=min(frq_dic, key=frq_dic.get)
            b=a.lower()
            lst_habit.append(b)
            del frq_dic[a]
    else:
        for num in range(len(frq_dic)):
            a=min(frq_dic, key=frq_dic.get)
            b=a.lower()
            lst_habit.append(b)
            del frq_dic[a]
    #write basic information
    if income!=None:
        if age!='' and gender!='':
            final_str="According to the data Google extract from your activties, Google infers that you are a " +age+' '+gender+' with a '+income+' family income. '
        elif age=='' and gender!='':
            final_str="According to the data Google extract from your activties, Google infers that you are a "+gender+' with a '+income+' family income. '
        elif age!='' and gender=='':
            final_str="According to the data Google extract from your activties, Google infers that you are " +age+' with a '+income+' family income. '
        elif age=='' and gender=='':
            final_str="According to the data Google extract from your activties, Google infers that you have a " +income+' family income. '
    elif income==None:
        if age!='' and gender!='':
            final_str="According to the data Google extract from your activties, Google infers that you are a " +age+' '+gender+'. '
        elif age!='' and gender=='':
            final_str="According to the data Google extract from your activties, Google infers that you are " +age+'. '
        elif age=='' and gender!='':
            final_str="According to the data Google extract from your activties, Google infers that you are a "+gender+'. '
        else:
            final_str=''
    if parental_status!='' and marrial_status!='':
        final_str=final_str+ 'Google also infers that you are '+marrial_status+' and '+parental_status+'. '
    if parental_status=='' and marrial_status!='':
        final_str=final_str+ 'Google also infers that you are '+marrial_status+'. '
    if parental_status!='' and marrial_status=='':
        final_str=final_str+ 'Google also infers that you are '+parental_status+'. '
    #write habits
    if len(lst_habit)>4:
        final_str2='From your activties and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
        final_str2+='Google also noticed that you are interested in '+lst_habit[2]+', '+ lst_habit[3]+' and '+lst_habit[4]+'. '
    elif len(lst_habit)==4:
        final_str2='From your activties and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
        final_str2+='Google also noticed that you are interested in '+lst_habit[2]+' and '+lst_habit[3]+'. '
    elif len(lst_habit)==3:
        final_str2='From your activties and searches on Google, Google infers that you may be interested in '+lst_habit[0]+', '+ lst_habit[1]+' and '+ lst_habit[2]+'. '
    elif len(lst_habit)==2:
        final_str2='From your activties and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
    elif len(lst_habit)==1:
        final_str2='From your activties and searches on Google, Google notices that you may be interested in '+lst_habit[0]+'. '
    elif len(lst_habit)==0:
        final_str2='Google knows nothing about your habits because of your limited activty on Google. '
    #write catgorical habits
    if len(music)>1:
        final_str2+='Among different types of musics, you enjoyed listening to'
        for ele in music:
                if ele!=music[-1]:
                    final_str2=final_str2+' '+ele.lower()+','
                else:
                    final_str2=final_str2+' and '+ele.lower()+'. '
    if len(games)>1:
        final_str2+='You also enjoy playing'
        for ele in games:
            if ele!=games[-1]:
                final_str2=final_str2+' '+ele.lower()+','
            else:
                final_str2=final_str2+' and '+ele.lower()+'.'
    return final_str+final_str2


st.title('Your Social Media Data Dashboard')
st.caption("NOTE: None of your personal data you upload to this dashboard will be saved by this research team.")
st.header("Instagram Data Dashboard")
st.caption("We've created an insights dashboard just using the information Instagram tracks about you.")

try: 
    uploaded_files = st.file_uploader("Upload your account_based_in.json, advertisers.json, liked.json, personal.json, and post_comments.json files to create your personal Instagram Data Dashboard", accept_multiple_files=True, key = 0)
    st.caption("NOTE: The zipfile.zip file may take a long time to upload depending on the size of your data. Be patient and allow for 1-2 minutes of it.")
    sorted_files = []
    index = 0 
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        sorted_files.append([index, uploaded_file.name, uploaded_file, bytes_data])
        index+=1 

    if len(sorted_files) >= 1: 
        # sort files by name 
        sorted_files = sorted(sorted_files, key=lambda x: x[1])
        for file in sorted_files: 
            name = str(file[1])
            if name.startswith("account_based_in"): 
                account_based_json = json.load(file[2])
            elif name.startswith("advertisers"):
                advertisers_using_json = json.load(file[2])
            elif name.startswith("liked"):
                liked_posts_json = json.load(file[2])
            elif name.startswith("personal"):
                personal_information_json = json.load(file[2])
            elif name.startswith("post_comments"): 
                post_comments_json = json.load(file[2])
            elif name.startswith("zipfile"):
                zipfile = zipfile.ZipFile(file[2])
                size = sum([zinfo.file_size for zinfo in zipfile.filelist])
                total_file_size = round(float(size) / 1000000,2)  # total file size in mB




    # profile information
    user_name = personal_information_json['profile_user'][0]['string_map_data']['Username']['value']
    phone_number = personal_information_json['profile_user'][0]['string_map_data']['Phone Number']['value']
    email = personal_information_json['profile_user'][0]['string_map_data']['Email']['value']
    gender = personal_information_json['profile_user'][0]['string_map_data']['Gender']['value']
    primary_account_location = account_based_json['inferred_data_primary_location'][0]['string_map_data']['City Name']['value']


    #Parse through the liked_posts.json file to take count of all of the posts I've liked and which account they belong to
    liked_posts = []
    for like in liked_posts_json['likes_media_likes']:
        liked_posts.append((like['title']))
    top_liked_accounts = (Counter(liked_posts).most_common(5))
    account_name = list(zip(*top_liked_accounts))[0]
    num_liked_posts = list(zip(*top_liked_accounts))[1]


    _lock = RendererAgg.lock
    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))
    with line1_1:
        st.header('Your Instagram Information, Visualized')

    st.write('')
    row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.columns(
        (.1, 1, .1, 1, .1))

    with row3_1, _lock:
        # st.subheader('Books n Stuff ')
        fig = plt.figure(figsize=(10,6))
        ax = fig.subplots()
        x_pos = np.arange(len(account_name))
        plt.bar(x_pos, num_liked_posts,align='center',color='#8134AF')
        plt.rcParams.update({'font.size': 10})
        plt.xticks(x_pos, account_name) 
        plt.xticks(rotation=90)
        plt.title("Favorite Instagram Accounts")
        plt.xlabel('Account Name')
        plt.ylabel('Number of Liked Posts')
        plt.show()
        st.pyplot(fig)
        st.markdown("It looks like your 5 most liked posters are: {}, {}, {}, {}, {}".format(top_liked_accounts[0], top_liked_accounts[1], top_liked_accounts[2], top_liked_accounts[3], top_liked_accounts[4]))

    with row3_2, _lock: 
        data = {'Category':['Username', 'Phone Number', 'Email', 'Gender', 'Primary Account Location'],
                'Your Information':[user_name, phone_number, email, gender, primary_account_location]}
        df = pd.DataFrame(data)
        # Display an interactive table
        st.table(df)



    st.write('')
    row4_space1, row4, row4_space2 = st.columns((0.01, 1, 0.01))


    with row4, _lock: 
        # Get all Instagram comments into one list
        #Get all Instagram comments into one list
        comment_list = []
        list_of_dic = post_comments_json['comments_media_comments']
        for index in range(len(list_of_dic)):
            comment_list.append(list_of_dic[index]['string_list_data'][0]['value'])

        long_comments = []
        for comment in comment_list:
            comment = comment.encode("ascii", "ignore").decode()
            if len(comment) > 100:
                long_comments.append(comment)

        #Put longest comments in dataframe
        st.subheader("All Comments 100 Characters or More")
        df_long_comment = pd.DataFrame({'Your Long Comments': long_comments})
        df_long_comment = df_long_comment.style.set_properties(**{'text-align': 'left'}).hide_index()

    
        # Display an interactive table
        st.table(df_long_comment)
        st.subheader("Your Most Polarizing Comments")
        st.write("Sentiment is view of or attitude toward a situation or event; an opinion. The following table shows your top five negative and top five positive comments based on a sentiment analysis. Please note that the sentiment analyser can only analyze if the words in your comment have a positive or negative meaning. Not if you are using the words in a positive or negative way. Therefore, if you use words in ways other than their intended meanings, your comment selection may not be as 'negative' or 'positive' as expected.")
        #Comment Sentiment Analysis 

        #Read comments to a dataframe
        df_sentiment_analysis = pd.DataFrame(comment_list, columns = ['Comment'])

        #Function to remove non-ASCII from comments 
        def remove_non_ascii(text): 
            return ''.join(i for i in text if ord(i)<128) 
        df_sentiment_analysis['Comment'] = df_sentiment_analysis['Comment'].apply(remove_non_ascii) 


        #Data preprocessing
        df_sentiment_analysis['Comment'] = df_sentiment_analysis['Comment'].astype(str)
        df_sentiment_analysis['Comment'] = df_sentiment_analysis['Comment'].apply(lambda x: " ".join(x.lower() for x in x.split()))
        df_sentiment_analysis['Comment'] = df_sentiment_analysis['Comment'].str.replace(r'[^\w\s]+', '')

        # Define a function which can be applied to calculate the sentiment score for the whole dataset
        # The sentiment function of textblob returns two properties, polarity, and subjectivity. Polarity is 
        # float which lies in the range of [-1,1] where 1 means positive statement and -1 means a negative 
        # statement. Subjective sentences generally refer to personal opinion, emotion or judgment whereas 
        # objective refers to factual information. Subjectivity is also a float which lies in the range of [0,1].
        mask = (df_sentiment_analysis['Comment'].str.len() >= 50)
        df_sentiment_analysis = df_sentiment_analysis.loc[mask]
        def senti(x):
            return TextBlob(x).sentiment  
        df_sentiment_analysis['Sentiment_Score'] = df_sentiment_analysis['Comment'].apply(senti)

        #Create separate columns for Polarity and Subjectivity Scores 
        df_sentiment_analysis[['Polarity', 'Subjectivity']] = pd.DataFrame(df_sentiment_analysis['Sentiment_Score'].tolist(), index=df_sentiment_analysis.index) 

        #Rank comments by sentiment, and then list top 5 negative and top 5 positive comments in a dataframe
        df_sentiment_analysis = df_sentiment_analysis.sort_values('Sentiment_Score')
        top_5_negative = []
        negative_index_list = list(df_sentiment_analysis.head(5).index)
        for idx in negative_index_list:
            top_5_negative.append(comment_list[idx].encode("ascii", "ignore").decode())
        top_5_positive = []
        positive_index_list = list(df_sentiment_analysis.tail(5).index)
        for idx in positive_index_list:
            top_5_positive.append(comment_list[idx].encode("ascii", "ignore").decode())
        df_pos_neg_comments = pd.DataFrame({'5 Most Negative Comments': top_5_negative, '5 Most Positive Comments': top_5_positive})
        pd.set_option('display.max_colwidth', None)
        df_pos_neg_comments = df_pos_neg_comments.style.set_properties(**{'text-align': 'left'}).hide_index()
        st.table(df_pos_neg_comments)

    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))
    with line1_1:
        st.header('Total Data Collected')

    st.write('')
    row5_space1, row5, row5_space5 = st.columns(
        (.1, 1, .1))


    with row5, _lock: 
        num_advertisers_using_data = len(advertisers_using_json['ig_custom_audiences_all_types'])
        st.write("Instagram has collected a total of " + str(total_file_size) + " megabytes of data about you. There are " + str(num_advertisers_using_data) + " advertisers using your Instagram data.")


except: 
    st.error("You need to upload more files. Make sure there are no duplicates, and make sure you have uploaded the correct files and correct number of files from the YouTube video!")



st.header("What Google Knows About You")
st.caption("From your internet usage, we compiled a paragraph that describes the main insights Google was able to infer about you.")
try: 
    uploaded_files= st.file_uploader("Upload your Google Ad Settings HTML for a paragraph about you from Google Ad Settings", accept_multiple_files=True, key= 1)
    index = 0 

    for uploaded_file in uploaded_files:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        # To read file as string:
        string_data = stringio.read()
        st.write(extract_inference(string_data))
except:     
    st.error("Error! You may have uploaded a file of incorrect type, or the incorrect file altogether. Make sure it is the HTML file specified in the YouTube video.")



st.header("Snapchat Has Been Tracking You")
st.caption("We have created a series of different maps, visualizations, and tools to track your location history below. Each one has a slightly different functionality.")
st.caption("NOTE: Some visualizations may take a few minutes or even more to load.")
try: 
    uploaded_files= st.file_uploader("Upload your Snapchat location_history.JSON file here", accept_multiple_files=True, key= 1)
    # for uploaded_file in uploaded_files:
    #     # To convert to a string based IO:
    #     location = json.load(uploaded_file)

    for uploaded_file in uploaded_files:
        # To convert to a string based IO:
        location = json.load(uploaded_file)


   


    areas_visited = location['Location History']

    location_list = list()

    for j in range(len(areas_visited)):
        location_list.append([areas_visited[j]['Time'], areas_visited[j]['Latitude, Longitude']])

    location_df = pd.DataFrame (location_list, columns = ['Time', 'Latitude, Longitude'])

    location_df[['Latitude_old', 'Longitude_old']] = location_df['Latitude, Longitude'].str.split(',', expand=True)
    location_df[['lat', 'Lat_throw']] = location_df['Latitude_old'].str.split('±', expand=True)
    location_df[['long', 'Long_throw']] = location_df['Longitude_old'].str.split('±', expand=True)
    location_df = location_df.drop(['Latitude_old', 'Longitude_old', 'Latitude, Longitude', 'Lat_throw', 'Long_throw'], axis=1)

    location_df['lat'] = pd.to_numeric(location_df['lat'])
    location_df['long'] = pd.to_numeric(location_df['long'])





    # # -------------------------------------------------------------------------------- #
                ##     # BEGIN WHERE SNAPCHAT BELIEVES YOU HAVE BEEN CODE  ## 
    # # -------------------------------------------------------------------------------- #

    st.subheader("Where Snapchat Believes You've Been")
    businesses = location['Businesses and public places you may have visited']
    l_list = list()

    for j in range(len(businesses)):
        l_list.append([businesses[j]['Date'], businesses[j]['Name']])

    business_df = pd.DataFrame (l_list, columns = ['Date', 'Name'])


    _lock = RendererAgg.lock


    _, row1_1, _, row1_2, _ = st.columns((0.1, 1,0.1, 1, 0.1))

    _, row2, _ = st.columns((0.1, 1,0.1))
    _, row3, _ = st.columns((0.1, 1,0.1))
    _, row4_1, _, row4_2, _ = st.columns((0.01, 1,0.1, 1, 0.01))

    with row1_1, _lock: 
        business_df = business_df.sort_values(by = "Date", ascending = True)
        st.table(business_df)

    home_and_work = location['Home & Work']

    work_home_df = pd.DataFrame(list(home_and_work.items()),columns = ['Home','Work']) 
    work_home_df[['Latitude_old', 'Longitude_old']] = work_home_df['Work'].str.split(',', expand=True)
    work_home_df[['lat', 'Lat_throw']] = work_home_df['Latitude_old'].str.split('±', expand=True)
    work_home_df[['long', 'Long_throw']] = work_home_df['Longitude_old'].str.split('±', expand=True)
    work_home_df = work_home_df.drop(['Latitude_old', 'Longitude_old', 'Work', 'Lat_throw', 'Long_throw'], axis=1)
    work_home_df['lat'] = pd.to_numeric(location_df['lat'])
    work_home_df['long'] = pd.to_numeric(location_df['long'])
    work_home_df = work_home_df.rename(columns={"Home": "Inferred Location"})

        
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Assign Latitude & Longitude
    home_Latitude = work_home_df.iat[0,1].astype(str)
    home_Longitude = work_home_df.iat[0,2].astype(str)
    work_Latitude = work_home_df.iat[1,1].astype(str)
    work_Longitude = work_home_df.iat[1,2].astype(str)


    # Get location with geocode
    home_location = geolocator.geocode(home_Latitude+","+home_Longitude)
    work_location = geolocator.geocode(work_Latitude+","+work_Longitude)

    with row1_2, _lock: 
        st.subheader("Snapchat believes your home location is " + str(home_location))
        st.subheader("Snapchat believes your work location is " + str(work_location))



    # # # -------------------------------------------------------------------------------- #
    #             ## BEGIN TIMELAPSE MAP CODE ## 
    # # # -------------------------------------------------------------------------------- #
    
    with row2, _lock: 
        selected_columns = location_df[["Time", "lat", "long"]]
        timelapse_df = selected_columns.copy()
        #timelapse_df
        lat_long_list = []
        for i in timelapse_df['Time'].unique():
            temp=[]
            for index, instance in timelapse_df[timelapse_df['Time'] == i].iterrows():
                temp.append([instance['lat'],instance['long']])
            lat_long_list.append(temp)
            
        #converting it to datetime format
        timelapse_df['Time']= pd.to_datetime(timelapse_df['Time'])
        #creating a time index
        time_index = []
        for i in timelapse_df['Time'].unique():
            time_index.append(i)
        #formatting the index
        date_strings = [d.strftime('%d/%m/%Y, %H:%M:%S') for d in time_index]


        #Choosing the map type 
        timelapse_map = folium.Map(location=[42.2808, -83.7430],zoom_start = 5, tiles="openstreetmap",attr="Stadia.AlidadeSmoothDark")
        #Plot it on the map
        HeatMapWithTime(lat_long_list,radius=10,auto_play=True,position='bottomright',name="cluster",index=date_strings,max_opacity=0.7).add_to(timelapse_map)
        # Display the map
        # Adds tool to the top right
        from folium.plugins import MeasureControl
        timelapse_map.add_child(MeasureControl())
        st.subheader("Here's a timelapse of your location history")
        st.caption("Below you can see every day of location history Snapchat has tracked about you")
        folium_static(timelapse_map, width = 1000)

    # # # -------------------------------------------------------------------------------- #
    #             ## BEGIN CLUSTER MAP ## 
    # # # -------------------------------------------------------------------------------- #

    with row3, _lock: 
        st.subheader("Here's a cluster map of your activity")
        st.caption("By zooming in and out, the number of locations will change. Based upon this, Snapchat can infer your most common locations.")
        # Create the map
        cluster_map = folium.Map(location=[42.2808, -83.7430], tiles='openstreetmap', zoom_start=5)
        # Add points to the map
        mc = MarkerCluster()
        for idx, row in location_df.iterrows():
            if not math.isnan(row['long']) and not math.isnan(row['lat']):
                mc.add_child(Marker([row['lat'], row['long']]))
        cluster_map.add_child(mc)

        # Adds tool to the top right
        from folium.plugins import MeasureControl
        cluster_map.add_child(MeasureControl())
        # Display the map
        folium_static(cluster_map, width = 1000)


    # # # -------------------------------------------------------------------------------- #
    #             ## BEGIN FOURSQUARE NO QUERY CODE ## 
    # # # -------------------------------------------------------------------------------- #
    # CLIENT_ID = 'JKHM1V3IJMGJTDH13VB2UKKYNLHN0N3XG4UENX0JEKBUZSMP' 
    # CLIENT_SECRET = 'CTHTUE1JSINGUNVXSDL0JGPO1CRKOE312RYYA21LEBKE5ZSA' # your Foursquare Secret
    # VERSION = '20220313'
    # LIMIT = 100


    # ndf = location_df[['lat','long']]
    # nndf = ndf.drop_duplicates(subset=['long', 'lat'])

    # concat_df = pd.DataFrame()
    
    # for index, row in nndf.iterrows():
    #     url = "https://api.foursquare.com/v3/places/nearby?ll={},{}&limit=5".format(round(row['lat'], 2),round(row['long'], 2))
    # #     print(url)
    #     headers = {
    #     "Accept": "application/json",
    #     "Authorization": "fsq3chVTJib0Z11IA8qFisvs8p7dkOJ6ky0WEbGTZ9FQPqc="
    #     }
    #     result = requests.request("GET", url, headers=headers).json()
    #     result_df = json_normalize(result['results'])
    #     result_df = result_df.rename(columns={"geocodes.main.latitude": "lat", "geocodes.main.longitude": "long", "location.formatted_address": "address"})
    # #     print(result_df)
    #     concat_df = concat_df.append(result_df)

    # # -------------------------------------------------------------------------------- #
    # foursquare_map_no_query = folium.Map(location=[42.2808, -83.7430], zoom_start=7)
    # # add a red circle marker to represent each visited locations
    # for lat, long in zip(nndf.lat, nndf.long):
    #     folium.features.CircleMarker(
    #         [lat, long],
    #         radius=10,
    #         color='red',
    #         #popup=label,
    #         fill = True,
    #         fill_color='red',
    #         fill_opacity=0.6
    #     ).add_to(foursquare_map_no_query)
    # # add all venues as blue circle markers
    # for lat, long, label in zip(concat_df.lat, concat_df.long, concat_df.name):
    #     folium.features.CircleMarker(
    #         [lat, long],
    #         radius=5,
    #         color='blue',
    #         popup=label,
    #         fill = True,
    #         fill_color='blue',
    #         fill_opacity=0.6
    #     ).add_to(foursquare_map_no_query)

    # folium_static(foursquare_map_no_query)


    # # Adds tool to the top right
    # from folium.plugins import MeasureControl
    # foursquare_map_no_query.add_child(MeasureControl())
    # concat_df = concat_df[['name', 'distance']]
    # concat_df = concat_df.rename(columns = {"name": "Location Name Near You", "distance": "Distance (meters)"})
    # concat_df["Distance (miles)"] = concat_df["Distance (meters)"] / 1000 * 0.621371
    # concat_df = concat_df.sort_values(by = "Distance (miles)", ascending = True)
    # concat_df = concat_df.drop_duplicates(subset='Location Name Near You', keep="last")
    # concat_df = concat_df[["Location Name Near You", "Distance (miles)"]]


      
    # with row4_1, _lock:
    #     st.subheader("We've identified this list of nearby locations of interest for you")
    #     st.caption('Red dots represent each visited locations and Blue dots represent surrounding popular venues')
    #     folium_static(foursquare_map_no_query)

    # with row4_2, _lock: 
    #     st.subheader("This is a list of locations near you")
    #     st.caption('These are all locations of interest in the map to the left near you in ascending order of proximity')
    #     st.table(concat_df)




except:     
    st.error("Error! You may have uploaded a file of incorrect type, or the incorrect file altogether. Make sure it is the JSON file specified in the YouTube video.")





