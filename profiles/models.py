from django.db import models

# Create your models here.


class Test(models.Model):
	test = models.TextField(verbose_name='Тест')
	time_limit = models.DecimalField(verbose_name='Время', default=10, decimal_places=2, max_digits=6, null=True)
	pass_score = models.DecimalField(verbose_name='Пороговый балл', default=5, decimal_places=2, max_digits=6, null=True)


class Question(models.Model):
	test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name='Тест')
	question = models.TextField(verbose_name='Текст вопроса')
	point = models.DecimalField(verbose_name='Количество баллов за вопрос', default=1, decimal_places=2, max_digits=6)


class Answer(models.Model):
	question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE, verbose_name='Вопрос')
	correct = models.BooleanField(verbose_name='Правильный ответ?', default=False, null=False)
	answer = models.TextField(verbose_name='Текст ответа')


class Passed_question(models.Model):
	user_uuid = models.UUIDField()
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
	date = models.DateTimeField(auto_now=True)


class Secret_Santa(models.Model):
	group_uuid = models.UUIDField()
	name = models.TextField(verbose_name='Имя игрока')
	type_link = models.TextField(verbose_name='Тип ссылки')
	link = models.TextField(verbose_name='Ссылка игрока')
	santa_for = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
	wish_list = models.TextField(verbose_name='Пожелания', null=True)
	limit = models.DecimalField(verbose_name='Ограничение на стоимость', decimal_places=2, max_digits=8, null=True)

