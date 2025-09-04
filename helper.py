from urlextract import URLExtract
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user == 'Overall':   
        temp = df
    else:
        temp = df[df['user'] == selected_user]

    # number of messages
    num_messages = temp.shape[0]

    # number of words
    words = []
    for message in temp['message']:
        words.extend(message.split())

    # number of media messages
    num_media_messages = temp[temp['message'] == '<Media omitted>'].shape[0]
    
    # fetch number of links
    links = []
    for message in temp['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    percent_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2) \
                    .reset_index().rename(columns={'index': 'name', 'user': 'percent'})
    return x, percent_df


def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read().split()  # split into list
    
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]
        
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']  
    
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    
    most_common_df = pd.DataFrame(Counter(words).most_common(30),
                                  columns=['word', 'count'])  
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]
        
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
        
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))),
                            columns=['emoji', 'count'])  
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]

    # Ensure necessary columns exist
    if 'year' not in df.columns or 'month' not in df.columns or 'month_num' not in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.strftime('%B')
        df['month_num'] = df['date'].dt.month
        
    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()
    timeline.rename(columns={'message': 'message_count'}, inplace=True)
    
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]

    # Ensure 'only_date' exists
    if 'only_date' not in df.columns:
        if 'date' in df.columns:
            df['only_date'] = pd.to_datetime(df['date']).dt.date
        else:
            raise KeyError("DataFrame must have a 'date' column to create 'only_date'.")
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    daily_timeline.rename(columns={'message': 'message_count'}, inplace=True)
    
    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]
        
    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]
        
    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':   
        df = df[df['user'] == selected_user]
        
    user_heatmap = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    
    return user_heatmap
    
    
    