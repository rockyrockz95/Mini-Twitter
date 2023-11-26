# File to maintain user data
# User has profile, messages/posts, likes

import pandas as pd
from flask_login import LoginManager, UserMixin
from datetime import datetime
from random import randint


# TODO: Implement unique key classification/establish relationships, post_id/author with User


""" UserMixin - manages session user for us
       # is_authenticated()
       # is_active()
       # is_anonymous
       # get_id()
"""
# TODO: Check if UserMixin is necessary with properties explicitly defined


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

    # for explicitly loading at startup
    @classmethod
    def load_users(cls):
        # added indices causing issues
        cls.users = pd.read_csv("data.csv")

    @classmethod
    def createUser(
        cls, email, username, password, image_file="profile_pics/default.png"
    ):
        cls.load_users()
        # trying to invoke flask_login for this user
        new_user = User(email, username, password, "", [], [])
        new_user = pd.DataFrame(
            [[email, username, password, image_file, [], []]],
            columns=cls.users.columns,
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        cls.users.to_csv("data.csv", index=False)
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
            cls.users.to_csv("data.csv", index=False)
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

    # Approach 3: save posts in different DataFrame, associate posts with users
    #    via post_id

    class Post:
        columns = ["title", "content", "username", "post_id", "date_posted"]
        posts = pd.DataFrame(columns=columns)
        # don't want any post to have the same id
        post_id = 0

        # check the syntax of this
        def __init__(self, title, content, username, post_id=None):
            self.title = title
            self.content = content
            self.username = username
            self.date_posted = datetime.utcnow()
            # keeps post_id from changing between updates
            if self.post_id == None:
                self.post_id = randint(0, 1000)
            else:
                self.post_id = post_id

        @classmethod
        def load_posts(cls):
            cls.posts = pd.read_csv("posts.csv")

        @classmethod
        def createPost(cls, title, content, username, date_posted=datetime.utcnow()):
            cls.load_posts()
            new_post = pd.DataFrame(
                [
                    [
                        title,
                        content,
                        username,
                        cls.post_id,
                        date_posted.strftime("%m-%d-%Y"),
                    ]
                ],
                columns=cls.posts.columns,
            )

            cls.posts = pd.concat([cls.posts, new_post], ignore_index=True)
            cls.posts.to_csv("posts.csv", header="posts", index=False)

            print("Current posts: ", cls.posts)

        @classmethod
        def updatePost(cls, post):
            cls.load_posts()

            # find the index of the post with an existing post_id
            if not cls.posts[cls.posts["post_id"] == post.post_id].empty:
                post_index = cls.posts[cls.posts["post_id"] == post.post_id].index[0]
            # TODO: ALL lines above this can be made into a seperate func, called again in next method

            if post_index is not None:
                cls.posts.loc[post_index, ["title", "content"]] = [
                    post.title,
                    post.content,
                ]
                cls.posts.to_csv("posts.csv", index=False)
            else:
                print("Post does not exist")

        @classmethod
        def deletePost(cls, post):
            cls.load_posts()

            if not cls.posts[cls.posts["post_id"] == post.post_id].empty:
                post_index = cls.posts[cls.posts["post_id"] == post.post_id].index[0]

            if post_index is not None:
                cls.posts.drop(index=post_index, inplace=True)
                cls.posts.to_csv("posts.csv", index=False)
            else:
                print("Post does not exist")


# User.Post.load_posts()
# for index, post in User.Post.posts.iterrows():
#     print(post)

""" TODO: User classification: Differentiate SUs, from CUs, OUs, and Surfers
    - Inner class?
    - Another cloumn? """


# https://stackoverflow.com/questions/30829748/multiple-pandas-dataframe-to-one-csv-file : multiple dataFrames vertically

""" TODO: Add balance maintenance
      # Every user starts with the same balance?
      # How do users add more? 
          - Account settings?"""

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#   https://pandas.pydata.org/docs/user_guide/io.html
#   https://realpython.com/using-flask-login-for-user-management-with-flask/
#   Column as Index Example: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html#pandas.DataFrame.reset_index
#   Datetime Code Used: https://www.geeksforgeeks.org/python-strftime-function/
"""
