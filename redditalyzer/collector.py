import os, itertools
from collections import defaultdict
from typing import Generator, Tuple
import praw
import prawcore.exceptions
import requests
import dotenv

dotenv.load_dotenv(".env")

reddit = praw.Reddit(
    client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    user_agent=os.environ.get("USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME"),
    password=os.environ.get("REDDIT_PASSWORD"),
)


def request_pushift(subreddit: str, start_date: str="30d", endpoint:str ="comment") -> Tuple:
    """
    Requests pushift api for comment or submission endpoint and returns list of dicts as first tuple item
    if successful. Second item is a boolean value true if all the possible results
    were returned.
    """
    complete = True
    payload = {
        "subreddit": subreddit,
        "size": 100,
        "after": start_date,
        "metadata": "true",
    }
    baseURL = f"https://api.pushshift.io/reddit/search/{endpoint}/"
    response = requests.get(baseURL, params=payload)
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError):
        raise RuntimeError("Request couldn't be processed")
    else:
        response = response.json()
        if response.get("metadata").get("results_returned") < response.get(
            "metadata"
        ).get("total_results"):
            complete = False
        return (response["data"], complete)


def pull_usernames(data: list, name_set:set=None) -> set:
    """Takes a list of dicts and extracts the author value from each dict into a set."""
    usernames = {entry.get("author") for entry in data}
    if name_set:
        usernames |= name_set
    return usernames


def last_created(data: list) -> str:
    """Gets the timestamp for the last datapoint in the list returned by pushift api"""
    last_created = data[-1].get("created_utc")
    if last_created == None:
        raise NameError("Key created_utc not found in data.")
    return last_created


def retrieve_activity(names: list, time_range:str="month") -> defaultdict:
    """Counts the number of comments and posts made in the past month per subreddit"""
    activity = defaultdict(lambda: {"activity": 0, "rludwig": 0, "users": 0})
    for index, name in enumerate(names):
        print(index, name)
        # Subreddits per person
        subreddits = set()
        pre_count = activity['LudwigAhgren']['activity']
        try:
            user = reddit.redditor(name)
            comments = user.comments.top(time_filter=time_range)
            submissions = user.submissions.top(time_filter=time_range)
            user.link_karma
        except (prawcore.exceptions.NotFound, AttributeError) as e:
            print(f"{name} could not be found. Error: {e}")
            continue
        for obj in itertools.chain(comments, submissions):
            # Increment activity counter everytime the subreddit comes up
            activity[obj.subreddit.display_name]['activity'] += 1
            subreddits.add(obj.subreddit.display_name)
        post_count = activity['LudwigAhgren']['activity']
        for entry in subreddits.difference({'LudwigAhgren'}):
            if post_count > pre_count:
                activity[entry].update(rludwig=activity[entry]['rludwig']+(post_count - pre_count), users=activity[entry]['users']+1)
            else:
                activity[entry]['users'] += 1
    return activity

def activity_patch(names: list, activity, time_range:str="month") -> defaultdict:
    """Function for fixing a dumb mistake I made"""
    activity_patched = activity
    for index, name in enumerate(names):
        print(index, name)
        subreddits = set()
        try:
            user = reddit.redditor(name)
            comments = user.comments.top(time_filter=time_range)
            submissions = user.submissions.top(time_filter=time_range)
            user.link_karma
        except (prawcore.exceptions.NotFound, AttributeError) as e:
            print(f"{name} could not be found. Error: {e}")
            continue
        for obj in itertools.chain(comments, submissions):
            subreddits.add(obj.subreddit.display_name)
        for entry in subreddits.difference({'LudwigAhgren'}):
            if activity[entry].get('users') == None:
                activity[entry]['users'] = 1
            else:
                activity[entry]['users'] += 1
    return activity_patched

if __name__ == "__main__":
    import dill
    with open('usernames.dat', 'rb') as dillfile:
        username_set = dill.load(dillfile)
    test = list(username_set)[:10]
    activity = activity_patch(['free_brandon', 'Exoraii', 'hamxz2', 'Tsevier', '-pizza-time-'], test)
    print(activity)
