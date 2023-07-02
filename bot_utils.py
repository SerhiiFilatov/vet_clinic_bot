import os
from environs import Env

from google.cloud import dialogflow_v2 as dialogflow
from google.auth.exceptions import DefaultCredentialsError



def date_time_dict(time_list):
    '''
    :param time_list: отфильтрованный список "времени без записи клиента"
    :return: словарь для колбек кнопок
    '''
    time_dict = {}
    for x in time_list:
        time_dict[x] = x
    return time_dict


async def check_dialogflow_connection(text):
    env = Env()

    credentials_path = "C:\\Users\\User\\Desktop\\_bot\\vet-akgc-a117714d8d74.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(env.str('DIALOGFLOW_PROJECT_ID'), "test_session")
    text_input = dialogflow.types.TextInput(text=text, language_code="en-US")
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session= session, query_input= query_input)

        if response.query_result:
            print("Подключение к Dialogflow успешно.")
        else:
            print("Ошибка подключения к Dialogflow.")

        fulfillment_text = response.query_result.fulfillment_text

    except DefaultCredentialsError:
        print("Ошибка аутентификации. Убедитесь, что у вас есть правильные учетные данные.")

    return fulfillment_text


