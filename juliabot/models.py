from __future__ import annotations

from datetime import datetime
from typing import List
from sqlalchemy import Column, String, Integer, DateTime, Boolean, and_, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from .config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Model(Base):
    __abstract__ = True

    def __init__(self, **data) -> None:
        super().__init__(**data)

        session.add(self)
        self.update()

    def delete(self) -> None:
        session.delete(self)
        self.update()

    def update(self) -> None:
        session.commit()

    @classmethod
    def select(cls, key: str, value: str) -> list:
        return session.query(cls).filter(getattr(cls, key) == value).all()

    @classmethod
    def select_one(cls, key: str, value):
        return session.query(cls).filter(getattr(cls, key) == value).first()

    @classmethod
    def select_all(cls) -> list:
        return session.query(cls).all()

    @classmethod
    def delete_all(cls):
        for i in cls.select_all().copy():
            i.delete()


class Server(Model):
    __tablename__ = "servers"

    server_id = Column(String, primary_key=True)
    prefix = Column(String, default="j!")
    anime_channel = Column(String)

    def __init__(self, server_id: str) -> None:
        super().__init__(server_id=server_id)

    def set_prefix(self, prefix: str) -> None:
        if not prefix:
            raise "Prefix can not be empty"

        self.prefix = prefix
        self.update()

    def set_anime_channel(self, channel_id: str):
        self.anime_channel = channel_id
        self.update()

    @classmethod
    def get(cls, server_id: str) -> Server | None:
        return cls.select_one(key="server_id", value=server_id)

    @classmethod
    def get_or_create(cls, server_id: str) -> Server:
        # Query a discord server in the database, if it doesn't exist insert a new one into it.
        server = cls.get(server_id)
        if not server:
            server = Server(server_id)

        return server


class Reminder(Model):
    __tablename__ = "reminder"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    message_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_reminder = Column(DateTime, nullable=False)

    def __init__(
        self, channel_id: str, message_id: str, user_id: str, time_reminder: datetime
    ) -> None:
        super().__init__(
            channel_id=channel_id,
            message_id=message_id,
            user_id=user_id,
            time_reminder=time_reminder,
        )

    @classmethod
    def get_expired(cls) -> List[Reminder]:
        return session.query(cls).filter(cls.time_reminder <= datetime.now()).all()


class AnimesNotifier(Model):
    __tablename__ = "animes_notifier"

    # My Anime List ID
    mal_id = Column(Integer, primary_key=True)
    episode = Column(Integer, primary_key=True)
    dubbed = Column(Boolean, primary_key=True, default=False)
    name = Column(String, nullable=False)
    image = Column(String, nullable=False)
    url = Column(String, nullable=False)
    site = Column(String, nullable=False)
    notified = Column(Boolean, nullable=False, default=False)

    def __init__(
        self,
        mal_id: int,
        episode: int,
        name: str,
        image: str,
        url: str,
        site: str,
        dubbed: bool = False,
    ) -> None:
        super().__init__(
            mal_id=mal_id,
            episode=episode,
            name=name,
            image=image,
            url=url,
            site=site,
            dubbed=dubbed,
        )

        self.keep_limit()

    def set_notified(self, notified: bool):
        self.notified = notified
        self.update()

    @classmethod
    def get_not_notified(cls) -> List[AnimesNotifier]:
        return session.query(cls).filter(cls.notified == False).all()

    @classmethod
    def get(cls, mal_id: int, episode: int, dubbed: bool) -> AnimesNotifier | None:
        return (
            session.query(cls)
            .filter(
                and_(cls.mal_id == mal_id, cls.episode == episode, cls.dubbed == dubbed)
            )
            .first()
        )

    @classmethod
    def keep_limit(cls):
        LIM = 1000
        rows = cls.select_all()

        if len(rows) > LIM:
            for i in range(len(rows) - LIM):
                rows[i].delete()


class AnimesList(Model):
    __tablename__ = "anime_list"

    user_id = Column(String, primary_key=True)
    mal_id = Column(Integer, primary_key=True)
    dubbed = Column(Boolean, primary_key=True, default=False)

    def __init__(self, user_id: str, mal_id: str, dubbed: bool = False) -> None:
        super().__init__(user_id=user_id, mal_id=mal_id, dubbed=dubbed)

    @classmethod
    def get(cls, user_id: str, mal_id: int, dubbed: bool) -> AnimesList | None:
        return (
            session.query(cls)
            .filter(
                and_(cls.user_id == user_id, cls.mal_id == mal_id, cls.dubbed == dubbed)
            )
            .first()
        )

    @classmethod
    def get_user(cls, user_id: str) -> List[AnimesList]:
        return session.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_anime(cls, mal_id: int, dubbed: bool = False) -> List[AnimesList]:
        return (
            session.query(cls)
            .filter(and_(cls.mal_id == mal_id, cls.dubbed == dubbed))
            .all()
        )


def init_db():
    Model.metadata.create_all(engine)
