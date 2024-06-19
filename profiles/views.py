from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Test, Question, Answer, Passed_question, Secret_Santa
import requests
import json
import datetime
from uuid import uuid4
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv


# Create your views here.
load_dotenv()
# ============================================================================================================================================


def home(request):

    user_name = uuid4()

    context = {
        'user_name': user_name,
    }

    return render(request,'profiles/home.html', context)


# ============================================================================================================================================
# WEATHER


class WeatherParameter:
    def __init__(self, name, value, units):
        self.name = name
        self.value = value
        self.units = units


def create_wether_objects(weather_parameter_dict):
    date = datetime.datetime.strptime(weather_parameter_dict['datetime'], "%Y-%m-%d").strftime('%d.%m.%Y')
    date_time = WeatherParameter(name='Дата', value=date, units='')

    temperature = WeatherParameter(name='Температура', value=round(weather_parameter_dict['temp']), units='°C')
    feels_like = WeatherParameter(name='По ощущениям', value=round(weather_parameter_dict['feelslike']), units='°C')
    humidity = WeatherParameter(name='Влажность', value=round(weather_parameter_dict['humidity']), units='%')
    precipitation = WeatherParameter(name='Осадки', value=round(weather_parameter_dict['precip']), units='мм')

    speed = round(float(weather_parameter_dict['windspeed']) * 1000 / 3600)
    wind_speed = WeatherParameter(name='Скорость ветра', value=speed, units='м/с')

    visibility = WeatherParameter(name='Видимость', value=round(weather_parameter_dict['visibility']), units='км')
    solar_radiation = WeatherParameter(name='Солнечная радиация', value=round(weather_parameter_dict['solarradiation']), units='Вт/м²')

    description = WeatherParameter(name='description', value=weather_parameter_dict['description'], units='')
    conditions = WeatherParameter(name='conditions', value=weather_parameter_dict['conditions'], units='')

    weather_parameter_list = [date_time, temperature, feels_like, humidity, precipitation, wind_speed, visibility,
                              solar_radiation]
    
    return weather_parameter_list


def weather(request):
    if request.method == 'POST':
        ru_city_name = request.POST.get('city')
        city_name = ru_city_name
        weather_key = os.getenv('weather_key')

        response = requests.request("GET", f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_name}?unitGroup=metric&include=days&key={weather_key}&contentType=json")
        
        if response.status_code == 200:
            json_data = response.json()

            temperature = f"{round(json_data['days'][0]['temp'])} °C"
            locale_name = json_data['resolvedAddress']

            if 'Україна' in locale_name:
                locale_name = ''

            weather_parameter_list = create_wether_objects(json_data['days'][0])

            forecast_weather_parameter_list_1 = create_wether_objects(json_data['days'][1])
            forecast_weather_parameter_list_2 = create_wether_objects(json_data['days'][2])
            forecast_weather_parameter_list_3 = create_wether_objects(json_data['days'][3])
            forecast_weather_parameter_list_4 = create_wether_objects(json_data['days'][4])
            forecast_weather_parameter_list_5 = create_wether_objects(json_data['days'][5])
            forecast_weather_parameter_list_6 = create_wether_objects(json_data['days'][6])
            forecast_weather_parameter_list = [forecast_weather_parameter_list_1, forecast_weather_parameter_list_2, forecast_weather_parameter_list_3, 
                                               forecast_weather_parameter_list_4, forecast_weather_parameter_list_5, forecast_weather_parameter_list_6]

            context = {
                'temperature': temperature,
                'city_name': locale_name,
                'weather_parameter_list': weather_parameter_list,
                'information_text': '',
                'forecast_weather_parameter_list': forecast_weather_parameter_list,
                'status': True,
            }
        else:
            context = {
                'temperature': 'Ой...',
                'city_name': 'Ничего не нашлось, попробуйте ввести название города на английском',
                'status': False,
            }
    else:
        context = {
            'temperature': 'Погода',
            'city_name': '',
            'status': False,
        }

    return render(request,'profiles/weather.html', context)


# ============================================================================================================================================
# EXAM


def exam(request, user_name):
    test_id = 1
    
    test = Test.objects.get(id=test_id).test
    time_limit = int(Test.objects.get(id=test_id).time_limit)
    pass_score = int(Test.objects.get(id=test_id).pass_score)
    limit = 3

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
    if is_ajax:
        if request.method == 'GET':
            passed_question_list = list(Passed_question.objects.filter(user_uuid=user_name).values_list('question', flat=True).distinct())
            question = list()
            answer_list = list()

            if len(passed_question_list) < limit:
                question = list(Question.objects.filter(test=test_id).exclude(pk__in=passed_question_list).order_by('?')[:1].values())
                question_id = question[0]['id']
                answer_list = list(Answer.objects.filter(question=question_id).order_by('?').values())

                Passed_question(user_uuid=user_name, question=Question.objects.get(id=question_id), answer=None).save()

            context = {
                'list_question': question,
                'list_answers': answer_list,
            }

            return JsonResponse(context)
        
        if request.method == 'POST':
            data = json.load(request)
            todo = data.get('payload')

            if todo['question_id'] != []:
                passed_question = Question.objects.get(id=todo['question_id'][0])
                selected_answer_list = list(Answer.objects.filter(pk__in=todo['values']))
                Passed_question.objects.bulk_create([Passed_question(user_uuid=user_name, question=passed_question, answer=selected_answer) for selected_answer in selected_answer_list])
            
            return JsonResponse({'status': 'Todo added!'})
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        context = {
            'test_id': test_id,
            'test': test,
            'count': 0,
            'limit': limit,
            'time_limit': time_limit,
            'pass_score': pass_score,
            'user_name': user_name,
        }

        return render(request, 'profiles/exam.html', context)


def result_exam(request, user_name):

    result_list = Passed_question.objects.filter(user_uuid=user_name).select_related('question').select_related('answer').order_by('id')
    question_list = list(result_list.values_list('question', flat=True))
    answer_list = list(result_list.values_list('answer', flat=True))
    
    questions_of_attempt = Question.objects.filter(pk__in=question_list)
    answers_of_attempt = Answer.objects.filter(question__in=question_list)

    context = {
        'result_list': result_list,
        'questions_of_attempt': questions_of_attempt,
        'answers_of_attempt': answers_of_attempt,
        'answer_list': answer_list,
    }

    return render(request, 'profiles/result_exam.html', context)


# ============================================================================================================================================
# WEDDING


def wedding(request):

    return render(request, 'profiles/wedding.html')


def wedding_photo(request):

    return render(request, 'profiles/wedding_photo.html')


# ============================================================================================================================================
# SECRET SANTA


def secret_santa(request):

    text_result = ''
    
    if request.method == 'POST':
        number_players = int(request.POST.get('number_players'))

        try:
            limit = int(request.POST.get('limit'))
        except Exception as e:
            limit = None

        group_uuid = uuid4()
        
        for player in range(1, number_players + 1):
            name = request.POST.get(f'name_{player}')
            link = request.POST.get(f'email_{player}')

            if name != '' and link != '':
                Secret_Santa(group_uuid=group_uuid, name=name, type_link='Почта', link=link, limit=limit).save()

        shuffle_santa_player_id_list = list(Secret_Santa.objects.filter(group_uuid=group_uuid).order_by('?').values_list('id', flat=True))

        if shuffle_santa_player_id_list:
            for index, santa_player_id in enumerate(shuffle_santa_player_id_list):
                santa_player = Secret_Santa.objects.get(id=santa_player_id)

                if index == len(shuffle_santa_player_id_list) - 1:
                    santa_player.santa_for = Secret_Santa.objects.get(id=shuffle_santa_player_id_list[0])
                else:
                    santa_player.santa_for = Secret_Santa.objects.get(id=shuffle_santa_player_id_list[index + 1])

                santa_player.save(update_fields=['santa_for'])
        
        check_santa_players = Secret_Santa.objects.filter(group_uuid=group_uuid).exists()
        check_shuffle_santa_players = Secret_Santa.objects.filter(group_uuid=group_uuid).filter(santa_for=None).exists()

        if not check_shuffle_santa_players and check_santa_players:
            text_result = 'Игроки добавлены и перемешаны'
            check_result = True
            return redirect(f'/result_secret_santa/{group_uuid}')
        elif check_shuffle_santa_players and check_santa_players:
            text_result = 'Игроки добавлены, но не перемешаны, попробуйте сначала'
            check_result = False
        else:
            text_result = 'Что-то пошла не так, попробуйте сначала'
            check_result = False
    
    context = {
        'text_result': text_result,
    }

    return render(request, 'profiles/secret_santa.html', context)


def result_secret_santa(request, group_uuid):

    santa_players = Secret_Santa.objects.filter(group_uuid=group_uuid)

    if request.method == 'POST':
        send_confirm = request.POST.get('send_confirm')

        if send_confirm:
            for player in santa_players:
                send_email(player=player, later=False, request=request)                
        else:
            first_player = santa_players.order_by('id')[0]
            send_email(player=first_player, later=True, request=request)
        
        return redirect('/secret_santa')
    
    context = {
        'santa_players': santa_players,
    }

    return render(request, 'profiles/result_secret_santa.html', context)


def send_email(player, later, request):

    receiver = player.link

    result_secret_santa_link = request.build_absolute_uri()
    secret_santa_link = result_secret_santa_link.replace(f"result_secret_santa/{result_secret_santa_link.split('/')[-1]}", 'secret_santa')

    santa_mail_path = Path(__file__).resolve().parent / 'templates' / 'profiles' / 'santa_mail.html'
    with open(santa_mail_path, "r", encoding='utf-8') as f:
        santa_mail= f.read()

    if later:
        santa_mail = santa_mail.replace('text_of_msg', f'Чтобы разослать письма с Тайными Сантами, перейдите по ссылке')
        santa_mail = santa_mail.replace('name_santa_for', f'<a href="{result_secret_santa_link}" style="color: #d04c42;">Разослать</a>')
    else:
        name_santa_for = Secret_Santa.objects.get(id=player.santa_for_id).name
        santa_mail = santa_mail.replace('text_of_msg', f'Вы Тайный Санта для игрока')
        santa_mail = santa_mail.replace('name_santa_for', f'{name_santa_for}')

    if player.limit:
        limit = f'На стоимость подарков было <br>установлено ограничение <br>в {player.limit} рублей.'
    else:
        limit = f''

    santa_mail = santa_mail.replace('limit', limit)
    santa_mail = santa_mail.replace('secret_santa_link', f'<a href="{secret_santa_link}" trget="_blank">"Тайный Санта"</a>')
    
    server = os.getenv('SMTP_SERVER')
    port = os.getenv('PORT')
    username = os.getenv('MAIL_SENDER')
    password = os.getenv('MAIL_PASSWORD')
    sender = os.getenv('MAIL_SENDER')

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = 'Тайный Санта'
    msg.attach(MIMEText(santa_mail, 'html'))

    session = smtplib.SMTP(server, port)
    session.starttls()
    session.login(username, password)
    session.send_message(msg)
    session.quit()


# ============================================================================================================================================
# TEXT QUEST
# 
# Локация 1
# 
# 
# 
# 
# 
