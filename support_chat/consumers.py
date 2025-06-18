import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EssenseHouse.settings')
django.setup()

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer



class QuestionChatConsumer(AsyncWebsocketConsumer):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    async def connect(self):
        from urllib.parse import parse_qs
        try:
            await self.accept()

            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            if not token:
                await self.close(code=4001)
                return

            self.user = await self.authenticate_user(token)
            if not self.user:
                await self.close(code=4001)
                return

            # Инициализация чата после успешной аутентификации
            self.question_id = self.scope['url_route']['kwargs']['question_id']
            self.room_group_name = f'chat_{self.question_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            print("Добавлен в группу", self.room_group_name)

            await self.send(text_data=json.dumps({'status': 'connected'}))

            print(f"Успешное подключение пользователя {self.user.email}")

        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
            await self.close(code=4001)

    @database_sync_to_async
    def authenticate_user(self, token):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        try:
            auth = JWTAuthentication()
            validated_token = auth.get_validated_token(token)
            return auth.get_user(validated_token)
        except Exception:
            return None

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            print(f"Соединение закрыто с кодом: {close_code}")
        except Exception as e:
            print(f"Ошибка при отключении: {str(e)}")

    async def receive(self, text_data):
        try:
            # Проверка инициализации
            if not all(hasattr(self, attr) for attr in ['user', 'room_group_name']):
                await self.close(code=4001)
                return

            data = json.loads(text_data)
            message = data['message']
            is_admin = data.get('is_admin', False)

            # Проверка прав доступа
            if not self.user.is_authenticated:
                await self.send(json.dumps({'error': 'Требуется авторизация'}))
                await self.close(code=4001)
                return

            # Получение связанного вопроса
            user_question = await self.get_user_question()
            if not user_question:
                await self.send(json.dumps({'error': 'Вопрос не найден'}))
                await self.close(code=4004)
                return

            # Создание сообщения
            chat_message = await self.create_chat_message(
                user_question=user_question,
                message=message,
                is_admin=is_admin
            )
            print(f"Создано сообщение ID: {chat_message.id}")

            # Отправка в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': f"{self.user.first_name} {self.user.last_name}",
                    'is_admin': is_admin,
                    'timestamp': str(chat_message.timestamp)
                }
            )

        except json.JSONDecodeError:
            await self.send(json.dumps({'error': 'Неверный формат JSON'}))
        except Exception as e:
            print(f"Ошибка обработки сообщения: {str(e)}")
            await self.send(json.dumps({'error': 'Внутренняя ошибка сервера'}))

    @database_sync_to_async
    def get_user_question(self):
        from backend.models import UserQuestionHouse
        try:
            return UserQuestionHouse.objects.get(id=self.question_id)
        except UserQuestionHouse.DoesNotExist:
            return None

    @database_sync_to_async
    def create_chat_message(self, user_question, message, is_admin):
        from support_chat.models import ChatMessage
        return ChatMessage.objects.create(
            user_question=user_question,
            sender=self.user,
            message=message,
            is_admin=is_admin,
            is_read=False
        )

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username'],
                'is_admin': event['is_admin'],
                'timestamp': event.get('timestamp')
            }))
        except Exception as e:
            print(f"Ошибка отправки сообщения: {str(e)}")