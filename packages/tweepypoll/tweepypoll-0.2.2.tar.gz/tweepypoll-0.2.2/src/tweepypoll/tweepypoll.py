# author: Rada Rudyak, Wenxin Xiang, Linh Giang Nguyen
# date: 2022-01-14

import altair as alt
import pandas as pd
import numpy as np
import tweepy
import dotenv
import os
import re

def get_polls_from_user(username, tweet_num=10):
    '''
    Extract tweet ids (where the tweet contains a poll) for a given Twitter user
    
    Parameters
    ----------
    username : str
        username of the Twitter user
    tweet_num: int
        number of the most recent tweets to be pulled
        default = 10
        maximum = 100, minimum = 5 per request by Twitter API
        
    Returns
    --------
        array of twitter ids
    Examples
    --------
    >>> get_polls_from_user('PollzOnTwitta')
    '''

    # Check argument validity
    if not(isinstance(username, str)):
        raise TypeError('Invalid argument type: username must be a string.')
    elif not(isinstance(tweet_num, int) and tweet_num >= 5 and tweet_num <= 100):
        raise TypeError('Invalid argument: input tweet_num must be >= 5 and <= 100.')

    # Twitter API credentials
    #from dotenv import load_dotenv
    #load_dotenv(".env")
    #bearer_token = os.environ.get("BEARER_TOKEN")

    ############################################################################
    # Note: For the TAs convenience, we hard coded the bearer_token below.
    # In practice, we would use commented out code to get the token from environmental variable
    ############################################################################
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAAyIYQEAAAAAjvBdCMMh1dT8clkpXhHxzld7Dhs%3DLPl5zMXXOZqznZGe9JP7zHj3Wzx0N4unogLcWl8wfIkwikjQKm'
    client = tweepy.Client(bearer_token=bearer_token)
    
    # Get user_id from username
    users = client.get_users(usernames=username, user_fields=['id'])

    for user in users.data:  
        user_id = user.id

    # Get tweets specified by the requested user id
    tweets = client.get_users_tweets(id=user_id, 
                                     max_results=tweet_num,
                                     expansions="attachments.poll_ids")

    # Get tweet_id from tweets that contain polls (if available)
    tweet_id_with_poll = []

    for tweet in tweets.data:
        if "attachments" in tweet.data.keys():
            tweet_id_with_poll.append(tweet.id)
        else:
            pass  
    
    return tweet_id_with_poll

def get_poll_by_id(tweet_ids):
    """
    Extracts poll data from Twitter given the poll IDs array

    Parameters
    ----------
    tweet_id : str
        id of the tweet containing twitter poll

    Returns
    --------
    a dictionary with the following keys:
        poll question,
        poll responses,
        total votes,
        duration,
        date

    Examples
    --------
    >>> get_poll_by_id(['1484375486473986049','1484375486473986049'])
    """

    # Check argument validity
    if not(isinstance(tweet_ids, list)):
        raise TypeError('Invalid argument type: input tweet_id must be a list of numeric IDs.')

    # Twitter API credentials
    #from dotenv import load_dotenv, find_dotenv
    #load_dotenv(find_dotenv())
    #bearer_token = os.environ.get("BEARER_TOKEN")
    
    ############################################################################
    # Note: For the TAs convenience, we hard coded the bearer_token below.
    # In practice, we would use commented out code to get the token from environmental variable
    ############################################################################
    
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAAyIYQEAAAAAjvBdCMMh1dT8clkpXhHxzld7Dhs%3DLPl5zMXXOZqznZGe9JP7zHj3Wzx0N4unogLcWl8wfIkwikjQKm'
    client = tweepy.Client(bearer_token=bearer_token)

    rtn = []

    for tweet_id in tweet_ids:

        res_tweet = client.get_tweets(
            tweet_id,
            expansions=["attachments.poll_ids", "author_id"],
            poll_fields=["duration_minutes", "end_datetime"],
        )
        res = res_tweet.includes

        try:
            res["polls"][0]
        except KeyError:
            raise TypeError("Provided tweet does not contain a poll!")

        poll = res["polls"][0]
        duration = poll["duration_minutes"]
        date = poll["end_datetime"]
        options = poll["options"]
        text = res_tweet.data[0]["text"]
        user = res["users"][0].username

        total = 0
        for opt in options:
            total = total + opt["votes"]

        tweet_data = {
            "text": text,
            "duration": duration,
            "date": date,
            "poll options": options,
            "user": user,
            "total": total,
        }

        rtn.append(tweet_data)

    return rtn


def visualize_poll(poll_obj, show_user=False, show_duration=False, show_date=False):
    """
    Returns a simple bar chart of poll responses
    Option to include additional information in the text box

    Parameters
    ----------
    poll_obj : dictionary
        the output of get_poll_by_id() function
    show_user : bool
        option to display user handle in the textbox
        default = False
    show_duration : bool
        option to display poll duration
        default = False
    show_date : bool
        option to display date
        default = False

    Returns
    --------
        an altair bar chart for the poll responses
        includes a textbox with additional information if at least one of
        - show_user
        - show_duration
        - show_date
        was set to True

    Examples
    --------
    >>> visualize_poll('4235234', show_duration=True)
    """
    
    # Check for valid inputs
    if not isinstance(poll_obj, dict):
        raise Exception("The type of the argument 'poll_obj' mush be a dictionary")
    
    # Convert dictionary to pd.DataFrame
    df = pd.DataFrame(poll_obj["poll options"])
    
    # Extract user id and print
    if show_user == True:
        print(f"The user of the poll: {poll_obj['user']}")
    
    # Extract poll date and print
    if show_date == True: 
        print(f"The end date and time of the poll: {pd.Timestamp(poll_obj['date']).strftime('%Y-%m-%d %H:%M:%S')}") # len()=1
    
    # Extract duration and print
    if show_duration == True:
        print(f"The duration of the poll in hours: {poll_obj['duration'] / 60:.1f}h")
    
    # Create the plot
    plot = alt.Chart(
        df, 
        title=alt.TitleParams(
            text=poll_obj['text'],
            anchor="start"
        )).mark_bar().encode(
        alt.Y('label', title='', sort='x'),
        alt.X('votes', title='Votes'),
        alt.Color('label',title='Options'),
        alt.Tooltip('votes')
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=15,
    ).configure_title(fontSize=20
                     ).properties(
        height=200, width=400
    )

    return plot
