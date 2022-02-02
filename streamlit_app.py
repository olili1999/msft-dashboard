import streamlit as st
import pandas as pd
import numpy as np
import json
import os 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import warnings 
warnings.filterwarnings('ignore')
import ipywidgets as widgets
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.figure import Figure




st.title('Microsoft Research Dashboarding Project')
try: 
    uploaded_files = st.file_uploader("Choose a JSON file", accept_multiple_files=True)
    # for uploaded_file in uploaded_files:
    #     data = json.load(uploaded_file)
    # liked_posts.json
    liked_posts_json = json.load(uploaded_files[0])
    personal_information_json = json.load(uploaded_files[1])
    account_based_json = json.load(uploaded_files[2])

except: 
    pass


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

def barplot(): 
    #Create a barplot to display my top 5 favorite accounts 
    fig = plt.figure(figsize=(15,7))
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

    st.markdown("It looks like your 5 most liked posts are ___, ___, ___, ___, ___")

with row3_2, _lock: 
    # st.subheader('Books n Stuff ')
    data = {'Category':['Username', 'Phone Number', 'Email', 'Gender', 'Primary Account Location'],
            'Your Information':[user_name, phone_number, email, gender, primary_account_location]}
    df = pd.DataFrame(data)
    df = df.style.set_properties(**{'text-align': 'left'})
    df
