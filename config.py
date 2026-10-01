import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Local development configuration.

    Uses a SQLite file on disk so the project runs immediately with no
    extra setup. To use MySQL instead (as shown in the lessons), set the
    DATABASE_URL environment variable to something like:
        mysql+mysqlconnector://root:<password>@localhost/mechanic_shop_db
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'mechanic_shop.db')}"
    )
    DEBUG = True


class TestingConfig(Config):
    """Configuration used by the automated unittest suite."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


class ProductionConfig(Config):
    """Production configuration. Point DATABASE_URL at a real server."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
