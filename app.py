import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a File")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if "group_notification" in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")   

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        # ===== Top statistics =====
        num_messages, words, num_media_message, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Shared")
            st.title(num_media_message)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # ===== Monthly timeline =====
        st.title('Monthly Timeline')
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message_count'], color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # ===== Daily timeline =====
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message_count'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # ===== Most busy users (group-level only) =====
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                st.header("Most Busy Users (Chart)")
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='r')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most Busy Users (Data)")
                st.dataframe(new_df)

        # ===== Most common words =====
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)

        if isinstance(most_common_df, pd.DataFrame):
            if most_common_df.shape[1] == 2:
                most_common_df.columns = ['word', 'count']
        else:
            most_common_df = pd.DataFrame(most_common_df, columns=['word', 'count'])

        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='skyblue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.dataframe(most_common_df)

        # ===== Emoji analysis =====
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df['count'].head(),
                    labels=emoji_df['emoji'].head(),
                    autopct="%0.2f"
                )
                st.pyplot(fig)
            else:
                st.write("No emojis found in this chat.")

        # ===== Activity map =====
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # ===== Weekly Activity Heatmap =====
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        fig, ax = plt.subplots(figsize=(12,6))
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)
