# File to maintain user data
# User has profile, messages/posts, likes

import pandas as pd
from flask_login import LoginManager, UserMixin
from datetime import datetime


# TODO: Implement unique key classification/establish relationships, post_id/author with User


""" UserMixin - manages session user for us
       # is_authenticated()
       # is_active()
       # is_anonymous
       # get_id()
"""
# TODO: Check if UserMixin is necessary with properties explicitly defined


# no foreign key function in pandas
# not calling yet, returns an error
# in the merged table, when a user is added without a post, NaN is entered for the post column values
def mergeData():
    User.load_users()
    user_post_df = pd.merge(Post.posts, User.users, on="username", how="left")
    user_post_df.to_csv("test.csv", index=False)


class User(UserMixin):
    def __init__(self, email, username, password, image_file, likes, posts):
        self.id = email
        self.email = email
        self.username = username
        self.password = password
        self.image_file = image_file
        self.likes = likes

    users = pd.DataFrame()

    # for explicitly loading at startup
    @classmethod
    def load_users(cls):
        # added indices causing issues
        cls.users = pd.read_csv("test.csv")

    @classmethod
    def createUser(cls, email, username, password, image_file="static\default.png"):
        cls.load_users()
        # trying to invoke flask_login for this user
        new_user = User(email, username, password, "", [], [])
        new_user = pd.DataFrame(
            [[email, username, password, image_file, []]],
            columns=cls.users.columns,
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        cls.users.to_csv("test.csv", index=False)
        print("Registered users: ", cls.users)

    @classmethod
    def updateUser(cls, curr_user):
        cls.load_users()
        # find the index of the user with an existing email
        # have to use email as search parameter if username is being changes, vice-versa
        if not cls.users[cls.users["username"] == curr_user.username].empty:
            user_index = cls.users[cls.users["username"] == curr_user.username].index[0]
        elif not cls.users[cls.users["email"] == curr_user.email].empty:
            user_index = cls.users[cls.users["email"] == curr_user.email].index[0]
        # not condition: iloc returns IndexError for empty dataFrame

        # update the user parameterin the databases
        if user_index is not None:
            cls.users.loc[user_index] = [
                curr_user.email,
                curr_user.username,
                curr_user.password,
                curr_user.image_file,
                curr_user.likes,
                curr_user.posts,
            ]
            cls.users.to_csv("test.csv", index=False)
        else:
            print("Unable to update unknown user")

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


""" TODO: User classification: Differentiate SUs, from CUs, OUs, and Surfers
    - Inner class?
    - Another cloumn? """


class Post:
    # username = user_id bc it should be shown on posts
    columns = ["title", "content", "username", "post_id", "date_posted"]
    posts = pd.DataFrame(columns=columns)
    # TODO: change to make it dependent on index of post in DataFrame
    post_id = 0

    # for invoking and creating merged table
    def __init__(self, title, content, username, post_id, date_posted):
        self.title = title
        self.content = content
        self.username = username
        self.post_id = post_id
        self.date_posted = datetime.utcnow

    @classmethod
    def createPost(cls, title, content, username, date_posted=datetime.utcnow):
        new_post = pd.DataFrame(
            [[title, content, username, cls.post_id, date_posted]],
            columns=cls.posts.columns,
        )

        cls.posts = pd.concat([cls.posts, new_post], ignore_index=True)
        cls.posts.to_csv("test.csv", index=False)

        cls.post_id += 1
        print("Current posts: ", cls.posts)


# https://stackoverflow.com/questions/30829748/multiple-pandas-dataframe-to-one-csv-file : multiple dataFrames vertically

""" TODO: Add balance maintenance
      # Every user starts with the same balance?
      # How do users add more? 
          - Account settings?"""

""" Skeleton of post structure
posts = pd.DataFrame(columns=['author','date', 'content', 'likes'])
    # Give posts an id? --> Easier to hold in User csv
"""

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#   https://pandas.pydata.org/docs/user_guide/io.html
# https://realpython.com/using-flask-login-for-user-management-with-flask/
"""
