# zhurik

Чат-бот для взаимодействия с абитуриентами 

## Инструкции к пользованию

### Подготовка 

Перед тем, как продолжить, сначала убедитесь, что у вас корректно установлен интерпретатор *python* и менеджер пакетов *pip* (обычно устанавливается вместе с интерпретатором).
Проверить это можно при помощи команд `py -v` и `py -m pip -v`, введёных в консоли (т.ж.с. командной строке) - если они исполняются без ошибки и корректно отображают номер версии, то всё в порядке. (ПРИМЕЧАНИЕ: здесь и далее `py` — это команда для использования интерпретатора *python*. В некоторых случаях данным "словом" может также быть `python3` или просто `python`. Если у вас по какой-то причине не работает первое — пробуйте их. Если же и они не сработали, то проблема была в самой установке)
Далее клонируйте данный репозиторий и из его корневой папки установите все текущие зависимости проекта - `py -m pip install -r requirements.txt`. Замечание для будущих разработчиков: после добавления новых зависимостей файл *requirements.txt* следует обновлять.
Напоследок следует создать текстовый файл с буквальным названием *.env* (пустое имя, расширение "env"), в который следует поместить подобную строчку:
`TG_BOT_TOKEN="выданный_вам_длинный_токен_для_телеграмм_бота"`
Получить строчку токена можно при обращении к официальному боту под именем @BotFather в самом Телеграме и пройдя небольшую процедуру регистрации. 

### Установка базы данных

Для правильной работы статистики необходимо настроить базу данных (на sqlite). Сделать это можно следующей командой: `py db_init.py`.
Замечание для будущих разработчиков: именно в этом файле задаётся структура базы данных в формате SQL. Если вы захотите её поменять, то не забудьте обновить её или в консоли соответствующими командами (вручную), или же запуском `py db_drop.py` (сбросом всей базы данных) и последующим `py db_init.py` (пересозданием).
ВНИМАНИЕ: адрес используемой базы данных задаётся через строчку в файле *.env* следующим образом:
`DB_ADDRESS="путь/до/желаемой/базы/данных.db"`
По умолчанию данный параметр равен *zhurik.db*

### Запуск

Для запуска бота достаточно ввести `py main.py` при нахождении в корневой папке проекта. Если в консоли вы увидели приветственное сообщение об успешном запуске - то бот готов к службе! Найдите его в приложении Телеграм по тому имени, что указывали при регистрации, и напишите команду `/start`.

### Корректировка ветвей вопросов

Древо вопросов и ответов формируется путём обработки файла `questions_tree.json` - текстовом файле в формате `json`.
Для правильной модификации следует: 

- Избегать использования символа *|* в темах и вопросах, так как он используется в качестве разделителя в скрипте выгрузки статистики.
- Придерживаться общих правил этого формата.
- Организовать его наподобие следующей древовидной структуры:

```json
{
    "вопрос": "прямой ответ",
    "ещё вопрос": "иной ответ",
    "особенная тема вопросов": {
        "конкретный вопрос": "конкретный ответ",
        "конкретный вопрос 2": "конкретный ответ 2",
        "ещё более углубленная тема вопроса": {
            "самый особенный вопрос": "самый особенный ответ"
        }
    },
    "вопрос о помощи": "ответ с памяткой"
}
```

Где на месте "ключей" объекта - вопросы, а на месте "значений" - или такие же объекты (условно назовём их "темы"), или ответы на них.
Внимание! Перед окончанием заполнения убедитесь, что во всём древе два всяких вопроса отличаются друг от друга или темой-родителем, или текстом. Если они отличаются текстом и темой-родителем, но у самих тем-родителей также идентичны тексты - это тоже считается нарушением формата.
Пример того, как быть НЕ должно:

```json
{
    "вопрос": "ответ",
    "вопрос": "ответ",
    "плохая тема": {
        "дубль": "дубль-ответ",
        "дубль": "дубль-ответ"
    },
    "плохая тема": {
        "дубль": "дубль-ответ",
        "нормальный вопрос": "нормальный ответ"
    }
}
```

### Функция обращения к оператору

Для получения контактов оператора достаточно прописать команду `/help`, и бот отправит вам кнопку с ссылкой на пользователя Телеграм.

Манипулировать списком операторов можно при помощи файла `operators.json`: соблюдая разметку данного формата, просто впишите в общий "словарь" сначала имя оператора (как ключ), каким будущий пользователь увидит его на кнопке, а через двоеточие (как значение) – тэг пользователя Телеграм, привязанный к аккаунту вашего оператора. (ПРИМЕЧАНИЕ: обычно тэги пишутся через символ "@", но в самом файле тэг следует вводить без него. Если вы хотите понять, какой тэг у вас – просто откройте свой профиль в Телеграм, и вы найдёте его в поле "Имя пользователя")

### Получение выгрузки из Базы Данных

На данный момент поддерживается получение статистики по запрошенным вопросам. Для того, чтобы её получить, достаточно запустить скрипт *db_stat.py* – сделать это можно при помощи команды `py db_stat.py`, находясь в корневой папке проекта.
Запуск данного скрипта сохранит результаты обработки базы данных в файле с разрешением *.csv* (известный формат, применяемый для ведения таблиц) *.xlsx* (стандартный для офисной программы Excel) внутри папки *stats*. Также во время запуска в консоль будут построчно выводиться аналогичные данные (только с иным порядком колонок).

## Требования к боту (для разработчиков)

В результате выполнения проекта должен появиться бот-помощник в Telegram, способный отвечать на вопросы абитуриентов и формировать инструкции по поступлению на направления факультета журналистики.

- Текст соответствует нормам и правилам русского языка
- Во взаимодействии с ботом пользователь может выбирать категории вопроса
- Пользователь имеет возможность возвращаться к предыдущему вопросу
- Существует возможность переадресации пользователя на специалиста отборочной комиссии (отправка контактов в случае, если обращающийся слишком долго ищет ответ на свой вопрос)
- Присутствуют элементы вовлечения пользователя в коммуникацию в рамках мессенджера
- Возможность редактирования ответов бота сотрудниками отборочной комиссии после завершения взаимодействия с проектной командой и инструкции по использованию
- У держателя бота есть возможность отслеживать количество обращений, контактные данные пользователей (номера телефонов и ФИО), формируется статистика по самым популярным вопросам
