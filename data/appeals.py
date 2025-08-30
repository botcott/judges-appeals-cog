import os
import json
import logging

async def save_data(judge_id: int, appeal_id: int, filename = f"{os.path.dirname(__file__)}/appeals.json") -> None:
    data = {}
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

    judge_id = str(judge_id)

    if judge_id in data:
        if "appeals" in data[judge_id] and "appeals" in data[judge_id]["appeals"] and isinstance(data[judge_id]["appeals"]["appeals"], list):
            if appeal_id not in data[judge_id]["appeals"]["appeals"]:
                data[judge_id]["appeals"]["appeals"].append(appeal_id)
                data[judge_id]["appeals"]["message_time"].append(0)

        else:
            data[judge_id]["appeals"] = {"appeals": [appeal_id], "message_time": [0]}
    else:
        data[judge_id] = {"appeals": {"appeals": [appeal_id], "message_time": [0]}}

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

async def remove_data(judge_id: int, appeal_id: int, filename = f"{os.path.dirname(__file__)}/appeals.json") -> None:
    if not os.path.exists(filename):
        logging.info(f"Файл {filename} не существует.")
        return

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствует.")
        return

    judge_id = str(judge_id)

    if judge_id not in data:
        logging.warning(f"Предупреждение: judge_id {judge_id} не найден в файле {filename}.")
        return

    if "appeals" in data[judge_id] and "appeals" in data[judge_id]["appeals"] and "appeals" in data[judge_id]["appeals"] and isinstance(data[judge_id]["appeals"]["appeals"], list):
        # Если judge_id существует и структура appeals уже создана

        try:
            appeal_index = data[judge_id]["appeals"]["appeals"].index(appeal_id) # Находим индекс appeal_id

            del data[judge_id]["appeals"]["appeals"][appeal_index] # Удаляем appeal_id
            del data[judge_id]["appeals"]["message_time"][appeal_index] # Удаляем соответствующее значение из message_time

            logging.info(f"Удален appeal_id {appeal_id}")

            if not data[judge_id]["appeals"]["appeals"]:
                del data[judge_id]
                logging.info(f"judge_id {judge_id} удален, так как список appeal_id стал пустым.")


        except ValueError:
            logging.warning(f"Предупреждение: appeal_id {appeal_id} не найден")
    else:
        logging.warning(f"Предупреждение: Неправильная структура данных")


    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Ошибка: Не удалось записать данные в файл {filename}: {e}")

async def check_appeal(appeal_id: int, filename = f"{os.path.dirname(__file__)}/appeals.json") -> bool:
    if not os.path.exists(filename):
        logging.info(f"Файл {filename} не существует.")
        return False

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствует. Считаем, что appeal_id не найден.")
        return False

    for judge_id, judge_data in data.items(): # Перебираем все judge_id
        if isinstance(judge_data, dict) and "appeals" in judge_data and "appeals" in judge_data["appeals"] and "appeals" in judge_data["appeals"] and isinstance(judge_data["appeals"]["appeals"], list):  # Проверяем структуру
            if appeal_id in judge_data["appeals"]["appeals"]:  # Ищем в списке appeals
                logging.info(f"appeal_id {appeal_id} найден у judge_id {judge_id}.")
                return True  # appeal_id найден
        else:
            logging.warning(f"Неправильная структура данных")

    logging.info(f"appeal_id {appeal_id} не найден ни у одного judge_id.")
    return False  # appeal_id не найден

async def get_judge(appeal_id: int, filename = f"{os.path.dirname(__file__)}/appeals.json"):
    if (not os.path.exists(filename)):
        return True

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствовать.")
        return True

    for judge_id, appeal_ids in data.items():
        if (isinstance(appeal_ids, list)):
            if (appeal_id in appeal_ids):
                return judge_id # Возвращаем judge_id если нашли
        elif (str(appeal_ids) == appeal_id):
            return judge_id # Возвращаем judge_id если нашли

    return True  # Если не нашли

async def get_all_appeals(filename = f"{os.path.dirname(__file__)}/appeals.json"):
    appeal_ids = []

    if (not os.path.exists(filename)):
        logging.info(f"Файл {filename} не существует.")
        return appeal_ids

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствует.")
        return appeal_ids

    for judge_id, appeal_ids_value in data.items():
        if (isinstance(appeal_ids_value, list)):
            appeal_ids.extend(appeal_ids_value)
        else:
            appeal_ids.append(appeal_ids_value)

    return appeal_ids

async def save_msg_time(judge_id: int, appeal_id: int, new_time: str, filename = f"{os.path.dirname(__file__)}/appeals.json") -> bool:
    if not os.path.exists(filename):
        logging.error(f"Файл {filename} не существует.")
        return False

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствует.")
        return False

    if judge_id not in data:
        logging.warning(f"Предупреждение: judge_id {judge_id} не найден в файле {filename}.")
        return False

    if not isinstance(data[judge_id], dict) or "appeals" not in data[judge_id] or not isinstance(data[judge_id]["appeals"], dict) or "appeals" not in data[judge_id]["appeals"] or "message_time" not in data[judge_id]["appeals"] or not isinstance(data[judge_id]["appeals"]["appeals"], list) or not isinstance(data[judge_id]["appeals"]["message_time"], list) or len(data[judge_id]["appeals"]["appeals"]) != len(data[judge_id]["appeals"]["message_time"]):
        logging.error(f"Неправильная структура данных")
        return False

    try:
        appeal_index = data[judge_id]["appeals"]["appeals"].index(appeal_id)
        new_timestamp = new_time.timestamp()
        data[judge_id]["appeals"]["message_time"][appeal_index] = new_timestamp  # Обновляем время
        logging.info(f"Время сообщения для appeal_id {appeal_id} у judge_id {judge_id} обновлено на {new_time}.")

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return True  # Успешно обновлено

    except ValueError:
        logging.warning(f"appeal_id {appeal_id} не найден")
        return False  # appeal_id не найден

    except IOError as e:
        logging.error(f"Ошибка: Не удалось записать данные в файл {filename}: {e}")
        return False

async def get_msg_time(judge_id: int, appeal_id: int, filename = f"{os.path.dirname(__file__)}/appeals.json") -> str:
    if not os.path.exists(filename):
        logging.error(f"Файл {filename} не существует.")
        return None

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Ошибка: Не удалось загрузить JSON из файла {filename}. Файл может быть поврежден или отсутствует.")
        return None

    if judge_id not in data:
        logging.warning(f"Предупреждение: judge_id {judge_id} не найден в файле {filename}.")
        return None

    if not isinstance(data[judge_id], dict) or "appeals" not in data[judge_id] or not isinstance(data[judge_id]["appeals"], dict) or "appeals" not in data[judge_id]["appeals"] or "message_time" not in data[judge_id]["appeals"] or not isinstance(data[judge_id]["appeals"]["appeals"], list) or not isinstance(data[judge_id]["appeals"]["message_time"], list) or len(data[judge_id]["appeals"]["appeals"]) != len(data[judge_id]["appeals"]["message_time"]):
        logging.error(f"Неправильная структура данных")
        return None

    try:
        appeal_index = data[judge_id]["appeals"]["appeals"].index(appeal_id)
        time = data[judge_id]["appeals"]["message_time"][appeal_index]
        return time

    except ValueError:
        logging.warning(f"appeal_id {appeal_id} не найден")
        return None