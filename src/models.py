"""SQLAlchemy models for the Twitter clone application."""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from .database import Base

# Association table for user followers (many-to-many relationship)
followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followee_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    """
    Represents a user in the system.

    Users can follow each other and have tweets, likes, and media uploads.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    avatar_url = Column(String)

    followers = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.followee_id,  # users who follow this user
        secondaryjoin=id == followers_table.c.follower_id,  # users this user follows
        backref="following",  # users that this user is following
    )


class Tweet(Base):
    """
    Represents a tweet created by a user.

    A tweet can contain text and associated media.
    """

    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    media_ids = Column(String, nullable=True)
    author_id = Column(
        Integer, ForeignKey("users.id")
    )  # Foreign key to the users table
    user = relationship("User", backref="tweets")  # Reference to the tweet's author


class Like(Base):
    """Represents a like given by a user to a tweet."""

    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Foreign key to the users table
    user = relationship("User", backref="likes")  # Reference to the user who liked
    tweet_id = Column(
        Integer, ForeignKey("tweets.id")
    )  # Foreign key to the tweets table
    tweet = relationship("Tweet", backref="likes")  # Reference to the liked tweet


class Media(Base):
    """Represents a media file uploaded by a user."""

    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Foreign key to the users table
    user = relationship("User", backref="medias")  # Reference to the uploading user
