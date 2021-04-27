## Redditor Activity Mapper

A script that uses reddit APIs to grab the posters from a specified subreddit and find what other subreddits they post to. Used to find some connections between subreddits.

[Interactive plot for r/LudwigAhgren](https://chart-studio.plotly.com/~brandon-info/3)

Raw data with over 7000 subreddits of activity compared to Ludwig's is in the activity.csv file if you want it.
<hr>

### Instructions for use:
<br>

**Required:** Some knowledge of python and Reddit API keys.

```
$ git clone https://github.com/maybemaby/RAM
$ pip install -r requirements.txt
```

The functions can technically work with pretty much any subreddit but I reccommend sticking to small - moderately active subreddits or short timeframes for large subreddits. 

Haven't optimised performance much and API requests are limited so a moderately active subreddit like r/LudwigAhgren takes a few hours to get the data.