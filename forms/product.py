from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField, Field
from wtforms import SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    content = TextAreaField("Описание")
    photo = Field('Фото', validators=[DataRequired()])
    connection = StringField('Связаться с нами(введите телефон)', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
    submit = SubmitField('Добавить')