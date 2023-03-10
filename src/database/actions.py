from uuid import UUID

from fastapi import Depends
from sqlalchemy import exists, func, select
from sqlalchemy.sql import Subquery

from src.database.crud import BaseORM
from src.database.database import AbstractAsyncSession, get_db
from src.models import Dish, Menu, SubMenu


class MenuAction(BaseORM):
    def __init__(self, db: AbstractAsyncSession):
        self.model = Menu
        self.db = db

    async def check_exist_menu(self, menu_id: UUID) -> bool:
        async with self.db as db:
            result = await db.session.execute(
                exists(self.model).where(self.model.id == menu_id).select()
            )
        if result.scalars().first():
            return True
        return False

    async def _get_subquery_dishes(self) -> "Subquery":
        return (
            select(
                SubMenu.menu_id.label("menu_id"),
                func.coalesce(func.count(SubMenu.dishes), 0).label("dishes"),
            )
            .outerjoin(Dish)
            .group_by(SubMenu.menu_id)
            .subquery()
        )

    async def _query_for_get(self, sq: "Subquery") -> "select":
        return (
            select(
                self.model.id,
                self.model.title,
                self.model.description,
                func.count(self.model.submenus).label("submenus_count"),
                func.coalesce(sq.c.dishes, 0).label("dishes_count"),
            )
            .outerjoin(SubMenu, SubMenu.menu_id == self.model.id)
            .outerjoin(sq, sq.c.menu_id == self.model.id)
            .group_by(self.model.id, sq.c.dishes)
        )

    async def get_all_with_relates(self, skip: int = 0, limit: int = 100) -> list[Menu]:
        async with self.db as db:
            sq = await self._get_subquery_dishes()
            queryset = await self._query_for_get(sq)
            result = await db.session.execute(queryset.offset(skip).limit(limit))
        return result.all()

    async def get_with_relates(self, menu_id: UUID) -> Menu | None:
        async with self.db as db:
            sq = await self._get_subquery_dishes()
            queryset = await self._query_for_get(sq)
            result = await db.session.execute(queryset.filter(self.model.id == menu_id))
        return result.first()

    async def get_all_data(self):
        async with self.db as db:
            stmt = (
                select(
                    Menu.title.label("menu_title"),
                    Menu.description.label("menu_description"),
                    SubMenu.title.label("submenu_title"),
                    SubMenu.description.label("submenu_description"),
                    Dish.title,
                    Dish.description,
                    Dish.price,
                )
                .join(SubMenu, Menu.id == SubMenu.menu_id)
                .join(Dish, SubMenu.id == Dish.submenu_id)
            )
            result = await db.session.execute(stmt)
        return result.all()


class SubMenuAction(BaseORM):
    def __init__(self, db: AbstractAsyncSession):
        self.model = SubMenu
        self.db = db

    async def check_exist_menu(self, menu_id: UUID) -> bool:
        async with self.db as db:
            result = await db.session.execute(
                exists(Menu).where(Menu.id == menu_id).select()
            )
        if result.scalars().first():
            return True
        return False

    async def check_exist_submenu(self, submenu_id: UUID, menu_id: UUID) -> bool:
        async with self.db as db:
            result = await db.session.execute(
                exists(self.model)
                .where(
                    self.model.id == submenu_id,
                    self.model.menu_id == menu_id,
                )
                .select(),
            )
        if result.scalars().first():
            return True
        return False

    async def _query_for_get(self, menu_id: UUID) -> "select":
        return (
            select(
                self.model.id,
                self.model.title,
                self.model.description,
                func.coalesce(func.count(Dish.id), 0).label("dishes_count"),
            )
            .outerjoin(Dish, self.model.id == Dish.submenu_id)
            .group_by(self.model.id)
            .filter(self.model.menu_id == menu_id)
        )

    async def get_with_relates(self, submenu_id: UUID, menu_id: UUID) -> SubMenu | None:
        async with self.db as db:
            queryset = await self._query_for_get(menu_id)
            result = await db.session.execute(
                queryset.filter(self.model.id == submenu_id)
            )
        return result.first()

    async def get_all_with_relates(
        self, menu_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[SubMenu]:
        async with self.db as db:
            queryset = await self._query_for_get(menu_id)
            result = await db.session.execute(queryset.offset(skip).limit(limit))
        return result.all()


class DishAction(BaseORM):
    def __init__(self, db: AbstractAsyncSession):
        self.model = Dish
        self.db = db

    async def check_exist_submenu(self, submenu_id: UUID, menu_id: UUID) -> bool:
        async with self.db as db:
            result = await db.session.execute(
                exists(SubMenu)
                .where(
                    SubMenu.id == submenu_id,
                    SubMenu.menu_id == menu_id,
                )
                .select(),
            )
        if result.scalars().first():
            return True
        return False

    async def check_exist_dish(self, submenu_id: UUID, dish_id: UUID) -> bool:
        async with self.db as db:
            result = await db.session.execute(
                select(
                    exists(self.model).where(
                        self.model.id == dish_id,
                        self.model.submenu_id == submenu_id,
                    ),
                ).select(),
            )
        if result.scalars().first():
            return True
        return False

    async def _query_for_get(self, menu_id: UUID, submenu_id: UUID) -> "select":
        return (
            select(self.model)
            .join(SubMenu, SubMenu.id == self.model.submenu_id)
            .filter(
                self.model.submenu_id == submenu_id,
                SubMenu.menu_id == menu_id,
            )
        )

    async def get_with_relates(
        self, dish_id: UUID, submenu_id: UUID, menu_id: UUID
    ) -> Dish:
        async with self.db as db:
            queryset = await self._query_for_get(menu_id, submenu_id)
            result = await db.session.execute(queryset.filter(self.model.id == dish_id))
        return result.scalars().first()

    async def get_all_with_relates(
        self, menu_id: UUID, submenu_id: UUID, skip: int, limit: int
    ) -> list[Dish]:
        async with self.db as db:
            queryset = await self._query_for_get(menu_id, submenu_id)
            result = await db.session.execute(queryset.offset(skip).limit(limit))
        return result.scalars().all()


def get_dish_orm(db: AbstractAsyncSession = Depends(get_db)) -> DishAction:
    return DishAction(db=db)


def get_menu_orm(db: AbstractAsyncSession = Depends(get_db)) -> MenuAction:
    return MenuAction(db=db)


def get_submenu_orm(db: AbstractAsyncSession = Depends(get_db)) -> SubMenuAction:
    return SubMenuAction(db=db)
