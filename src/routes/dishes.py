from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.models import schemas
from src.services import Service, get_dish_service

router = APIRouter(
    prefix="/menus/{menu_id}/submenus/{submenu_id}/dishes", tags=["Dishes"]
)


@router.post(
    "/",
    response_model=schemas.Dish,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": schemas.SubMenuError, "description": "Submenu or menu not exist"}
    },
)
async def create_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish: schemas.DishCreate,
    dish_service: Service = Depends(get_dish_service),
):
    """
    Create dish  for submenu with all the information:

    - **title**: each submenu must have a title
    - **description**: a long description
    - **price**: some float type score
    """
    return await dish_service.create(data=dish, menu_id=menu_id, submenu_id=submenu_id)


@router.get(
    "/",
    response_model=list[schemas.Dish],
    responses={
        404: {
            "model": schemas.DishError,
            "description": "Dish not found. Check menu and submenu existing",
        }
    },
)
async def get_dishes(
    menu_id: UUID,
    submenu_id: UUID,
    skip: int = 0,
    limit: int = 100,
    dish_service: Service = Depends(get_dish_service),
):
    """
    Get all dishes for submenu, depending on menu
    """
    return await dish_service.get_list(
        menu_id=menu_id, submenu_id=submenu_id, skip=skip, limit=limit
    )


@router.get("/{dish_id}", response_model=schemas.Dish)
async def get_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    dish_service: Service = Depends(get_dish_service),
):
    """
    Get dish by id, depending on submenu and menu
    """
    return await dish_service.get(
        menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
    )


@router.patch("/{dish_id}", response_model=schemas.UpdatedDish)
async def update_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    dish: schemas.DishUpdate,
    dish_service: Service = Depends(get_dish_service),
):
    """
    Update dish, depending on submenu and menu
    """
    return await dish_service.update(
        data=dish, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
    )


@router.delete("/{dish_id}", response_model=schemas.DishRemove)
async def delete_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    dish_service: Service = Depends(get_dish_service),
):
    """
    Remove dish, depending on submenu and menu
    """
    await dish_service.remove(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    return {"status": True, "message": "The dish has been deleted"}
