# Authors: Mahsa Sarafrazi, Mahmood Rahman, Shiva Shankar Jena, Amir Shojakhani
# Jan 2022

# imports
from arrow import now
import requests
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import altair as alt
import numpy as np
from collections import Counter
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from collections import Counter
from string import punctuation

load_dotenv()  # load .env files in the project folder

def get_store(
    bearer_token,
    keyword,
    start_date,
    end_date,
    max_results=25,
    store_path="output/",
    store_csv=False,
    include_public_metrics=True,
    api_access_lvl="essential",
):
    """
    Retreives all tweets of a keyword provided by the user through the Twitter API.
    Alternatively the user can directly read from a structered Json response based
    on the Twitter API.
    If the user plans to access to the Twitter API they must have a personal bearer
    token and store it as an environement variable to access it.
    Parameters:
    -----------
    bearer_token : string
        The user's personal twitter API dev bearer token.
        It is recommended to add the token from an
        enviroment variable.
    keyword : string
        The keyword to search Twitter and retrieve tweets.
    start_date: string
        Starting date to collect tweets from. Dates should be
        entered in string format: YYYY-MM-DD
    end_date: string
        Ending date (Included) to collect tweets from. Dates should be
        entered in string format: YYYY-MM-DD
    max_results: int
        The maximum number of tweets to return. Default is 25.
        Must be between 10 and 100.
    store_path: string
        The string path to store the retrieved tweets in
        Json format. Default is working directory.
    store_csv: boolean
        Create .csv file with response data or not.
        Default is False.
    include_public_metrics : boolean
        Should public metrics regarding each tweet such as
        impression_count, like_count, reply_count, retweet_count,
        url_link_clicks and user_profile_clicks be downloaded
        and stored. Default is True.
    api_access_lvl : string
        The twitter API access level of the user's bearer token.
        Options are 'essential' or 'academic'.
        Default is 'essential'
    Returns:
    --------
    tweets_df : dataframe
        A pandas dataframe of retrieved tweets based on user's
        selected parameters. (Data will be stored as a Json file)
    Examples
    --------
    >>> bearer_token = os.getenv("BEARER_TOKEN")
    >>> tweets = get_store(
            bearer_token,
            keyword="vancouver",
            start_date="2022-01-12",
            end_date="2022-01-17")
    >>> tweets
    """

    # parameter tests
    if not isinstance(bearer_token, str):
        raise TypeError(
            "Invalid parameter input type: bearer_token must be entered as a string"
        )
    if not isinstance(keyword, str):
        raise TypeError(
            "Invalid parameter input type: keyword must be entered as a string"
        )
    if not isinstance(start_date, str):
        raise TypeError(
            "Invalid parameter input type: start_date must be entered as a string"
        )
    if not (
        datetime.strptime(end_date, "%Y-%m-%d")
        > datetime.strptime(start_date, "%Y-%m-%d")
        > (datetime.now() - timedelta(days=7))
    ) & (api_access_lvl == "essential"):
        raise ValueError(
            "Invalid parameter input value: api access level of essential can only search for tweets in the past 7 days"
        )
    if not isinstance(end_date, str):
        raise TypeError(
            "Invalid parameter input type: end_date must be entered as a string"
        )
    if not (
        datetime.now()
        >= datetime.strptime(end_date, "%Y-%m-%d")
        > datetime.strptime(start_date, "%Y-%m-%d")
    ):
        raise ValueError(
            "Invalid parameter input value: end date must be in the range of the start date and today"
        )
    if not isinstance(max_results, int):
        raise TypeError(
            "Invalid parameter input type: max_results must be entered as an integer"
        )
    if not isinstance(store_path, str):
        raise TypeError(
            "Invalid parameter input type: store_path must be entered as a string"
        )
    if not isinstance(store_csv, bool):
        raise TypeError(
            "Invalid parameter input type: store_csv must be entered as a boolean"
        )
    if not api_access_lvl in ["essential", "academic"]:
        raise ValueError(
            "Invalid parameter input value: api_access_lvl must be of either string essential or academic"
        )

    headers = {
        "Authorization": "Bearer {}".format(bearer_token)
    }  # set authorization header for API

    # check access level and switch url accordingly. recent will can only search the past 7 days.
    if api_access_lvl == "essential":
        search_url = "https://api.twitter.com/2/tweets/search/recent"
    elif api_access_lvl == "academic":
        search_url = "https://api.twitter.com/2/tweets/search/all"

    # set request parameters
    query_params = {
        "query": f"{keyword}",
        "start_time": f"{start_date}T00:00:00.000Z",
        "end_time": f"{end_date}T00:00:00.000Z",
        "max_results": f"{max_results}",
        "expansions": "author_id,in_reply_to_user_id",
        "tweet.fields": "id,text,author_id,in_reply_to_user_id,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source",
        "user.fields": "id,name,username,created_at,description,public_metrics,verified,entities",
        "place.fields": "full_name,id,country,country_code,name,place_type",
        "next_token": {},
    }

    # send request and store response
    tweet_response = requests.request(
        "GET", search_url, params=query_params, headers=headers
    )
    tweet_response_json = tweet_response.json()

    # check if path in store path exists. create folders if not and create .Json file
    if not os.path.exists(store_path):
        os.makedirs(store_path)
    with open(os.path.join(store_path, "tweets_response.json"), "w") as file:
        json.dump(tweet_response_json, file, indent=4, sort_keys=True)

    tweets_df = pd.DataFrame.from_dict(tweet_response_json["data"])

    # expand public_metrics column and store in separate columns.
    tweets_df[["retweetcount", "reply_count", "like_count", "quote_count"]] = tweets_df[
        "public_metrics"
    ].apply(pd.Series)

    if store_csv:
        tweets_df.to_csv(os.path.join(store_path, "tweets_response.csv"), index=False)

    return tweets_df


def clean_tweets(file_path, tokenization=True, word_count=True):
    """
    Cleans the text in the tweets and returns as new columns in the dataframe.
    
    The cleaning process includes converting into lower case, removal of punctuation, hastags and hastag counts
    Parameters:
    -----------
    file_path : string
        File path to csv file containing tweets data
    tokenization : Boolean
        Creates new column containing cleaned tweet word tokens when True
        Default is True
    word_count : Boolean
        Creates new column containing word count of cleaned tweets
        Default is True
        
    df_tweets : dataframe
        A pandas dataframe comprising cleaned data in additional columns

    Examples
    --------
    >>> clean_tweets("tweets_df.json")
    """
    
    # Checking for valid input parameters
    
    
    if not isinstance(file_path, str):
        raise Exception("'input_file' must be of str type")
    if not isinstance(tokenization, bool):
        raise Exception("'tokenization' must be of bool type")
    if not isinstance(word_count, bool):
        raise Exception("'word_count' must be of bool type")
    
    # Dropping irrelavant columns
    columns=["public_metrics"]
    df = pd.read_csv(file_path).drop(columns=columns)
    
    # Checking for 'df' to be a dataframe
    if not isinstance(df, pd.DataFrame):
        raise Exception("'df' must be of DataFrame type.")
    
    # Looping through the data set 
    for i in range(len(df)):
        # Cleaning a retweet tag 'RT @xx:'
        tweet_text = df.loc[i,"text"]
        tweet_text = re.sub(r"RT\s@.*:\s","",tweet_text)

        # Lowercasing
        tweet_text.lower()

        # Cleaning hashtags and mentions in tweet
        tweet_text = re.sub(r"@[A-Za-z0-9_]+","", tweet_text)
        tweet_text = re.sub(r"#[A-Za-z0-9_]+","", tweet_text)

        # Cleaning links
        tweet_text = re.sub(r"http\S+", "", tweet_text)
        tweet_text = re.sub(r"www.\S+", "", tweet_text)

        # Cleaning all punctuations and non-alpha numerics
        tweet_text = tweet_text.strip(punctuation).replace(",", "")

        # Adding clean_tweets column    
        df.loc[i, "clean_tweets"] = tweet_text

        # Adding clean_tokens column
        if tokenization:
            df.loc[i, "clean_tokens"] = ','.join(tweet_text.split())
        
        # Adding word_count column
        if word_count:
            df.loc[i, "word_count"] = len(tweet_text.split())
         
    return df
  
def analytics(input_file, keyword):
    """Analysis the tweets of specific keyword in term of
    average number of retweets, the total number of
    comments, most used hashtags and the average number
    of likes of these tweets.

    Parameters
    ----------
    input_file : dataframe
        pandas dataframe
    keyword: str
        The keyword that the original dataframe extracted
        based on.

    Returns
    -------
    analytics_df: dataframe
        Dataframe object where includes average number
        of retweets, the total number of comments, most
        used hashtags and the average number of likes

    Examples
    --------
    >>> from tweetlytics.tweetlytics import analytics
    >>> report = analytics(df,keyword)
    """
    
    #checking the input_file argument to be url path
    if not isinstance(input_file, str):
        raise TypeError(
            "Invalid parameter input type: input_file must be entered as a string of url"
        )
    # check keyword argument to be string
    if not isinstance(keyword, str):
        raise TypeError(
            "Invalid parameter input type: keyword must be entered as a string"
        )

    result = {} # for storing the result from each part
    result["Factors"] = f"Keyword Analysis" #output dataset column name
    
    df = pd.read_csv(input_file) 
    # calculating sum of like, comment and retweets
    result["Total Number of Likes"] = df["like_count"].sum()
    result["Total Number of Comments"] = df["reply_count"].sum()
    result["Total Number of Retweets"] = df["retweetcount"].sum()
    
    #determining the sentiment of the tweet
    pol_list = []
    for tweet in df["text"]:
        pol_list.append(TextBlob(tweet).sentiment.polarity)

    df["polarity"] = pol_list

    pos = 0
    neu = 0
    neg = 0
    for i in range(0, len(df)):
        if df["polarity"][i] > 0:
            pos += 1
        elif df["polarity"][i] == 0:
            neu += 1
        else:
            neg += 1
        i += 1
        
    #storing all results in adictionary
    result["Percentage of Positive Sentiment"] = round(pos / (pos + neg + neu), 2)
    result["Percentage of Negative Sentiment"] = round(neg / (pos + neg + neu), 2)
    result["Percentage of Nuetral Sentiment"] = round(neu / (pos + neg + neu), 2)
    
    #converting the dictionary to data frame
    analytics_df = pd.DataFrame(result,index = ["factors"]).set_index("Factors").T
    return analytics_df

def plot_freq(df, col_text):
    """
    Takes in dataframe and analyzes 
        the hashtags to plot the most frequent ones.

    Parameters:
    -----------
    df : A pandas dataframe 
        consisting of the tweets

    col_text: string
        The column name of tweet text in dataframe.

    Returns:
    --------
    hash_plot: A bar chart
        A chart plotting analysis result of most frequent used hashtag words.
    """
    # Checking for valid inputs
    if not isinstance(df, pd.DataFrame):
        raise Exception("The argunment, df should take in a pandas dataframe")
    if type(col_text) != str:
        raise Exception("The argunment, col_text should take in a string")

    # get hashtags from text
    df['hash'] = df[col_text].apply(lambda x: re.findall(r'[#]\w+', x))

    # counting tags
    hash_dict = {}
    for hashtags in df["hash"]:
        for word in hashtags:
            hash_dict[word] = hash_dict.get(word, 0) + 1

    hash_df = pd.DataFrame(columns=['Keyword', 'Count'])
    for key, value in hash_dict.items():
        key_value = [[key, value]]
        hash_df = hash_df.append(pd.DataFrame(key_value, columns=['Keyword', 'Count']),
                                       ignore_index=True)

    # frequency plot
    hash_plot = alt.Chart(hash_df).mark_bar().encode(
        x=alt.X('Count', title="Hashtags"),
        y=alt.Y('Keyword', title="Count of Hashtags", sort='-x')
    ).properties(
        title='Top 15 Hashtag Words'
    ).transform_window(
        rank='rank(Count)',
        sort=[alt.SortField('Count', order='descending')]
    ).transform_filter((alt.datum.rank <= 15))

    return hash_plot
