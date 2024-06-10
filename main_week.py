import streamlit as st
import pandas as pd
from pygooglenews import GoogleNews
from datetime import datetime, timedelta
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup


# Function to perform sentiment analysis on the title using TextBlob
def analyze_title_sentiment(title):
    try:
        title_blob = TextBlob(title)
        sentiment_score = title_blob.sentiment.polarity
        return sentiment_score
    except:
        return 0.0

# Function to perform sentiment analysis on the title using Vader
def analyze_title_sentiment_vader(title):
    analyzer = SentimentIntensityAnalyzer()
    vader_scores = analyzer.polarity_scores(title)
    return vader_scores['compound']

# Function to perform a Google News search and return a DataFrame for a specific date range
def google_news_search_for_date_range(keyword, from_date, to_date):
    try:
        # Initialize a GoogleNews object
        gn = GoogleNews()

        # Perform the search for the specified date range
        search_results = gn.search(keyword, from_=from_date, to_=to_date)

        # Create a list of dictionaries containing the title and published date
        filtered_data = [{'Title': entry['title'].split('-')[0].strip(), 'Published Date': entry['published'], 'News Source': entry['title'].split('-')[-1].strip()} for entry in search_results['entries'] if any(word.lower() in entry['title'].lower() for word in keyword.split())]

        if filtered_data:
            # Create a DataFrame from the list of dictionaries
            df = pd.DataFrame(filtered_data)
        else:
            # If no records are filtered, return all titles
            df = pd.DataFrame([{'Title': entry['title'].split('-')[0].strip(), 'Published Date': entry['published'], 'News Source': entry['title'].split('-')[-1].strip()} for entry in search_results['entries']])

        # Add sentiment analysis columns using TextBlob and Vader
        df['TextBlobSentiment'] = df['Title'].apply(analyze_title_sentiment)
        df['VaderSentiment'] = df['Title'].apply(analyze_title_sentiment_vader)

        # Convert the values in the 'Published Date' to datetime objects
        df['Published Date'] = pd.to_datetime(df['Published Date'], format='%a, %d %b %Y %H:%M:%S %Z')

        # Return the DataFrame
        return df

    except ValueError as e:
        return None



def main():
    st.title('news SNTMNT ANLYZR')

    # Get user input for the date range
    from_date = st.date_input("Enter the starting date:")
    to_date = st.date_input("Enter the ending date:")

    keyword = st.text_input("Enter the keyword (e.g., Betta Edu): ")

    if from_date <= to_date and (to_date - from_date).days <= 6:
        if st.button("Run Analysis"):
            dataframes = []

            # Iterate through consecutive pairs of days within the specified date range
            current_date = from_date.strftime('%Y/%m/%d')
            to_date = to_date.strftime('%Y/%m/%d')
            while current_date < to_date:
                next_date = (datetime.strptime(current_date, '%Y/%m/%d') + timedelta(days=1)).strftime('%Y/%m/%d')
                df = google_news_search_for_date_range(keyword, current_date, next_date)
                if df is not None:
                    dataframes.append(df)
                current_date = next_date

            # Concatenate all dataframes into a single dataframe
            if dataframes:
                result_df = pd.concat(dataframes, ignore_index=True)

                # Customize the final CSV file name to include the date range
                #date_range_str = f'{from_date}_{to_date}'
                now = datetime.now()
                final_csv_filename = f'{keyword}{now}.csv'
                result_df.to_csv(final_csv_filename, index=False)
                st.write(f"Saved the final data to `{final_csv_filename}`")

                # Display the resulting DataFrame
                st.write(result_df)

            else:
                st.write("No dataframes were generated.")
    else:
        st.error("Please make sure the ending date is after the starting date and the selected date range is within the last week.")

if __name__ == "__main__":
    main()
