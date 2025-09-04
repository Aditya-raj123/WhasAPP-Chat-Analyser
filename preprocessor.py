import re
import pandas as pd

def preprocess(chat_text):
    # Regex pattern: DD/MM/YYYY or DD/MM/YY, HH:MM - Sender: Message
    pattern = r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s(.*)"

    dates = []
    users = []
    messages = []

    for line in chat_text.split("\n"):
        match = re.match(pattern, line)
        if match:
            date_str = match.group(1) + " " + match.group(2)
            message_block = match.group(3)

            # Handle user vs system message
            if ": " in message_block:
                user, message = message_block.split(": ", 1)
            else:
                user = "group_notification"
                message = message_block

            dates.append(date_str)
            users.append(user.strip())
            messages.append(message.strip())
        else:
            # Multi-line message continuation
            if messages:
                messages[-1] += " " + line.strip()

    # Convert to DataFrame
    df = pd.DataFrame({
        'date': pd.to_datetime(dates, dayfirst=True, errors='coerce'),
        'user': users,
        'message': messages
    })

    # Extract datetime parts
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['month_num'] = df['date'].dt.month
    
    period = []
    for hour in df[['day_name','hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour+1))
        else:
            period.append(str(hour) + "-" + str(hour+1))
            
    df['period'] = period

    

    # Create period column (e.g., 01-02AM, 02-03PM)
    df['period'] = df['hour'].apply(lambda h: f"{h:02d}-{(h+1)%24:02d}")

    return df
