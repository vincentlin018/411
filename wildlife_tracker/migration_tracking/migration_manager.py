from typing import Optional

from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath


class MigrationManager:
    def __init__(self) -> None:
        self.migrations: dict[int, Migration] = {}
        self.migration_paths: dict[int, MigrationPath] = {}

    def get_migration_by_id(self, migration_id: int) -> Optional[Migration]:
        pass

    def schedule_migration(self, migration: Migration) -> None:
        pass

    def cancel_migration(self, migration_id: int) -> None:
        pass

    def update_migration_details(self, migration_id: int, **kwargs) -> None:
        pass

    def create_migration_path(self, migration_path: MigrationPath) -> None:
        pass

    def remove_migration_path(self, path_id: int) -> None:
        pass

    def get_migration_path_by_id(self, path_id: int) -> Optional[MigrationPath]:
        pass