from uuid import UUID

from fastapi import HTTPException

from src.cache import cache
from src.cache import key_gen
from src.cache import serialize
from src.cache.cache_service import RedisCache
from src.database.actions import DishAction
from src.models import Dish
from src.models import schemas


class DishService:
    all_cache_key: str = 'all_dishes'
    cache: RedisCache = cache
    service_orm: DishAction = DishAction()

    async def create(self, menu_id: UUID, submenu_id: UUID, data: schemas.DishCreate) -> dict:
        dish = await self.service_orm.create(obj_in=data, submenu_id=submenu_id)
        result: dict = serialize(dish)
        await self.cache.set_cache(data=result, key=key_gen(menu_id, submenu_id, getattr(dish, 'id')))
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id, self.all_cache_key))
        await self.cache.delete_cache(key=key_gen(menu_id, 'all_submenus'))
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id))
        return result

    async def get_list(self, menu_id: UUID, submenu_id: UUID, skip: int = 0, limit: int = 10) -> list | dict | None:
        cache_key: str = key_gen(menu_id, submenu_id, self.all_cache_key)
        result: list | dict | None = await self.cache.get_cache(key=cache_key)
        if not result:
            dishes: list[Dish] = await self.service_orm.get_all_with_relates(
                menu_id=menu_id, submenu_id=submenu_id,
                skip=skip, limit=limit,
            )
            result = list(serialize(dish) for dish in dishes)
            await self.cache.set_cache(data=result, key=cache_key)
        return result

    async def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        cache_key: str = key_gen(menu_id, submenu_id, dish_id)
        result: dict = await self.cache.get_cache(key=cache_key)
        if not result:
            dish: Dish = await self.service_orm.get_with_relates(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
            if not dish:
                raise HTTPException(detail='dish not found', status_code=404)
            result = serialize(dish)
            await self.cache.set_cache(data=result, key=cache_key)
        return result

    async def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, data: schemas.DishUpdate) -> dict:
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id, dish_id))
        await self.service_orm.update(id_obj=dish_id, obj_data=data)
        return await self.get(submenu_id=submenu_id, menu_id=menu_id, dish_id=dish_id)

    async def remove(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> bool:
        await self.service_orm.remove(id_obj=dish_id)
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id, dish_id))
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id, self.all_cache_key))
        await self.cache.delete_cache(key=key_gen(menu_id, 'all_menus'))
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id, 'all_submenus'))
        await self.cache.delete_cache(key=key_gen(menu_id, submenu_id))
        return True


dish_service = DishService()
