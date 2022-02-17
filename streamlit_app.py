import streamlit as st
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
import folium.plugins as plugins
import geopandas as gpd

from pandas.io.json import json_normalize
from geopy.geocoders import Nominatim 
import requests

CLIENT_ID = 'JKHM1V3IJMGJTDH13VB2UKKYNLHN0N3XG4UENX0JEKBUZSMP' # your Foursquare ID
CLIENT_SECRET = 'CTHTUE1JSINGUNVXSDL0JGPO1CRKOE312RYYA21LEBKE5ZSA' # your Foursquare Secret
VERSION = '20220208'
LIMIT = 100





# google extract inferences code
def extract_inference(ad):
    #extract_tags
    # file = open(html_file, "r")
    # ad=file.read()
    regex='<div class="c7O9k">((\w| |-|:)+)'
    a=re.findall(regex,ad)
    #turn into list
    lst=[]
    num=0
    for ele in a:
        lst.append([ele[0]][0].strip())
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
    lst_habit=[]
    num_list=[]
    for num in range(7):    
        ind=random.randrange(len(lst_2))
        if ind in num_list:
            num=num-1
        else:
            num_list.append(ind)
            lst_habit.append(lst_2[ind].lower())

    #write basic information
    if income!=None:
        if age!='' and gender!='':
            final_str="According to the data Google extract from your activities, Google infers that you are a " +age+' '+gender+' with a '+income+' family income. '
        elif age=='' and gender!='':
            final_str="According to the data Google extract from your activities, Google infers that you are a "+gender+' with a '+income+' family income. '
        elif age!='' and gender=='':
            final_str="According to the data Google extract from your activities, Google infers that you are " +age+' with a '+income+' family income. '
        elif age=='' and gender=='':
            final_str="According to the data Google extract from your activities, Google infers that you have a " +income+' family income. '
    elif income==None:
        if age!='' and gender!='':
            final_str="According to the data Google extract from your activities, Google infers that you are a " +age+' '+gender+'. '
        elif age!='' and gender=='':
            final_str="According to the data Google extract from your activities, Google infers that you are " +age+'. '
        elif age=='' and gender!='':
            final_str="According to the data Google extract from your activities, Google infers that you are a "+gender+'. '
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
        final_str2='From your activities and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
        final_str2+='Google also noticed that you are interested in '+lst_habit[2]+', '+ lst_habit[3]+' and '+lst_habit[4]+'. '
    elif len(lst_habit)==4:
        final_str2='From your activities and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
        final_str2+='Google also noticed that you are interested in '+lst_habit[2]+' and '+lst_habit[3]+'. '
    elif len(lst_habit)==3:
        final_str2='From your activities and searches on Google, Google infers that you may be interested in '+lst_habit[0]+', '+ lst_habit[1]+' and '+ lst_habit[2]+'. '
    elif len(lst_habit)==2:
        final_str2='From your activities and searches on Google, Google infers that you may be interested in '+lst_habit[0]+' and '+ lst_habit[1]+'. '
    elif len(lst_habit)==1:
        final_str2='From your activities and searches on Google, Google notices that you may be interested in '+lst_habit[0]+'. '
    elif len(lst_habit)==0:
        final_str2='Google knows nothing about your habits because of your limited activity on Google. '
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
st.header("Instagram Data Dashboard")
try: 
    uploaded_files = st.file_uploader("Upload your account_based_in.json, advertisers.json, liked.json, and personal.json files to create your personal Instagram Data Dashboard", accept_multiple_files=True, key = 0)

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
                account_based_json = json.load(sorted_files[0][2])
            elif name.startswith("advertisers"):
                advertisers_using_json = json.load(sorted_files[1][2])
            elif name.startswith("liked"):
                liked_posts_json = json.load(sorted_files[2][2])
            elif name.startswith("personal"):
                personal_information_json = json.load(sorted_files[3][2])


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
        st.markdown("It looks like your 5 most liked posts are: {}, {}, {}, {}, {}".format(top_liked_accounts[0], top_liked_accounts[1], top_liked_accounts[2], top_liked_accounts[3], top_liked_accounts[4]))

    with row3_2, _lock: 
        data = {'Category':['Username', 'Phone Number', 'Email', 'Gender', 'Primary Account Location'],
                'Your Information':[user_name, phone_number, email, gender, primary_account_location]}
        df = pd.DataFrame(data)
        df = df.style.set_properties(**{'text-align': 'left'})
        df

    line1_spacer1, line1_1, line1_spacer2 = st.columns((.1, 3.2, .1))
    with line1_1:
        st.header('Total Data Collected')

    st.write('')
    row4_space1, row4_1, row4_space2, row4_2, row4_space4 = st.columns(
        (.1, 1, .1, 1, .1))


    with row4_1, _lock: 
        total_file_size = 0 
        for file in sorted_files: 
            total_file_size += len(file[3])
        total_file_size = total_file_size * (0.000001)
        num_advertisers_using_data = len(advertisers_using_json['ig_custom_audiences_all_types'])
        st.write("Instagram has collected a total of " + str(total_file_size) + " megabytes of data about you. There are " + str(num_advertisers_using_data) + " advertisers using your Instagram data.")



except: 
    st.error("You need to upload more files. Make sure there are no duplicates")



st.header("What Google Knows About You")
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
    st.error("Uploaded file of incorrect type. Make sure it is the HTML file specified in the YouTube video.")



st.header("Snapchat has been tracking you.")
try: 
    # center on Liberty Bell
    # m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)

    # # add marker for Liberty Bell
    # tooltip = "Liberty Bell"
    # folium.Marker(
    #     [39.949610, -75.150282], popup="Liberty Bell", tooltip=tooltip
    # ).add_to(m)

    # # call to render Folium map in Streamlit
    # folium_static(m)



    uploaded_files= st.file_uploader("Upload your Snapchat CSV data here", accept_multiple_files=True, key= 1)
    index = 0 

    for uploaded_file in uploaded_files:
        # To convert to a string based IO:
        df = pd.read_csv(uploaded_file)
    

    lat_long_list = []
    for i in df['Date'].unique():
        temp=[]
        for index, instance in df[df['Date'] == i].iterrows():
            temp.append([instance['lat'],instance['long']])
        lat_long_list.append(temp)
    df['Date']= pd.to_datetime(df['Date'])
    #creating a time index
    time_index = []
    for i in df['Date'].unique():
        time_index.append(i)
    #formatting the index
    date_strings = [d.strftime('%d/%m/%Y, %H:%M:%S') for d in time_index]

    from folium.plugins import HeatMap
    from folium.plugins import HeatMapWithTime

    #Choosing the map type 
    m = folium.Map(location=[42.2808, -83.7430],zoom_start = 11,control_scale=True, tiles='openstreetmap',attr="Stadia.AlidadeSmoothDark")

    #Plot it on the map
    HeatMapWithTime(lat_long_list,radius=10,auto_play=True,position='bottomright',name="cluster",index=date_strings,max_opacity=0.7).add_to(m)
    # Display the map
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.LayerControl().add_to(m)
    st.subheader("Here's a timelapse of where you've been.")
    folium_static(m)


    ndf = df[['loc','lat','long']]
    nndf = ndf.drop_duplicates()
    nndf["long_lat"] = list(zip(nndf["lat"], nndf["long"]))
    concat_df = pd.DataFrame()
    concat_df2 = pd.DataFrame()

    # for index, row in nndf.iterrows():
    #     url = "https://api.foursquare.com/v3/places/nearby?ll={},{}&limit=20".format(round(row['lat'], 2),round(row['long'], 2))
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


    user_input = st.text_input('Search Points of Interest')
    for index, row in nndf.iterrows():
        url = "https://api.foursquare.com/v3/places/search?query={}&ll={},{}&radius=50000&limit=5".format(user_input, row['lat'], row['long'])
    #     print(url)
        headers = {
        "Accept": "application/json",
        "Authorization": "fsq3chVTJib0Z11IA8qFisvs8p7dkOJ6ky0WEbGTZ9FQPqc="
        }
        result = requests.request("GET", url, headers=headers).json()
        result_df = json_normalize(result['results'])
        result_df = result_df.rename(columns={"geocodes.main.latitude": "lat", "geocodes.main.longitude": "long", "location.formatted_address": "address"})
        # st.write(result_df)
    #     print(result_df)
        concat_df2 = concat_df.append(result_df)

    st.write(concat_df2)
    new_map2 = folium.Map(location=[42.2808, -83.7430], zoom_start=15)
    # add a red circle marker to represent each visited locations
    for lat, long in zip(nndf.lat, nndf.long):
        folium.features.CircleMarker(
            [lat, long],
            radius=10,
            color='red',
            #popup=label,
            fill = True,
            fill_color='red',
            fill_opacity=0.6
        ).add_to(new_map2)
    

    # # add all venues as blue circle markers
    for lat, long, label in zip(concat_df2.lat, concat_df2.long, concat_df2.name):
        folium.features.CircleMarker(
            [lat, long],
            radius=5,
            color='blue',
            popup=label,
            fill = True,
            fill_color='blue',
            fill_opacity=0.6
        ).add_to(new_map2)

    folium_static(new_map2)




except:     
    st.error("Make sure you uploaded your personal Snapchat media CSV here.")





