from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional, List
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("hotel.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

#11 ИСКЛЮЧЕНИЯ
class InvalidRoomError(Exception):
    """Исключение для некорректных параметров номера."""
    def __init__(self, message="Некорректные данные номера"):
        super().__init__(message)

class PermissionDeniedError(Exception):
    """Исключение при отсутствии прав доступа."""
    def __init__(self, message="Недостаточно прав доступа"):
        super().__init__(message)

class BookingNotFoundError(Exception):
    """Исключение, если бронирование не найдено."""
    def __init__(self, message="Бронирование не найдено"):
        super().__init__(message)

#6 МЕТАКЛАССЫ
class RoomMeta(type):
    """Метакласс для регистрации типов номеров."""
    registry = {}

    def __new__(cls, name, bases, class_dict):
        new_class = super().__new__(cls, name, bases, class_dict)
        if name != "Room":
            RoomMeta.registry[name.lower().replace("room", "")] = new_class
        return new_class
    
#5 МИКСИНЫ
class LoggingMixin():
    """Миксин для логирования действий."""
    def log_action(self, message):
        """Метод для логирования сообщения."""
        logging.info(message)

class NotificationMixin():
    """Миксин для отправки уведомлений."""
    def send_notification(self, message):
        """Метод для отправки уведомления."""
        print(f"[NOTIFICATION] {message}")

#1 БАЗОВЫЙ АБСТРАКТНЫЙ КЛАСС
class Room(LoggingMixin, metaclass = RoomMeta):
    """Абстрактный базовый класс для гостиничного номера."""
    def __init__(self, room_id: int, room_type: str, capacity: int, price_per_night: float, is_available: bool):
        """Инициализация номера с проверкой параметров."""
        if capacity <= 0 or price_per_night < 0:
            raise InvalidRoomError("Вместимость и цена должны быть положительными")
        self.__room_id = room_id
        self.__room_type = room_type
        self.__capacity = capacity
        self.__price_per_night = price_per_night
        self.__is_available = is_available
        self.log_action(f"Создана комната #{self.__room_id}. Тип: {self.__room_type}. Вместимость: {self.__capacity}. Цена за ночь: {self.__price_per_night}")

    def __str__(self):
        """Строковое представление номера."""
        return f"Номер: {self.__room_id}, Тип: {self.__room_type}" 
    
    def __lt__(self, other: 'Room'):
        """Сравнение номеров по цене (меньше)."""
        return self.__price_per_night < other.get_price_per_night()
    def __gt__(self, other: 'Room'):
        """Сравнение номеров по цене (больше)."""
        return self.__price_per_night > other.get_price_per_night()
    
    @abstractmethod
    def calculate_cost(self, nights: int):
        """Абстрактный метод для подсчета стоимости."""
        self.log_action("Посчитана стоимость проживания")
        pass

    def set_room_id(self, room_id : int):
        """Сеттер для room_id"""
        self.__room_id = room_id
    def set_room_type(self, room_type: str):
        """Сеттер для room_type"""
        self.__room_type = room_type
    def set_capacity(self, capacity: int):
        """Сеттер для capacity"""
        self.__capacity = capacity
    def set_price_per_night(self, price: float):
        """Сеттер для price_per_night"""
        self.__price_per_night = price
    def set_is_available(self, available: bool):
        """Сеттер для is_available"""
        self.__is_available = available

    def get_room_id(self) -> int:
        """Геттер для room_id"""
        return self.__room_id
    def get_room_type(self) -> str:
        """Геттер для room_type"""
        return self.__room_type
    def get_capacity(self) -> int:
        """Геттер для capacity"""
        return self.__capacity
    def get_price_per_night(self) -> float:
        """Геттер для price_per_night"""
        return self.__price_per_night
    def get_is_available(self) -> bool:
        """Геттер для is_available"""
        return self.__is_available
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь."""
        return {
            "room_id": self.get_room_id(),
            "room_type": self.__class__.__name__.lower().replace("room", ""),
            "capacity": self.get_capacity(),
            "price_per_night": self.get_price_per_night(),
            "is_available": self.get_is_available()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создать объект номера из словаря."""
        return cls(
            room_id=data["room_id"],
            room_type=data["room_type"],
            capacity=data["capacity"],
            price_per_night=data["price_per_night"],
            is_available=data["is_available"]
        )
    
#2 НАСЛЕДНИКИ
class StandardRoom(Room):
    """Номер типа 'Стандарт' с возможностью добавления телевизора."""
    def __init__(self, room_id, capacity, price_per_night, is_available, has_tv):
        super().__init__(room_id, "Стандарт", capacity, price_per_night, is_available)
        self.__has_tv = has_tv
    
    def calculate_cost(self, nights: int) -> float: 
        """Расчет стоимости с учетом наличия телевизора."""
        return self.get_price_per_night() * nights + (1000 if self.__has_tv else 0)
    
    def __str__(self):
        """Строковое представление стандартного номера."""
        return f"Стандарт: {self.get_room_id()}, TV: {'есть' if self.__has_tv else 'нет'}"
    
    def set_has_tv(self, has_tv: bool):
        """Сеттер для наличия телевизора."""
        self.__has_tv = has_tv
    def get_has_tv(self) -> bool:
        """Геттер для наличия телевизора."""
        return self.__has_tv
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base["has_tv"] = self.get_has_tv()
        return base

    
class DeluxeRoom(Room):
    """Номер типа 'Люкс' с возможностью добавления джакузи."""
    def __init__(self, room_id, capacity, price_per_night, is_available, has_jacuzzi):
        super().__init__(room_id, "Люкс", capacity, price_per_night, is_available)
        self.__has_jacuzzi = has_jacuzzi
    
    def calculate_cost(self, nights: int) -> float: 
        """Расчет стоимости с учетом наличия джакузи."""
        return self.get_price_per_night() * nights + (2500 if self.__has_jacuzzi else 0)
    
    def __str__(self):
        """Строковое представление номера люкса."""
        return f"Люкс: {self.get_room_id()}, Джакузи: {'есть' if self.__has_jacuzzi else 'нет'}"
    
    def set_has_jacuzzi(self, has_jacuzzi: bool):
        """Сеттер для наличия джакуззи."""
        self.__has_jacuzzi = has_jacuzzi
    def get_has_jacuzzi(self) -> bool:
        """Геттер для наличия джакуззи."""
        return self.__has_jacuzzi
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base["has_jacuzzi"] = self.get_has_jacuzzi()
        return base


class Suite(Room):
    """Апартаменты с несколькими комнатами."""
    def __init__(self, room_id, capacity, price_per_night, is_available, number_of_rooms):
        if number_of_rooms <= 0:
            raise InvalidRoomError("Количество комнат должно быть положительным")
        super().__init__(room_id, "Апартаменты", capacity, price_per_night, is_available)
        self.__number_of_rooms = number_of_rooms
    
    def calculate_cost(self, nights: int) -> float:
        """Расчет стоимости с учетом количества комнат."""
        return self.get_price_per_night() * nights + (self.__number_of_rooms * 4000)
    
    def __str__(self):
        """Строковое представление апартаментов."""
        return f"Аппартаменты: {self.get_room_id()}, Кол-во комнат: {self.__number_of_rooms}"
    
    def set_number_of_rooms(self, number_of_rooms: int):
        """Сеттер для количества комнат."""
        self.__number_of_rooms = number_of_rooms
    def get_number_of_rooms(self) -> int:
        """Геттер для количества комнат."""
        return self.__number_of_rooms
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base["number_of_rooms"] = self.get_number_of_rooms()
        return base


#4 ИНТЕРФЕЙСЫ ДЛЯ РАБОТЫ С ГОСТИНИЦЕЙ
class Bookable(ABC):
    """Интерфейс для бронирования номера."""
    @abstractmethod
    def book_room(self):
        """Метод для бронирования номера."""
        pass

class Reportable(ABC):
    """Интерфейс для генерации отчетов."""
    @abstractmethod
    def generate_report(self):
        """Метод для генерации отчета."""
        pass 
        
#8 ЦЕПОЧКА ОБЯЗЯННОСТЕЙ
class Booking_change_request:
    """Запрос на изменение бронирования."""
    def __init__(self, change_type: str, details: str):
        self.change_type = change_type
        self.details = details

class Handler:
    """Базовый класс обработчика для цепочки обязанностей."""
    def __init__(self, next_handler = None):
        self.next_hadler = next_handler
    
    def handle(self, request: Booking_change_request):
        """Обработка запроса или передача на следующий обработчик."""
        if self.next_hadler:
            return self.next_hadler.handle(request)
        print("Запрос не может быть обработан")

class Administrator(Handler):
    """Обработчик для администраторов."""
    def handle(self, request: Booking_change_request):
        """Обработка запроса на изменение даты бронирования."""
        if request.change_type == 'date':
            print(f"Администратор одобрил изменение: {request.details}")
        else:
            super().handle(request)

class Manager(Handler):
    """Обработчик для менеджеров."""
    def handle(self, request: Booking_change_request):
        """Обработка запроса на изменение цены бронирования."""
        if request.change_type == "price":
            print(f"Менеджер пересчитал стоимость: {request.details}")
        else:
            super().handle(request)

class Director(Handler):
    """Обработчик для директоров."""
    def handle(self, request: Booking_change_request):
        """Обработка запроса на одобрение директором."""
        print(f"Директор рассмотрел и одобрил: {request.details}")

#3 КОМПОЗИЦИЯ И АГРЕГАЦИЯ
class Customer(LoggingMixin):
    """Класс для работы с клиентами гостиницы."""
    def __init__(self, customer_id: int, name: str, age: int):
        self.__customer_id = customer_id
        self.__name = name
        self.__age = age
        self.log_action(f"Создана запись о клиенте #{self.__customer_id}. Имя: {self.__name}. Возраст: {self.__age}")
        
    
    def get_customer_id(self) -> int:
        """геттер для customer_id"""
        return self.__customer_id
    def get_name(self) -> str:
        """геттер для name"""
        return self.__name
    def get_age(self) -> int:
        """геттер для age"""
        return self.__age
    
    def to_dict(self) -> dict:
        """Получить данные клиента в виде словаря."""
        return {
            "customer_id": self.get_customer_id(),
            "name": self.get_name(),
            "age": self.get_age()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создать объект клиента из данных."""
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            age=data["age"]
        )
    
class BookingIDGenerator:
    """Генератор уникальных идентификаторов для бронирований."""
    current_id = 0
    @classmethod
    def next_id(cls):
        """Получить следующий идентификатор для бронирования."""
        cls.current_id += 1
        return cls.current_id

class Booking(LoggingMixin, NotificationMixin, Reportable):
    """Класс для бронирования номера в гостинице."""
    def __init__(self, booking_id: int, customer_info: Customer, room: Room, check_in_date: str, check_out_date: str, services = None):
        self.__booking_id = booking_id
        self.__customer_info = customer_info
        self.__room = room
        self.__check_in_date = datetime.strptime(check_in_date, "%d-%m-%Y")
        self.__check_out_date = datetime.strptime(check_out_date, "%d-%m-%Y")
        self.__services: Dict[str, float] = {}
        self.__total_cost: float = 0.0
        self.log_action(f"Создано новое бронирование #{self.__booking_id}")
    
    def __str__(self):
        """Строковое представление бронирования."""
        return f"Бронирование #{self.__booking_id} для клиента {self.__customer_info.get_name()}"
    
    def add_service(self, service_name: str, price: float):
        """Добавить услугу в бронирование."""
        self.__services[service_name] = price
        self.log_action(f"Добавлена услуга {service_name} за {price}₽")
        self.send_notification(f"K вашему бронированию добавлена услуга '{service_name}'")
    
    def remove_service(self, service_name: str):
        """Удалить услугу из бронирования."""
        if service_name in self.__services:
            del self.__services[service_name]
            self.log_action(f"Услуга '{service_name}' удалена")
            self.send_notification(f"Услуга '{service_name}' была удалена из вашего бронирования")
    
    def calculate_total(self) -> float:
        """Рассчитать итоговую стоимость бронирования."""
        nights = (self.__check_out_date - self.__check_in_date).days
        room_cost = self.__room.calculate_cost(nights)
        services_cost = sum(self.__services.values())
        self.__total_cost = room_cost + services_cost
        self.log_action(f"Рассчитана итоговая стоимость бронирования: {self.__total_cost}₽")
        return self.__total_cost
    
    def request_change(self, change_type: str, details: str):
        """Запросить изменение бронирования через цепочку обработчиков."""
        request = Booking_change_request(change_type, details)
        chain = Administrator(Manager(Director()))
        chain.handle(request)
        self.log_action("Создана цепочка запросов")
    
    @staticmethod
    def next_id():
        """Получить следующий уникальный идентификатор для бронирования."""
        return BookingIDGenerator.next_id()
    
    def get_total_cost(self) -> float:
        """Геттер для total_cost"""
        return self.__total_cost
    def get_services(self) -> Dict[str, float]:
        """Геттер для services"""
        return self.__services
    def get_customer(self) -> Customer:
        """Геттер для customer_info"""
        return self.__customer_info
    def get_booking_id(self) -> int:
        """Геттер для booking_id"""
        return self.__booking_id
    def get_room(self) -> Room:
        """Геттер для room"""
        return self.__room
    def get_check_in_date(self) -> str:
        """Геттер для даты заезда"""
        return self.__check_in_date.strftime("%d-%m-%Y")
    def get_check_out_date(self) -> str:
        """Геттер для даты выезда"""
        return self.__check_out_date.strftime("%d-%m-%Y")
    
    def to_dict(self) -> dict:
        """Получить данные бронирования в виде словаря."""
        return {
            "booking_id": self.get_booking_id(),
            "customer_info": self.get_customer().to_dict(),
            "room": self.get_room().to_dict(),
            "check_in_date": self.get_check_in_date(),
            "check_out_date": self.get_check_out_date(),
            "services": self.get_services()
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создать объект бронирования из данных."""
        customer_info = Customer.from_dict(data["customer_info"])
        
        room_data = data["room"].copy()
        room_type = room_data.pop("room_type").lower()  # ← удаляем room_type, чтобы не дублировался

        room = RoomFactory.create_room(room_type, **room_data)

        return cls(
            booking_id=data["booking_id"],
            customer_info=customer_info,
            room=room,
            check_in_date=data["check_in_date"],
            check_out_date=data["check_out_date"],
            services=data["services"]
        )
    
    def generate_report(self) -> str:
        """Генерирование отчета по бронированию"""
        report_lines = [
            f"Отчет по бронированию #{self.get_booking_id()}",
            f"Клиент: {self.get_customer().get_name()} (ID: {self.get_customer().get_customer_id()}, Возраст: {self.get_customer().get_age()})",
            f"Номер: {self.get_room().__class__.__name__} (ID: {self.get_room().get_room_id()}, Вместимость: {self.get_room().get_capacity()})",
            f"Даты проживания: с {self.get_check_in_date()} по {self.get_check_out_date()}",
        ]

        if self.__services:
            report_lines.append("Дополнительные услуги:")
            for service, price in self.__services.items():
                report_lines.append(f"   - {service}: {price}₽")
        else:
            report_lines.append("Дополнительные услуги: отсутствуют")
        self.calculate_total()
        report_lines.append(f"Общая стоимость: {self.__total_cost:.2f}₽")

        self.log_action(f"Сгенерирован отчет по бронированию #{self.__booking_id}")
        return "\n".join(report_lines)

#7 ФАБРИЧНЫЕ МЕТОДЫ
class RoomFactory:
    """Класс фабрики для создания номеров."""
    @staticmethod
    def create_room(room_type: str, *args, **kwargs):
        """Создание номера на основе типа комнаты."""
        room_type = room_type.lower()
        if room_type not in RoomMeta.registry:
            raise InvalidRoomError(f"Неизвестный тип номера: {room_type}")
        return RoomMeta.registry[room_type](*args, **kwargs)
    
#10 ДЕКОРАТОР ДЛЯ ПРОВЕРКИ ПРАВ ДОСТУПА     
def check_permissions(*allowed_roles):
    """Декоратор для проверки прав доступа к методам."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            user = getattr(self, "user", None)
            if not user or user.get("role") not in allowed_roles:
                raise PermissionDeniedError(f"Доступ запрещен для роли: {user.get('role', 'Неизвестно')}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
    
#9 ШАБЛОННЫЙ МЕТОД
class BookingProcess(Bookable, ABC):
    """Абстрактный класс для процесса бронирования номера."""
    def __init__(self, customer, room, check_in, check_out, user: dict):
        self.customer = customer
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.user = user
        self.booking: Optional[Booking] = None

    def book_room(self):
        """Основной метод для бронирования."""
        self.check_availability()
        self.reserve_room()
        self.confirm_booking()

    @abstractmethod
    def check_availability(self):
        """Проверка доступности номера — абстрактный метод."""
        pass

    @abstractmethod
    def reserve_room(self):
        """Резервирование номера — абстрактный метод."""
        pass

    @abstractmethod
    def confirm_booking(self):
        """Подтверждение бронирования — абстрактный метод."""
        pass

    @check_permissions("receptionist", "manager")
    def add_service(self, service_name: str, price: str):
        """Добавление услуги в бронирование с проверкой прав доступа."""
        if self.booking:
            self.booking.add_service(service_name, price)
        else:
            raise BookingNotFoundError("Невозможно добавить услугу — бронирование не найдено")
    
    @check_permissions("receptionist", "manager")
    def remove_service(self, service_name: str):
        """Удаление услуги из бронирования с проверкой прав доступа."""
        if self.booking:
            self.booking.remove_service(service_name)
        else:
            raise BookingNotFoundError("Невозможно удалить услугу - бронирование не найдено")

    @check_permissions("guest", "receptionist", "manager")
    def calculate_total(self):
        """Расчет общей стоимости бронирования с проверкой прав доступа."""
        if self.booking:
            return self.booking.calculate_total()
        else:
            raise BookingNotFoundError("Невозможно рассчитать стоимость — бронирование не найдено")


class OnlineBookingProcess(BookingProcess, LoggingMixin, NotificationMixin):
    """Процесс бронирования через онлайн-систему."""
    def check_availability(self):
        """Проверка доступности номера в онлайн-системе."""
        if not self.room.get_is_available():
            raise Exception("Номер недоступен для бронирования")
        self.log_action("Онлайн: проверка доступности номера через веб-интерфейс")

    def reserve_room(self):
        """Резервирование номера через онлайн-систему."""
        self.booking = Booking(
            booking_id=Booking.next_id(),
            customer_info=self.customer,
            room=self.room,
            check_in_date=self.check_in,
            check_out_date=self.check_out
        )
        self.log_action(f"Онлайн: создано бронирование #{self.booking.get_booking_id()} через сайт")

    def confirm_booking(self):
        """Подтверждение бронирования в онлайн-системе."""
        self.room.set_is_available(False)
        self.send_notification(f"Бронирование подтверждено: {self.booking}")
        self.log_action(f"Онлайн: бронирование #{self.booking.get_booking_id()} подтверждено")


class OfflineBookingProcess(BookingProcess, LoggingMixin, NotificationMixin):
    """Процесс оффлайн-бронирования через стойку регистрации."""
    def check_availability(self):
        """Проверка доступности номера на стойке регистрации."""
        if not self.room.get_is_available():
            raise Exception("Номер недоступен для бронирования")
        self.log_action("Оффлайн: проверка доступности номера при личном обращении")

    def reserve_room(self):
        """Резервирование номера через стойку регистрации."""
        self.booking = Booking(
            booking_id=Booking.next_id(),
            customer_info=self.customer,
            room=self.room,
            check_in_date=self.check_in,
            check_out_date=self.check_out
        )
        self.log_action(f"Оффлайн: ручное бронирование #{self.booking.get_booking_id()} на стойке регистрации")

    def confirm_booking(self):
        """Подтверждение бронирования на стойке регистрации."""
        self.room.set_is_available(False)
        self.send_notification(f"Бронирование подтверждено: {self.booking}")
        self.log_action(f"Оффлайн: бронирование #{self.booking.get_booking_id()} подтверждено")

#12 СЕРИАЛИЗАЦИЯ И ДЕСЕРИАЛИЗАЦИЯ
def save_to_file(objects: List, filename: str):
    """Сохранение объектов в файл в формате JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([obj.to_dict() for obj in objects], f, ensure_ascii=False, indent=4)

def load_from_file(filename: str, cls):
    """Загрузка объектов из файла в формате JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [cls.from_dict(item) for item in data]


#ПРИМЕР ИСПОЛЬЗОВАНИЯ
# --- Создание клиентов ---
alice = Customer(1, "Алиса Иванова", 28)
boris = Customer(2, "Борис Смирнов", 45)

# --- Создание номеров через фабрику ---
room1 = RoomFactory.create_room("standard", 101, 2, 3500.0, True, has_tv=True)
room2 = RoomFactory.create_room("deluxe", 102, 3, 5200.0, True, has_jacuzzi=True)
room3 = RoomFactory.create_room("suite", 103, 5, 8000.0, True, number_of_rooms=3)

# --- Онлайн-бронирование для Алисы ---
user_online = {"role": "guest"}
online_process = OnlineBookingProcess(alice, room1, "01-05-2025", "05-05-2025", user=user_online)
online_process.book_room()

# --- Добавление услуг через рецепцию ---
online_process.user = {"role": "receptionist"}
online_process.add_service("Завтрак", 800.0)
online_process.add_service("Поздний выезд", 1200.0)

# --- Итоговая стоимость брони ---
print(f"\n Общая сумма онлайн-бронирования: {online_process.calculate_total()}₽")

# --- Генерация отчета и вывод в консоль ---
print("\n Отчет по бронированию:")
print(online_process.booking.generate_report())

# --- Запрос на изменение даты через цепочку обязанностей ---
online_process.booking.request_change("date", "Продление до 06-05-2025")

# --- Оффлайн-бронирование для Бориса ---
user_offline = {"role": "manager"}
offline_process = OfflineBookingProcess(boris, room3, "10-05-2025", "13-05-2025", user=user_offline)
offline_process.book_room()

# --- Удаление и добавление услуг ---
offline_process.add_service("Трансфер", 2000.0)
offline_process.add_service("Прачечная", 600.0)
offline_process.remove_service("Прачечная")

print(f"\n Общая сумма оффлайн-бронирования: {offline_process.calculate_total()}₽")

# --- Генерация и печать отчета ---
print("\n Отчет по бронированию:")
print(offline_process.booking.generate_report())

# --- Сохранение данных ---
save_to_file([online_process.booking, offline_process.booking], "bookings.json")
print("\n Бронирования сохранены в bookings.json")

# --- Чтение из файла и печать ---
loaded_bookings = load_from_file("bookings.json", Booking)
print("\n Загрузка бронирований из файла:")
for booking in loaded_bookings:
    print(booking.generate_report())
    print("-" * 40)