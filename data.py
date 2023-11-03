# File to maintain user data
# User has profile, messages/posts, likes

import pandas as pd
from flask_login import UserMixin


# TODO: Find out if pandas allow unique key classification/establish relationships


class User:
    users = pd.read_csv("data.csv")

    # for explicitly loading at startup
    @classmethod
    def load_users(cls):
        cls.users = pd.read_csv("data.csv")

    @classmethod
    def createUser(cls, username, email, password):
        # should not be used in loop --> O(n)
        new_user = pd.DataFrame(
            [[username, email, "", password, [], []]], columns=cls.users.columns
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        cls.users.to_csv("data.csv")
        print(cls.users)  # for testing
        # results in an error if csv is open when register in-progess
        # logical error or bug?


# TODO: Address issue of maintaining data
# On app start retrieve user data -- Might be redundant (revisit at post implementation)
# write user data to a file when registering -- check
# use csv DF to add authentication


""" Skeleton of post structure
posts = pd.DataFrame(columns=['author','date', 'content', 'likes'])
"""

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#   https://pandas.pydata.org/docs/user_guide/io.html
"""
