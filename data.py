# File to maintain user data
# User has profile, messages/posts, likes

import pandas as pd
from flask_login import UserMixin


# TODO: Find out if pandas allow unique key classification/establish relationships


class User:
    users = pd.DataFrame(
        columns=["username", "email", "image_file", "password", "likes", "posts"]
    )

    @classmethod
    def createUser(cls, username, email, password):
        # should not be used in loop --> O(n)
        new_user = pd.DataFrame(
            [[username, email, "", password, [], []]], columns=cls.users.columns
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        print(cls.users)  # for testing


# TODO: Address issue of maintaining data
# write user data to a file when registering
# retrieve and check file on app start
# print(users)

""" Skeleton of post structure
posts = pd.DataFrame(columns=['author','date', 'content', 'likes'])
"""

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
"""
