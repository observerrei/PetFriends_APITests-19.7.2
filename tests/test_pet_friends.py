
from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):  #Проверяем валидность получения АПИ-ключа при существующем пользователе
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert "key" in result

def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password): #Проверка ввода неправильного имейла с правильным паролем
    status, result = pf.get_api_key(email, password)
    assert 400 <= status <= 499
    assert "key" not in result


def test_get_api_key_for_invalid_pass(email=valid_email, password=invalid_password): #Проверка ввода правильно имейла с неправильным паролем
    status, result = pf.get_api_key(email, password)
    assert 400 <= status <= 499
    assert "key" not in result

def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):  #Проверка полностью несуществующего пользователя
    status, result = pf.get_api_key(email, password)
    assert 400 <= status <= 499
    assert "key" not in result

def test_get_all_pets_with_valid_key(filter=""):  #Проверяем, что у существующего пользователя не пустой список питомцев путем запроса списка петов и АПИ-кей
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result["pets"]) > 0

def test_add_new_pet_with_valid_data(name='Котичка', animal_type='Кот дворянский обыкновенный', age='2', pet_photo='images\mozhno-nenado-mem-9.jpg'):
    #Проверяем создание питомца с верными данными

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name #Сверяем итоговый результат с именем питомца


def test_successful_delete_self_pet(): #проверяем удаление питомца

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.post_add_new_pet(auth_key, "Можно не надо", "Кот дворянский обыкновенный", "2", "images\mozhno-nenado-mem-9.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Котичка', animal_type='Кот дворянский обыкновенный', age=5):  #Проверка обновления информации о питомце

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("Ой-ей, разбежались все")


def test_get_all_pets_with_invalid_filter(filter='not_my_pets'): #Проверка неправильно заданного параметра filter
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert 400 <= status <= 499


def test_post_add_new_pet_with_invalid_name(name='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', animal_type='parrot', age='1', pet_photo='images\mozhno-nenado-mem-9.jpg'):
    #Проверка создания питомца с неправильно заданным именем
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert 400 <= status <= 499


def test_post_add_new_pet_with_none_name(name='', animal_type='Кот дворянский обыкновенный', age='1', pet_photo='images\mozhno-nenado-mem-9.jpg'):
    #Проверка создания питомца без имени
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert 400 <= status <= 499

def test_add_pet_with_uncorrect_animal_type(name='Неведома зверушка', animal_type='1212121', age='2', pet_photo='images\mozhno-nenado-mem-9.jpg'):
    #Проверка создания питомца с некорректным типом животного (состоящим только из чисел)
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, api_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.post_add_new_pet(api_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert animal_type not in result['animal_type'] #питомца не должно быть в результатах