# File to maintain user data
# User has profile, messages/posts, likes

import pandas as pd
from flask_login import LoginManager, UserMixin


# TODO: Find out if pandas allow unique key classification/establish relationships


""" UserMixin - manages session user for us
       # is_authenticated()
       # is_active()
       # is_anonymous
       # get_id()
"""


class User(UserMixin):
    def __init__(self, email, username, password, image_file, likes, posts):
        self.id = email
        self.email = email
        self.username = username
        self.password = password
        self.image_file = image_file
        self.likes = likes
        self.posts = posts

    users = pd.DataFrame()

    # for explicitly loading at startup *** No longer necessary --> keeping for testing
    @classmethod
    def load_users(cls):
        # added indices causing issues
        cls.users = pd.read_csv("data.csv")

    @classmethod
    def createUser(cls, email, username, password):
        # should not be used in loop --> O(n)
        cls.load_users()
        # trying to invoke flask_login for this user
        new_user = User(email, username, password, "", [], [])
        new_user = pd.DataFrame(
            [[email, username, password, "", [], []]], columns=cls.users.columns
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        cls.users.to_csv("data.csv", index=False)
        print("DataFrame columns: ", cls.users.columns)  # for testing

    def get_id(self):
        return self.email

    # overridden bc UserMixin was not providing correct values with dataFrame implementation
    @property  # @property -- need to be read-only, values stay the same when a user is registered + logged in
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True


# TODO: Address issue of maintaining data
# On app start retrieve user data -- Might be redundant (revisit at post implementation)
# write user data to a file when registering -- check
# use csv DF to add authentication

""" TODO: User classification: Differentiate SUs, from CUs, OUs, and Surfers
    - Inner class?
    - Another cloumn? """


""" TODO: Add balance maintenance
      # Every user starts with the same balance?
      # How do users add more? 
          - Account settings?"""

""" Skeleton of post structure
posts = pd.DataFrame(columns=['author','date', 'content', 'likes'])
"""

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#   https://pandas.pydata.org/docs/user_guide/io.html
# https://realpython.com/using-flask-login-for-user-management-with-flask/
"""
