from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from _utils import mock_list, mock_dict
from database import database


class TestDatabase(TestCase):
    @patch("database.database.sa_select")
    def test__select__no_args(self, sa_select_patch: MagicMock):
        entity = MagicMock()

        result = database.select(entity)

        sa_select_patch.assert_called_once_with(entity)
        self.assertEqual(sa_select_patch(), result)

    @patch("database.database.selectinload")
    @patch("database.database.sa_select")
    def test__select__with_args(self, sa_select_patch: MagicMock, selectinload_patch: MagicMock):
        entity = MagicMock()

        result = database.select(
            entity,
            a := MagicMock(),
            b := MagicMock(),
            [c := MagicMock(), d := MagicMock(), e := MagicMock()],
            [f := MagicMock()],
        )

        selectinload_patch.assert_has_calls(
            [
                call(a),
                call(b),
                call(c),
                call().selectinload(d),
                call().selectinload().selectinload(e),
                call(f),
            ],
        )

        sa_select_patch.assert_called_once_with(entity)
        sa_select_patch().options.assert_called_once_with(
            selectinload_patch(),
            selectinload_patch(),
            selectinload_patch().selectinload().selectinload(),
            selectinload_patch(),
        )
        self.assertEqual(sa_select_patch().options(), result)

    @patch("database.database.select")
    def test__filter_by(self, select_patch: MagicMock):
        cls = MagicMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.filter_by(cls, *args, **kwargs)

        select_patch.assert_called_once_with(cls, *args)
        select_patch().filter_by.assert_called_once_with(**kwargs)
        self.assertEqual(select_patch().filter_by(), result)

    @patch("database.database.sa_exists")
    def test__exists(self, sa_exists_patch: MagicMock):
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.exists(*args, **kwargs)

        sa_exists_patch.assert_called_once_with(*args, **kwargs)
        self.assertEqual(sa_exists_patch(), result)

    @patch("database.database.sa_delete")
    def test__delete(self, sa_delete_patch: MagicMock):
        table = MagicMock()

        result = database.delete(table)

        sa_delete_patch.assert_called_once_with(table)
        self.assertEqual(sa_delete_patch(), result)
