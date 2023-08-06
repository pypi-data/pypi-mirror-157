import logging
import os

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from attune_project_api import ObjectStorageContext


logger = logging.getLogger(__name__)


def runMigrationsForStorageContext(storageContext: ObjectStorageContext):
    currentRev = storageContext.getRevision()

    # Create a temporary database file and an engine to it
    engine = create_engine("sqlite:///")
    # Load the alembic_version table and insert the project value into it
    engine.execute("CREATE TABLE alembic_version(version_num varchar)")
    engine.execute(
        f"INSERT INTO alembic_version (version_num) VALUES ('{currentRev}')"
    )
    # We don't seem to need a commit

    # Load the migration scripts and
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    latestRev = script.get_heads()[0]

    # The migration context expects a function to return an iterator of
    # revisions from a current revision (`revision`) to the destination
    # revision `latestRev`. The `script._upgrade_revs` method provides such
    # an iterator built from the scripts under `versions`
    def migrations_fn(revision, _ctx):
        return script._upgrade_revs(latestRev, revision)

    with engine.connect() as conn:
        context = MigrationContext.configure(
            connection=conn,
            opts={"transactional_ddl": False, "fn": migrations_fn},
        )

        if currentRev != latestRev:
            logger.info("Running migrations for Project API")
            storageContext.prepareWorkingBranch()
            context.run_migrations(storageContext=storageContext)
            storageContext.setRevision(latestRev)
            storageContext.squashAndMergeWorking(
                f"Migrate to {latestRev} revision"
            )


def getLatestRevision() -> str:
    codeDir = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(codeDir, "alembic.ini")
    migrationsDir = os.path.join(codeDir, "alembic_migrations")

    config = Config(file_=configFilePath)
    config.set_main_option("script_location", migrationsDir)
    script = ScriptDirectory.from_config(config)
    return script.get_heads()[0]
