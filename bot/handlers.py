from aiogram import Router, types, F
from aiohttp import ClientSession
from config import BASE_URL
from fsm import *
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

router = Router()





@router.message(F.text == "/start")
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id

    async with ClientSession() as session:
        await session.post(f'{BASE_URL}/api/authenticate/', json={
            "telegram_id": telegram_id,
        
        })
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить категорию")],
            [KeyboardButton(text="📃 Мои категории")],
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="📋 Мои задачи")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
        
    await message.answer(f'Начните работу с добавления категории', reply_markup=keyboard)
    


@router.message(F.text == "➕ Добавить категорию")
async def add_category(message: types.Message, state: FSMContext):
    await state.set_state(CategoryStates.title)
    await message.answer("Введите название категории:")

@router.message(CategoryStates.title)
async def set_category_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    data = await state.get_data()

    # Отправка в бэкенд
    async with ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/categories/create/", json={
            "telegram_id": message.from_user.id,
            "title": data["title"]
        }) as resp:
            if resp.status != 201:
                error_message = await resp.text()
                await message.answer(f"❌ Ошибка при добавлении категории: {error_message}")
                return

    await message.answer("✅ Категория успешно добавлена!")
    await state.clear()


@router.message(F.text == "📃 Мои категории")
async def category_list_handler(message: types.Message):
    telegram_id = message.from_user.id
    async with ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/categories/", json={"telegram_id": telegram_id}) as resp:
            categories = await resp.json()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for category in categories:
        button = InlineKeyboardButton(
            text=category["title"],
            callback_data=f"categories:{category['id']}"
        )
        keyboard.inline_keyboard.append([button])
    if not categories:
        await message.answer("У вас нет категорий.")
        return
    await message.answer("Вот ваши категории:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("categories:"))
async def category_callback(callback: types.CallbackQuery):
    category_id = callback.data.split(":")[1]

    # Получаем подробности по API
    async with ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/categories/{category_id}/") as resp:
            category = await resp.json()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Удалить категорию", callback_data=f"delete_category:{category_id}")],
    ])
    await callback.message.answer(
        f"📌 Категория: {category['title']}\n", reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete_category:"))
async def delete_category_callback(callback: types.CallbackQuery):
    category_id = callback.data.split(":")[1]

    # Отправляем запрос на удаление категории
    async with ClientSession() as session:
        async with session.delete(f"{BASE_URL}/api/categories/{category_id}/delete/") as resp:
            if resp.status == 204:
                await callback.message.answer("✅ Категория успешно удалена!")
            else:
                await callback.message.answer("❌ Ошибка при удалении категории.")

    await callback.answer()


@router.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: types.Message, state: FSMContext):
    await state.set_state(TaskStates.title)
    await message.answer("Введите название задачи:")


@router.message(TaskStates.title)
async def set_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(TaskStates.due)
    await message.answer("Введите дату дедлайна (в формате YYYY-MM-DD HH:MM):")


@router.message(TaskStates.due)
async def set_due(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    result = ''
    await state.update_data(due=message.text)
    await state.set_state(TaskStates.category)
    async with ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/categories/", json={"telegram_id": telegram_id}) as resp:
            categories = await resp.json()
            for category in categories:
                result += f'{category["id"]}. {category["title"]}\n'

    await message.answer("Введите id категории:")
    await message.answer(result)



@router.message(TaskStates.category)
async def set_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()

    # Отправка в бэкенд
    async with ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/tasks/create/", json={
            "telegram_id": message.from_user.id,
            "title": data["title"],
            "due_date": data["due"],
            "category_id": data["category"]
        }) as resp:
            if resp.status != 201:
                error_message = await resp.text()
                await message.answer(f"❌ Ошибка при добавлении задачи")
                return

    await message.answer("✅ Задача успешно добавлена!")
    await state.clear()


@router.message(F.text == '📋 Мои задачи')
async def task_list_handler(message: types.Message):
    telegram_id = message.from_user.id
    async with ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/tasks/", json={"telegram_id": telegram_id}) as resp:
            tasks = await resp.json()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for task in tasks:
        button = InlineKeyboardButton(
            text=f'{task["title"]}| {"✓" if task["is_completed"] else "✗"}. {task["created_at"]} → {task["due_date"]}',
            callback_data=f"tasks:{task['id']}"
        )
        keyboard.inline_keyboard.append([button])
    if not tasks:
        await message.answer("У вас нет задач.")
        return
    await message.answer("Вот ваши задачи:", reply_markup=keyboard)



@router.callback_query(F.data.startswith("tasks:"))
async def task_callback(callback: types.CallbackQuery):
    task_id = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    

    # Получаем подробности по API
    async with ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/tasks/{task_id}/", json={'telegram_id': telegram_id, 'task_id': task_id}) as resp:
            task = await resp.json()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить задачу", callback_data=f"complete_task:{task_id}")] if not task['is_completed'] else [],
        [InlineKeyboardButton(text="❌ Удалить задачу", callback_data=f"delete_task:{task_id}")],]
        )
    await callback.message.answer(
        f"📌 Задача: {task['title']}\n"
        f"Категория: {task['category'] if task['category'] else 'Без категории'}\n"
        f"Статус: {'✅' if task['is_completed'] else '❌'}\n"
        f"Создана: {task['created_at']}\n"
        f"Дедлайн: {task['due_date']}\n", reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("complete_task:"))
async def complete_task_callback(callback: types.CallbackQuery):
    task_id = callback.data.split(":")[1]

    # Отправляем запрос на завершение задачи
    async with ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/tasks/{task_id}/complete/") as resp:
            if resp.status in (200, 202, 204):
                await callback.message.answer("✅ Задача успешно завершена!")
            else:
                await callback.message.answer("❌ Ошибка при завершении задачи.")

    await callback.answer()

@router.callback_query(F.data.startswith("delete_task:"))
async def delete_task_callback(callback: types.CallbackQuery):
    task_id = callback.data.split(":")[1]

    # Отправляем запрос на удаление задачи
    async with ClientSession() as session:
        async with session.delete(f"{BASE_URL}/api/tasks/{task_id}/delete/") as resp:
            if resp.status == 204:
                await callback.message.answer("✅ Задача успешно удалена!")
            else:
                await callback.message.answer("❌ Ошибка при удалении задачи.")

    await callback.answer()