# File to maintain user data
# User has profile, messages/posts, likes

from flask import app
import pandas as pd
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import LoginManager, UserMixin
from datetime import datetime
from os import urandom


""" UserMixin - manages session user for us
       # is_authenticated()
       # is_active()
       # is_anonymous
       # get_id() """


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

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None

        # Assuming the user data is stored in the DataFrame users
        user_data = User.users[User.users["email"] == user_id]
        if user_data.empty:
            print("User not found for password reset.")
            return None

        # Assuming user_id is the email, you can access it like this
        user_id = user_data.iloc[0]["email"]

        # Returning the user_data or a User instance as needed
        user = User(
            email=user_data.iloc[0]["email"],
            username=user_data.iloc[0]["username"],
            password=user_data.iloc[0]["password"],
            image_file=user_data.iloc[0]["image_file"],
            likes=user_data.iloc[0]["likes"],
            posts=user_data.iloc[0]["posts"],
        )

        return user if isinstance(user, User) else None
           
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

    class Post:
        columns = [
            "title",
            "content",
            "username",
            "keywords",
            "date_posted",
            "post_id",
        ]
        posts = pd.DataFrame(columns=columns)
        # don't want any post to have the same id
        # TODO: Look into os.urandom
        post_id = int.from_bytes(urandom(1), "little")

        # check the syntax of this
        def __init__(self, title, content, username, keywords="", post_id=None):
            self.title = title
            self.content = content
            self.username = username
            self.keywords = keywords
            self.date_posted = datetime.utcnow()
            # keeps post_id from changing between updates
            if post_id is None:
                self.post_id = int.from_bytes(urandom(1), "little")
            else:
                self.post_id = post_id

        @classmethod
        def load_posts(cls):
            cls.posts = pd.read_csv("posts.csv")

        @classmethod
        def createPost(
            cls,
            title,
            content,
            username,
            keywords,
            date_posted=datetime.utcnow(),
        ):
            cls.load_posts()
            new_post = pd.DataFrame(
                [
                    [
                        title,
                        content,
                        username,
                        keywords,
                        date_posted.strftime("%m-%d-%Y"),
                        cls.post_id,
                    ]
                ],
                columns=cls.posts.columns,
            )

            cls.posts = pd.concat([cls.posts, new_post], ignore_index=True)
            cls.posts.to_csv("posts.csv", header="posts", index=False)

            print("Current posts: ", cls.posts)

        @classmethod
        def postUserPair(cls, post_id):
            # pandas indexing error without int casting
            # find the post with the same post_id
            User.load_users()
            users = User.users

            post = cls.posts[cls.posts["post_id"] == post_id].iloc[0]
            user = users[users["username"] == post.username].iloc[0]

            return post, user

        # common function
        # TODO: check if can be used outside of User
        @classmethod
        def findPost(cls, post):
            cls.load_posts()

            # find the index of the post with an existing post_id
            if not cls.posts[cls.posts["post_id"] == post.post_id].empty:
                post_index = cls.posts[cls.posts["post_id"] == post.post_id].index[0]

            return post_index

        @classmethod
        def updatePost(cls, post):
            # check
            post_index = cls.findPost(post)

            if post_index is not None:
                cls.posts.loc[post_index, ["title", "content", "keywords"]] = [
                    post.title,
                    post.content,
                    post.keywords,
                ]
                cls.posts.to_csv("posts.csv", index=False)
            else:
                print("Post does not exist")

        @classmethod
        def deletePost(cls, post):
            post_index = cls.findPost(post)
            if post_index is not None:
                cls.posts.drop(index=post_index, inplace=True)
                cls.posts.to_csv("posts.csv", index=False)
            else:
                print("Post does not exist")


User.Post.load_posts()
post = User.Post.posts.iloc[0]
User.Post.postUserPair(post.post_id)
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
