from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import (
    Attachment,
    Comment,
    Feedback,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    User,
)


class RegistrationForm(UserCreationForm):
    # Модель/форма RegistrationForm

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
        }),
    )
    patronymic = forms.CharField(
        max_length=150,
        required=False,
        label='Отчество',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите отчество (необязательно)',
        }),
    )
    email = forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru',
        }),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'patronymic',
                  'email', 'phone', 'password1', 'password2')
        labels = {
            'username': 'Логин',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Придумайте логин',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'


class LoginForm(AuthenticationForm):
    # Модель/форма LoginForm

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        }),
    )


class TicketForm(forms.ModelForm):
    # Модель/форма TicketForm

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'category', 'priority')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Кратко опишите проблему',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Подробно опишите вашу проблему или вопрос...',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = TicketCategory.objects.filter(is_active=True)


class CommentForm(forms.ModelForm):
    # Модель/форма CommentForm

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Ваш комментарий',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ответ или уточнение...',
            }),
        }


class AttachmentForm(forms.ModelForm):
    # Модель/форма AttachmentForm

    class Meta:
        model = Attachment
        fields = ('file',)
        labels = {
            'file': 'Прикрепить файл',
        }
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }


class FeedbackForm(forms.ModelForm):
    # Модель/форма FeedbackForm

    class Meta:
        model = Feedback
        fields = ('name', 'email', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш e-mail',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема обращения',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите ваш вопрос или предложение...',
            }),
        }


class ProfileEditForm(forms.ModelForm):
    # Модель/форма ProfileEditForm

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic', 'email', 'phone', 'bio', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TicketStatusForm(forms.Form):
    # Модель/форма TicketStatusForm

    status = forms.ModelChoiceField(
        queryset=TicketStatus.objects.all(),
        label='Новый статус',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    assignee = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['SUPPORT', 'ADMIN']),
        required=False,
        label='Исполнитель',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
