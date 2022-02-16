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




st.title('Your Social Media Data Dashboard')
try: 
    uploaded_files = st.file_uploader("Choose a JSON file", accept_multiple_files=True, key = 0)

    sorted_files = []
    index = 0 
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        sorted_files.append([index, uploaded_file.name, uploaded_file, bytes_data])
        index+=1 

    if len(sorted_files) == 4: 
        sorted_files = sorted(sorted_files, key=lambda x: x[1])
        account_based_json = json.load(sorted_files[0][2])
        advertisers_using_json = json.load(sorted_files[1][2])
        liked_posts_json = json.load(sorted_files[2][2])
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
        # st.subheader('Books n Stuff ')
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

uploaded_files_google= st.file_uploader("Choose a JSON file", accept_multiple_files=True, key= 1)



