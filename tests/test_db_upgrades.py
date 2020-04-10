import pytest
from web.api.user.colors import get_all_colors
from migrations.utils.image import (migrate_colors, extend_color_names_to_ids
        , replace_color_names)

def get_color_names_to_ids():
    return {bc.name: str(bc.id) for bc in get_all_colors()}

def get_color_ids_to_names():
    return {str(bc.id): bc.name for bc in get_all_colors()}

@pytest.mark.usefixtures('test_app', 'test_database')
@pytest.mark.parametrize('color', ['blue', 'pink', 'teal'])
def test_migration_from_color_names_to_ids(color):
    art = {color: [[0, 0]]}
    colors_to_ids = get_color_names_to_ids()
    migrated_art = migrate_colors(art, colors_to_ids)
    assert art[color] == migrated_art[colors_to_ids[color]]

@pytest.mark.usefixtures('test_app', 'test_database')
@pytest.mark.parametrize(
    'deprecated_color,color', [('orange','peach'), ('yellow','fluorescent yellow')]
)
def test_migration_from_deprecated_color_names_to_ids(deprecated_color, color):
    art = {deprecated_color: [[0, 0]]}
    colors_to_ids = extend_color_names_to_ids(get_color_names_to_ids())
    migrated_art = migrate_colors(art, colors_to_ids)
    assert art[deprecated_color] == migrated_art[colors_to_ids[color]]

@pytest.mark.usefixtures('test_app', 'test_database')
@pytest.mark.parametrize('color', ['blue', 'pink', 'teal'])
def test_downgrade_from_color_ids_to_names(color):
    color_names_to_ids = get_color_names_to_ids()
    color_ids_to_names = get_color_ids_to_names()
    color_id = color_names_to_ids[color]
    art = {color_id: [[0, 0]]}
    migrated_art = migrate_colors(art, color_ids_to_names)
    assert art[color_id] == migrated_art[color]

@pytest.mark.usefixtures('test_app', 'test_database')
@pytest.mark.parametrize(
    'deprecated_color,color', [('orange','peach'), ('yellow','fluorescent yellow')]
)
def test_migration_from_color_ids_to_deprecated_names(deprecated_color, color):
    color_names_to_ids = get_color_names_to_ids()
    color_ids_to_names = replace_color_names(get_color_ids_to_names())
    color_id = color_names_to_ids[color]
    art = {color_id: [[0, 0]]}
    migrated_art = migrate_colors(art, color_ids_to_names)
    assert art[color_id] == migrated_art[deprecated_color]
