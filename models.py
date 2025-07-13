from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base


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
    author_id = Column(Integer, nullable=False)