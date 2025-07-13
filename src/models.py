from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base


followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followee_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    avatar_url = Column(String)

    followers = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.followee_id,   # кто на меня подписан
        secondaryjoin=id == followers_table.c.follower_id, # я подписан на кого-то
        backref="following"                                # кого я читаю
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    media_ids = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))  # внешний ключ на таблицу users
    user = relationship("User", backref="tweets")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # внешний ключ на таблицу users
    user = relationship("User", backref="likes")  # объектная связь
    tweet_id = Column(Integer, ForeignKey("tweets.id"))  # внешний ключ на таблицу users
    tweet = relationship("Tweet", backref="likes")  # объектная связь


# class Link(Base):
#     __tablename__ = "links"
#
#     id = Column(Integer, primary_key=True, index=True)
#     link = Column(String, nullable=False)
#     tweet_id = Column(Integer, ForeignKey("tweets.id"))  # внешний ключ на таблицу tweets
#     tweet = relationship("Tweet", backref="links")  # объектная связь


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="medias")