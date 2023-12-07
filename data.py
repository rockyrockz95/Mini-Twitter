# File to maintain user data
# User has profile, messages/posts, likes

from flask import app
import pandas as pd
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import LoginManager, UserMixin
from datetime import datetime
from os import urandom
import re

""" UserMixin - manages session user for us
       # is_authenticated()
       # is_active()
       # is_anonymous
       # get_id() """


class User(UserMixin):
    def __init__(self, email, username, password, user_role, balance, warnings, image_file, posts):
        self.id = email
        self.email = email
        self.username = username
        self.password = password
        self.user_role = user_role
        self.balance = balance
        self.warnings = warnings
        self.image_file = image_file
        self.posts = posts

    users = pd.DataFrame()

    def get_reset_token(self):
        s = Serializer(app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=expires_sec)["user_id"]
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
            user_role=user_data.iloc[0]["user_role"],
            balance=user_data.iloc[0]["balance"],
            warnings=user_data.iloc[0]["warnings"],
            image_file=user_data.iloc[0]["image_file"],
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
        cls, email, username, password, user_role, balance=100, warnings=0, image_file="profile_pics/default.png"
    ):
        cls.load_users()
        new_user = pd.DataFrame(
            [[email, username, password, user_role, balance, warnings, image_file, []]],
            columns=cls.users.columns,
        )
        cls.users = pd.concat([cls.users, new_user], ignore_index=True)
        cls.users.to_csv("data.csv", index=False)
        print("Registered users: ", cls.users)



    @classmethod
    def removeUser(cls, username):  # Function solely meant for Super Users
        cls.load_users()
        if not cls.users[cls.users["username"] == username].empty:
            # Remove the user
            cls.users = cls.users[cls.users["username"] != username]
            cls.users.to_csv("data.csv", index=False)
            # Remove user posts
            User.Post.removeUserPosts(username)
            print("User removed:", username)
        else:
            print("User not found:", username)

    @classmethod
    def updateUser(cls, curr_user):
        cls.load_users()
        # find the index of the user with an existing email
        # have to use email as search parameter if username is being changes, vice-versa
        if not cls.users[cls.users["username"] == curr_user.username].empty:
            user_index = cls.users[cls.users["username"]
                                   == curr_user.username].index[0]
        elif not cls.users[cls.users["email"] == curr_user.email].empty:
            user_index = cls.users[cls.users["email"]
                                   == curr_user.email].index[0]
        # not condition: iloc returns IndexError for empty dataFrame

        # update the user parameter in the databases
        if user_index is not None:
            cls.users.loc[user_index] = [
                curr_user.email,
                curr_user.username,
                curr_user.password,
                curr_user.user_role,
                curr_user.balance,
                curr_user.warnings,
                curr_user.image_file,
                curr_user.posts,
            ]
            cls.users.to_csv("data.csv", index=False)
        else:
            print("Unable to update unknown user")

    @classmethod
    def add_warning(cls, username):
        cls.load_users()
        # Check if the user exists
        if not cls.users[cls.users['username'] == username].empty:
            # Increment the warning count for the user
            cls.users.loc[cls.users['username'] == username, 'warnings'] += 1
            cls.users.to_csv('data.csv', index=False)
            print("Warning added to user:", username)
        else:
            print("User not found:", username)

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
            "media",
            "keywords",
            # could be an int, int, user pair -- determine which
            "likes",
            "dislikes",
            # TODO: make a choice, ad or standard --> account balance monitor; Make setter
            "type",
            "views",
            "complaints",
            "date_posted",
            "post_id",
        ]
        like_cols = ["username", "post_id"]
        complaint_cols = ["username", "post_id", "content"]

        posts = pd.DataFrame(columns=columns)

        # lists in DFs difficult to work with
        likes = pd.DataFrame(columns=like_cols)
        likes.set_index("post_id", drop=False, inplace=True)
        dislikes = pd.DataFrame(columns=like_cols)
        dislikes.set_index("post_id", drop=False, inplace=True)
        complaints = pd.DataFrame(columns=complaint_cols)
        complaints.set_index("post_id", drop=False, inplace=True)

        # don't want any post to have the same id
        post_id = int.from_bytes(urandom(1), "little")

        # check the syntax of this
        def __init__(
            self, title, content, username, media="", keywords="", complaints=0, post_id=None
        ):
            self.title = title
            self.content = content
            self.username = username
            self.media = media
            self.keywords = keywords
            self.likes = 0
            self.dislikes = 0
            self.type = "standard"
            self.views = 0
            self.complaints = complaints
            self.date_posted = datetime.utcnow()
            # keeps post_id from changing between updates
            if post_id is None:
                self.post_id = int.from_bytes(urandom(1), "little")
            else:
                self.post_id = post_id

        @classmethod
        def load_posts(cls):
            cls.posts = pd.read_csv("posts.csv")
            cls.likes = pd.read_csv("likes.csv")
            cls.dislikes = pd.read_csv("dislikes.csv")
            cls.complaints = pd.read_csv("complaints.csv")

        @classmethod
        def createPost(
            cls,
            title,
            content,
            username,
            keywords,
            media="",
            likes=0,
            dislikes=0,
            type="standard",
            views=0,
            complaints=0,
            date_posted=datetime.utcnow(),
        ):
            cls.load_posts()
            new_post = pd.DataFrame(
                [
                    [
                        title,
                        content,
                        username,
                        media,
                        keywords,
                        likes,
                        dislikes,
                        type,
                        views,
                        complaints,
                        date_posted.strftime("%m-%d-%Y"),
                        cls.post_id,
                    ]
                ],
                columns=cls.posts.columns,
            )

            cls.posts = pd.concat([cls.posts, new_post], ignore_index=True)
            cls.posts.to_csv("posts.csv", header="posts", index=False)

            print("Current posts: ", cls.posts)

        # primarily for user initiated updates
        @classmethod
        def updatePost(cls, post):
            # check
            post_index = cls.findPost(post)

            if post_index is not None:
                cls.posts.loc[post_index, ["title", "content", "media", "keywords"]] = [
                    post.title,
                    post.content,
                    post.media,
                    post.keywords,
                ]
                cls.posts.to_csv("posts.csv", index=False)
            else:
                print("Post does not exist")

        @classmethod
        def deletePost(cls, post):
            post_index = cls.findPost(post)
            if post_index is not None:
                post_id = cls.posts.loc[post_index, "post_id"]
                # Remove associated complaints, likes, and dislikes
                cls.complaints = cls.complaints[cls.complaints["post_id"] != post_id]
                cls.likes = cls.likes[cls.likes["post_id"] != post_id]
                cls.dislikes = cls.dislikes[cls.dislikes["post_id"] != post_id]
                # Delete the post
                cls.posts.drop(index=post_index, inplace=True)
                cls.posts.to_csv("posts.csv", index=False)
                # Save updated likes, dislikes, and complaints
                cls.likes.to_csv("likes.csv", index=False)
                cls.dislikes.to_csv("dislikes.csv", index=False)
                cls.complaints.to_csv("complaints.csv", index=False)
            else:
                print("Post does not exist")

        @classmethod
        def deletePostById(cls, post_id):  # Function solely meant for Super Users
            cls.load_posts()
            # Find and delete post with matching post_id
            if not cls.posts[cls.posts["post_id"] == post_id].empty:
                cls.posts = cls.posts[cls.posts["post_id"] != post_id]
                cls.posts.to_csv("posts.csv", index=False)
                print("Post with ID", post_id, "has been deleted")
            else:
                print("Post with ID", post_id, "not found")

        @classmethod
        def removeUserPosts(cls, username):  # Function solely meant for Super Users
            cls.load_posts()
            # Filter out post by specified username
            cls.posts = cls.posts[cls.posts["username"] != username]
            cls.posts.to_csv("posts.csv", index=False)
            print("Posts removed for user:", username)

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
        @classmethod
        def findPost(cls, post):
            cls.load_posts()

            # find the index of the post with an existing post_id
            if not cls.posts[cls.posts["post_id"] == post.post_id].empty:
                post_index = cls.posts[cls.posts["post_id"]
                                       == post.post_id].index[0]

            return post_index

        @classmethod
        def sresults(cls, attribute, sterm):
            cls.load_posts()
            if attribute == "username" or attribute == "keywords":
                # results not case-sensitive
                post = cls.posts[cls.posts[attribute].str.lower()
                                 == sterm.lower()]

            elif attribute == "likes" or attribute == "dislikes":
                # Only numeric values allowed
                try:
                    sterm = int(sterm)
                    post = cls.posts[cls.posts[attribute] >= sterm]
                except ValueError:
                    print("Invalid input for likes/dislikes")

            if not post.empty:
                return post
            else:
                print("Post does not exist")
                return None

        @classmethod
        def add_like(cls, post_id, curr_username):
            post = cls.postUserPair(post_id)[0]
            post_index = cls.findPost(post)
            # why is this causing an error
            like_row = cls.likes.loc[
                (cls.likes["username"] == curr_username)
                & (cls.likes["post_id"] == post_id)
            ]
            new_row = pd.DataFrame(
                {"post_id": [post_id], "username": [curr_username]})

            if not like_row.empty:
                print("Already liked post")
                return 0
            else:
                cls.posts.loc[post_index, "likes"] += 1
                cls.likes = pd.concat([cls.likes, new_row], ignore_index=True)

                # save like data
                cls.posts.to_csv("posts.csv", index=False)
                cls.likes.to_csv("likes.csv", index=False)
                return 1

        # TU: likes - dislikes
        @classmethod
        def add_dislike(cls, post_id, curr_username):
            post = cls.postUserPair(post_id)[0]
            post_index = cls.findPost(post)
            # why is this causing an error
            dislike_row = cls.dislikes.loc[
                (cls.dislikes["username"] == curr_username)
                & (cls.dislikes["post_id"] == post_id)
            ]
            new_row = pd.DataFrame(
                {"post_id": [post_id], "username": [curr_username]})

            if not dislike_row.empty:
                print("Already liked post")
                return 0
            else:
                cls.posts.loc[post_index, "dislikes"] += 1
                cls.dislikes = pd.concat(
                    [cls.dislikes, new_row], ignore_index=True)

                # save like data
                cls.posts.to_csv("posts.csv", index=False)
                cls.dislikes.to_csv("dislikes.csv", index=False)
                return 1

        # method for updating views
        # TODO: not updating
        @classmethod
        def add_view(cls, post):
            post_index = cls.findPost(post)
            cls.posts.loc[post_index, "views"] += 1
            cls.posts.to_csv("posts.csv", index=False)

        @classmethod
        def createComplaint(cls, post_id, username, content):
            cls.load_posts()
            new_complaint = pd.DataFrame(
                [[post_id, username, content]], columns=cls.complaint_cols
            )
            cls.complaints = pd.concat(
                [cls.complaints, new_complaint], ignore_index=True
            )
            cls.complaints.to_csv("complaints.csv", index=False)

            cls.posts.loc[cls.posts["post_id"] == post_id, "complaints"] += 1
            cls.posts.to_csv("posts.csv", index=False)

        @classmethod
        def load_taboo_words(cls):
            try:
                taboo_words_df = pd.read_csv("taboo_word_list.csv")
                return taboo_words_df["banned_words"].tolist()
            except FileNotFoundError:
                return []

        @staticmethod
        def add_taboo_word(word):
            taboo_words = pd.read_csv("taboo_word_list.csv")
            new_word = pd.DataFrame([word], columns=["banned_words"])
            taboo_words = pd.concat([taboo_words, new_word], ignore_index=True)
            taboo_words.to_csv("taboo_word_list.csv", index=False)

        @staticmethod
        def remove_taboo_word(word):
            taboo_words = pd.read_csv("taboo_word_list.csv")
            taboo_words = taboo_words[taboo_words["banned_words"] != word]
            taboo_words.to_csv("taboo_word_list.csv", index=False)

        @classmethod
        def censor_taboo_words(cls, text):
            taboo_words = cls.load_taboo_words()
            for word in taboo_words:
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                text = pattern.sub("*" * len(word), text)
            return text
        
    

        """
        # method for displaying top posts
            # criteria: post has > 10 views && #likes - # dislikes > 3
            # strategy: find the 3 posts with > 10 views (assume they exist)
                        determine if #likes - #dislikes > 3
                        sort last for display
                        return those to home.html """

        @classmethod
        def trend_posts(cls):
            cls.load_posts()
            # results sorted by views
            most_viewed = cls.posts[cls.posts["views"] > 10]
            trendy_posts = most_viewed[
                (most_viewed["likes"] - most_viewed["dislikes"]) > 3
            ]
            top3 = trendy_posts.iloc[:3]
            return top3


User.Post.trend_posts()
# User.Post.load_posts()
# for index, post in User.Post.posts.iterrows():
#     print(post)


# https://stackoverflow.com/questions/30829748/multiple-pandas-dataframe-to-one-csv-file : multiple dataFrames vertically

""" TODO: Add balance maintenance
      # Every user starts with the same balance?
      # How do users add more? 
          - Account settings? """

""" Sources: 
#   https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#   https://pandas.pydata.org/docs/user_guide/io.html
#   https://realpython.com/using-flask-login-for-user-management-with-flask/
#   Column as Index Example: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html#pandas.DataFrame.reset_index
#   Datetime Code Used: https://www.geeksforgeeks.org/python-strftime-function/
"""
