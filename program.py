

#  КОМАНДА ЗАПУСКА  python program.py


from class_fstr import *

# СОЗДАНИЕ ЭКЗЕМПЛЯРА КЛАССА
dd=Fstr()


#############################################################
# ЧАСТЬ 1 = ПОДГОТОВКА БАЗЫ ДАННЫХ

# СОЗДАНИЕ ИСХОДНОЙ БАЗЫ ДАННЫХ И НЕКОТОРЫХ УЧЕБНЫХ ЗАПИСЕЙ В НЕЙ
try:
    # ЗАПУСК файла 'my_sql_prob.sql' НА ПЕРЕСОЗДАНИЕ ТАБЛИЦЫ
    # ЗАНОВО НЕ СОЗДАЁТСЯ, НО ОШИБКУ ПРОГЛАТЫВАЕТ. РАБОТАЕТ ДАЛЕЕ
    dd.zapusk_sql('sql/init_database.sql')

    # ЗАПУСК файла 'init_database_add_status_field.sql' НА ДОБАВЛЕНИЕ ПОЛЯ STATUS В ТАБЛИЦУ
    dd.zapusk_sql('sql/init_database_add_status_field.sql')

    # ЗАПУСК файла 'init_database_add_status_field.sql' НА ДОБАВЛЕНИЕ ЕЩЁ ПО 1 СТРОКЕ ДАННЫХ C ID=2
    # dd.zapusk_sql('sql/init_database_new_str.sql')

except :
    print('ВИДИМО ТАБЛИЦЫ УЖЕ БЫЛИ')


#############################################################

# ЧАСТЬ 2 = ПОДГОТОВКА ДАННЫХ ДЛЯ ЗАПИСИ


# ФОРМИРУЮ ДАННЫЕ ДЛЯ БУДУЩЕЙ ЗАПИСИ =submitData


#ДАННЫЕ О ЧЕЛОВЕКЕ БЕРУТСЯ ПРОСТО КАК КОПИЯ ПЕРВЫХ ПОПАВШИХСЯ ИМЕЮЩИХСЯ ПЕРВЫХ В СПИСКЕ ЗАГРУЖЕННЫХ
rez=dd.dannie_read_row('pereval_added')
raw_data=rez['rows'][0][2]

# ДАННЫЕ О ФОТОГРАФИЯХ БЕРУТСЯ ТАК ЖЕ ПЕРВЫЕ ПОПАВШАЯСЯ ФОТО, В 3 ИЛИ БОЛЕЕ ЭКЗЕМПЛЯРАХ
rez=dd.dannie_read_row('pereval_images')
foto=rez['rows'][0][2]


# ФОРМИРОВАНИЕ СОБСТВЕННО СПИСКА ФОТОК
images=[{'title':'фото1','img':foto},{'title':'фото2','img':foto},{'title':'foto_3','img':foto}]
#ЕСЛИ ХОЧЕТСЯ ОПРОБОВАТЬ СБОЙНУЮ СИТУАЦИЮ, КОГДА ФОТО НЕ ПОСЛАЛОСЬ - ЗДЕСЬ ОТСУТСТВУЕТ САМО ФОТО2.
# images=[{'title':'фото1','img':foto},{'title':'фото2'},{'title':'foto_3','img':foto}]

# СВЕДЕНИЕ ВОЕДИНО ДАННЫХ ПО ПЕРЕВАЛУ И ФОТОГРАФИЙ
submitData = {'raw_data':raw_data, 'images':images}


#############################################################
# ЧАСТЬ 3 = СОБСТВЕННО ЗАПИСЬ В БАЗУ
# rez=dd.POST( submitData)
# print(f'rez={rez}')


#############################################################
# ЧАСТЬ 4 = ПРОВЕРКА ЧТО ПОЛУЧИЛОСЬ В БАЗЕ В РЕЗУЛЬТАТЕ

# ЧТЕНИЕ ДАННЫХ ПЕРЕВАЛЫ
print('============================================')
rez=dd.dannie_read('pereval_added')
data=rez['data']
col=rez['col']
print(f'col={col}')
print(f'data={data}')
print('============================================')

# ЧТЕНИЕ ДАННЫХ САМИ ФОТОРГАФИИ НЕ В ТАБЛИЦУ
rez=dd.dannie_read('pereval_images')
for ff in rez['rows']:print(f'ff={ff}');#print('--------------------')
col=rez['col']
print(f'col={col}')
print('============================================')





# # ОДНОВРЕМЕННО МАКСИМАЛЬНЫЙ ID ПЕРЕВАЛА И ФОТОГРАФИИ В ПЕРЕВАЛЕ
# print('удаление')
# rez = dd.zapusk_sql_progr('delete from pereval_added where id>1')
# rez = dd.zapusk_sql_progr('delete from pereval_images where id>1')
#
# rez = dd.zapusk_sql_progr('select * from pereval_images ')
# print(f'rez={rez}')

