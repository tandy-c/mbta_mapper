"""Module for creating a flask app and setting the config for the app"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, session
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import select, delete, insert, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload, scoped_session


from .feed import Feed
from .gtfs_base import GTFSBase
from gtfs_realtime import Vehicle, Prediction, Alert
from gtfs_schedule import Route, Shape, Stop
from poll_mbta_data import predictions, vehicles, alerts


class FlaskApp:
    """Class for creating a flask app and setting the config for the app"""

    orm_func_mapper = {
        Vehicle: vehicles.get_vehicles,
        Alert: alerts.get_alerts,
        Prediction: predictions.get_predictions,
    }

    def __init__(self, app: Flask, feeds: list[Feed]) -> None:
        self.app = app
        self.feeds = {feed.route_type: feed for feed in feeds}
        self.update_app_config()
        self.db = self.return_db()

    def __repr__(self) -> str:
        return f"<FlaskApp {self.app.name} {','.join(self.feeds)}>"

    def return_db(self) -> SQLAlchemy:
        return SQLAlchemy(self.app)

    def update_app_config(self, config_dict: dict[str] = None) -> None:
        """Sets the config for the flask app

        Args:
            config_dict (dict[str]): dictionary of config values, defaults to
            {"SQLALCHEMY_DATABASE_URI": self.feed.engine.url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        """

        config_dict = config_dict or {
            "SQLALCHEMY_DATABASE_URI": str(next(iter(self.feeds.values())).engine.url),
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_BINDS": {k: str(v.engine.url) for k, v in self.feeds.items()},
        }

        self.app.config.update(config_dict)

    def query_and_return_vehicles(self) -> list[tuple[Vehicle]]:
        """Downloads realtime data from the mbta api and returns active vehicles.
        Note that this method also deletes all realtime data from the database and replaces it

        Returns:
            list[tuple[Vehicle]]: list of vehicles"""

        vehicle_list = []
        for route_type, feed in self.feeds.items():
            active_routes = ",".join(
                item[0]
                for item in feed.session.execute(
                    select(Route.route_id).distinct()
                ).all()
            )

            for orm, function in FlaskApp.orm_func_mapper.items():
                data = function(route_type if orm != Prediction else active_routes)
                try:
                    feed.session.execute(delete(orm))
                    feed.session.execute(
                        insert(orm), data.to_dict(orient="records", index=True)
                    )
                except IntegrityError:
                    feed.session.rollback()
                feed.session.commit()
            vehicle_list += feed.session.execute(select(Vehicle)).all()
            feed.session.close()

        return vehicle_list

    def return_data(self, orm: GTFSBase) -> list[tuple[GTFSBase]]:
        data = []
        for feed in self.feeds.values():
            data += feed.session.execute(select(orm)).all()
            feed.session.close()
