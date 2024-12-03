from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas
from .database import SessionLocal, engine
from .schemas import Application, Message, UpdateStatus
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiosmtplib
from email.mime.text import MIMEText
from app.schemas import EmailVerificationCreate, EmailVerificationCheck
from datetime import datetime, timedelta
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as torchvision_models
from PIL import Image
from fastapi import Form
import io
from io import BytesIO
import re
import random
import string
import os
import uuid
import base64
from fastapi.security import OAuth2PasswordBearer

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

# Настройки для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация FastAPI приложения
app = FastAPI()

UPLOAD_DIR = "static/photos"  # Папка для сохранения изображений
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Настроим FastAPI для обслуживания статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS настройки - можно расширить для работы с внешними доменами, если нужно
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение папки static для хранения и доступа к изображениям
app.mount("/static", StaticFiles(directory="static"), name="static")

#------------------------------------------------------------------------------#

# Функция для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для хеширования пароля
def hash_password(password: str):
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Генерация случайного кода
def generate_verification_code():
    return str(random.randint(100000, 999999))  # 6-значный код

# Конвертация изображения из base64 в файл
async def Image_Converter(Hax_Value: str):
    Hax_Value = Hax_Value + "=" * ((4 - len(Hax_Value) % 4) % 4)  # Добавляем знаки '=' для корректного base64 формата
    random_name = str(uuid.uuid4())
    img_path = f"./static/{random_name}.jpg"
    os.makedirs("static", exist_ok=True)
    with open(img_path, 'wb') as decodeit:
        decodeit.write(base64.b64decode(Hax_Value))
    img_url = f"http://localhost:8000/static/{random_name}.jpg"
    return img_url

class EmailRequest(BaseModel):
    email: str

async def send_email(recipient: str, code: str):
    # Настройка параметров письма
    sender = "denislopushansky@yandex.ru"  # замените на ваш адрес
    subject = "Подтверждение регистрации"
    content = f"Ваш код подтверждения: {code}"

    # Создаем письмо
    message = MIMEText(content)
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject

    # Отправляем письмо через SMTP
    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.yandex.ru",  # замените на ваш SMTP-сервер
            port= 465,
            username="denislopushansky@yandex.ru",
            password="ftelxkvdkjvsjiyl",
            use_tls=True
        )
    except Exception as e:
        print("Ошибка отправки:", e)
        raise HTTPException(status_code=500, detail="Ошибка при отправке письма")
    
async def save_and_crop_image(file: UploadFile):
    try:
        # Прочитать изображение из файла
        image = Image.open(io.BytesIO(await file.read()))
        
        # Применить обрезку изображения (например, до 150x150 пикселей)
        image = image.resize((150, 150))
        
        # Генерация уникального имени файла
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Сохранение изображения после обрезки
        image.save(file_path, "JPEG")
        
        # Возвращаем путь к изображению
        return f"/static/photos/{filename}"
    
    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        raise HTTPException(status_code=400, detail="Ошибка обработки изображения")
    

 
#------------------------------------------------------------------------------#

# CRUD для Application
@app.post("/applications/", response_model=schemas.Application)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    print(application.dict())
    db_application = models.Application(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/applications/", response_model=list[schemas.Application])
def get_applications(
    status: str = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    query = db.query(models.Application)
    if status:
        query = query.filter(models.Application.status == status)
    return query.offset(skip).limit(limit).all()

@app.get("/applications/{application_id}", response_model=schemas.Application)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return application

@app.delete("/applications/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    db_application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if db_application:
        db.delete(db_application)
        db.commit()
        return {"message": "Заявка успешно удалена"}
    raise HTTPException(status_code=404, detail="Заявка не найдена")

@app.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int, status: UpdateStatus, db: Session = Depends(get_db)
):
    db_application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    db_application.status = status.status
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/applications/email/{email}")
def get_applications_by_email(email: str, db: Session = Depends(get_db)):
    applications = db.query(models.Application).filter(models.Application.email == email).all()
    return applications

# CRUD для Message
@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages/{message_id}", response_model=schemas.Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return message

@app.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return {"message": "Сообщение успешно удалено"}
    raise HTTPException(status_code=404, detail="Сообщение не найдено")

# Дополнительные маршруты
@app.get("/statistics/")
async def get_statistics():
    with engine.connect() as connection:
        # Запросы к базе данных
        total_users = connection.execute(text("SELECT COUNT(*) FROM users")).scalar()
        total_applications = connection.execute(text("SELECT COUNT(*) FROM applications")).scalar()
        completed_applications = connection.execute(
            text("SELECT COUNT(*) FROM applications WHERE status = 'Completed'")
        ).scalar()

    # Возврат результата в формате JSON
    return {
        "total_users": total_users,
        "total_applications": total_applications,
        "completed_applications": completed_applications
    }

@app.post("/convert_image", tags=["IMAGE"])
async def convert_image(Hax_Value: str):
    img_path = await Image_Converter(Hax_Value)
    return {"converted_image_url": img_path}

# Регистрация пользователя
@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,  # Сохраняем имя
        last_name=user.last_name,     # Сохраняем фамилию
        photo_url=user.photo_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Авторизация пользователя
@app.post("/login/")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Полученные данные: {user}")  # Логирование полученных данных
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверные учетные данные")
    
    # Возвращаем данные пользователя, включая имя и фамилию
    return {
        "message": "Вход успешен",
        "id": db_user.id,
        "first_name": db_user.first_name,  # Предположим, что в модели User есть поле first_name
        "last_name": db_user.last_name, # Аналогично для last_name
        "city": db_user.city,
        "photo_url": db_user.photo_url
    }

@app.post("/send-confirmation-email/")
async def send_confirmation_email(request: EmailRequest):
    await send_email(request.email)
    return {"message": "Письмо с подтверждением отправлено"}

@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    first_name: str = Form(None),
    last_name: str = Form(None),
    city: str = Form(None),
    email: str = Form(None),
    file: UploadFile = None,
    db: Session = Depends(get_db),
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновление данных
    if first_name:
        db_user.first_name = first_name
    if last_name:
        db_user.last_name = last_name
    if city:
        db_user.city = city
    if email:
        db_user.email = email

    # Обработка файла
    if file:
        file_location = f"{UPLOAD_DIR}/{uuid.uuid4()}_{file.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(file.file.read())
        db_user.photo_url = f"/static/photos/{file_location.split('/')[-1]}"

    db.commit()
    db.refresh(db_user)
    return db_user


# Эндпоинт для удаления пользователя
@app.delete("/delete-user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}

@app.post("/send-verification-code/")
async def send_verification_code(email_request: EmailRequest, db: Session = Depends(get_db)):
    email = email_request.email

    # Проверяем, что email корректный
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(status_code=400, detail="Некорректный e-mail")

    # Генерируем код
    code = generate_verification_code()

    # Сохраняем в базу данных
    verification_entry = models.EmailVerification(email=email, code=code, expires_at=datetime.utcnow() + timedelta(minutes=10))
    db.add(verification_entry)
    db.commit()

    # Сохраняем код в базе данных или куда необходимо
    await send_email(email_request.email, code)
    return {"message": "Код подтверждения отправлен на ваш email"}

#Проверим код на соответствие и срок действия.
@app.post("/reset-password/")
async def reset_password(data: EmailVerificationCheck, db: Session = Depends(get_db)):
    try:
        verification = db.query(models.EmailVerification).filter(
            models.EmailVerification.email == data.email,
            models.EmailVerification.code == data.code
        ).first()

        if not verification or verification.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Неверный код или код истёк")

        hashed_password = hash_password(data.new_password)

        user = db.query(models.User).filter(models.User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.password_hash = hashed_password
        db.commit()

        return {"message": "Пароль успешно сброшен"}
    except Exception as e:
        print(f"Ошибка при сбросе пароля: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка при сбросе пароля")

@app.post("/upload_image/")
async def upload_image(file: UploadFile):
    image_url = await save_and_crop_image(file)
    return {"image_url": image_url}


# Загрузка модели
class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']  # Названия ваших классов
model = torchvision_models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, len(class_names))
model.load_state_dict(torch.load('C:/Users/Никита/Desktop/Backend_ZP23/app/trash_classifier.pth', map_location=torch.device('cpu')))
model.eval()  # Перевод модели в режим оценки

# Трансформация изображения
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def predict(image: Image.Image):
    # Преобразование изображения в тензор
    image = transform(image).unsqueeze(0)  # Добавляем batch dimension
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
        predicted_class = class_names[predicted.item()]
    return predicted_class, confidence

# Маршрут для классификации
@app.post("/classify/")
async def classify_image(file: UploadFile = File(...)):
    try:
        # Открываем изображение
        image = Image.open(BytesIO(await file.read())).convert("RGB")
        predicted_class, confidence = predict(image)
        
        # Возвращаем результат
        return {
            "class": predicted_class,
            "confidence": confidence
        }
    except Exception as e:
        return {"error": str(e)}

