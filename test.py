"""Test"""
import os
import logging
from dotenv import load_dotenv

# from sqlalchemy import select

from gtfs_loader.feed import Feed
from gtfs_realtime import Alert
from shared_code.gtfs_helper_time_functions import get_date

load_dotenv()


def nightly_import() -> None:
    """Runs the nightly import.

    Args:
        date: The date to import. Defaults to today."""

    logging.getLogger().setLevel(logging.INFO)
    feed = Feed("https://cdn.mbta.com/MBTA_GTFS.zip", get_date())
    # feed.import_gtfs()
    # feed.purge_and_filter()
    # feed.delete_old_databases()
    geojson_path = os.path.join(os.getcwd(), "static", "geojsons")
    for key in os.getenv("LIST_KEYS").split(","):
        Alert().get_realtime(feed.session, os.environ.get(key))
        feed.export_geojsons(key, geojson_path)


if __name__ == "__main__":
    nightly_import()
    # feed = Feed("https://cdn.mbta.com/MBTA_GTFS.zip", get_date())
    # feed.session.execute(select(Vehicle)).all()
    # app.run(debug=True, host="


# logging.getLogger().setLevel(logging.INFO)
# schedule.every().day.at("00:00", tz="America/New_York").do(nightly_import, None)
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # wait one minute
