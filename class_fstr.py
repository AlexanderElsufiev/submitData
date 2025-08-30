


import psycopg2
import numpy as np
import pandas as pd


from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
import json


# class PerevalDatabase:
class Fstr:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Установка соединения с БД"""
        try:
            self.connection = psycopg2.connect(  # = conn
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('FSTR_DB_LOGIN'),
                password=os.getenv('FSTR_DB_PASS'),
                host=os.getenv('FSTR_DB_HOST', 'localhost'),
                port=os.getenv('FSTR_DB_PORT', '5432')
            )
            # self.connection = psycopg2.connect(**self.connection_params)
            return True
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()


    def zapusk_sql(self,file_name):
        """ ПРОГРАММА ЗАПУСКА SQL НА ДЕЙСТВИЕ НАД ТАБЛИЦЕЙ, ВТЧ ПЕРЕСОЗДАНИЕ """
        rez=False
        with open(file_name, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Подключаемся и выполняем
        self.connect()
        conn = self.connection
        cursor = conn.cursor()

        try:
            cursor.execute(sql_script)
            conn.commit()
            # print("Таблица dann_pr пересоздана успешно!")
            print(f"Программа {file_name} отработала успешно!")
            rez=True
        except Exception as e:
            print(f"Программа {file_name} выдала Ошибка: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return rez


    def zapusk_sql_progr(self, progr):
        """ ЗАПУСК ПРОИЗВОЛЬНОЙ ПРОГРАММЫ, НАПИСАННОЙ ВНУТРИ ПИТОНА, С ЧТЕНИЕМ РЕЗУЛЬТАТА
        progr='select max(id) from pereval_images' """
        rez=False
        rz=self.connect()
        conn = self.connection
        cursor = conn.cursor() # Создание курсора для выполнения SQL-запросов

        try:
            cursor.execute(progr)  # Выполнение SQL-запроса
            conn.commit()  # КОММИТ
            rows = cursor.fetchall()  # Извлечение всех строк результата
            # Получение названий столбцов
            col_names = [desc[0] for desc in cursor.description]
            # rez = {'col': col_names, 'dann': rows}
            rez = {'col': col_names, 'rows': rows}
        except Exception as e:
            print(f"Программа  выдала Ошибку: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return rez





    def dannie_read_row(self,name="dannie"):
        """ чтение всех данных из таблицы, В СЫРОМ ВИДЕ. А НЕ МАТРИЦА"""
        rez=self.zapusk_sql_progr(f"SELECT * FROM {name} ")
        return rez



    def dannie_read(self,name="dannie"):
        """ чтение всех данных из таблицы, превращение в матрицу"""
        rez=self.dannie_read_row(name)
        if rez !=False:
            try:
                # Преобразование данных в массив numpy
                rows = rez['rows']
                col_names = rez['col']
                data = np.array(rows)
                data2 = pd.DataFrame(data, columns=col_names)
                rez['data'] = data2
                rez['dann'] = data
                # rez = {'col': col_names, 'data': data2, 'dann': data}
            except Exception as e:
                print(f"Программа перевода данных в массив NumPy выдала Ошибку: {e}")
        return rez





#########################################################

    # ПРОГРАММА ЗАПУСКАЕТСЯ ИЗ API/VIEWS.PY ИЗ МЕТОДА POST
    # def my_post(self, submitData):
    def my_post(self, raw_data, images):
        """ целевая программа собственно записи в базу данных
        ОТЛИЧИЕ ОТ СТАРОГО ВАРИАНТА - МАКСИМАЛЬНЫЙ ID ФОТО БЕРЁТСЯ ИЗ ТАБЛИЦЫ ПЕРЕВАЛОВ,
        ДАЖЕ ЕСЛИ ФОТО ЕЩЁ НЕ ЗАГРУЖЕНО ПРЕЖНИМ ПОЛЬЗОВАТЕЛЕМ"""
        submitData={'raw_data':raw_data,'images':images}
        rez=False
        rz=self.connect()
        conn = self.connection
        cursor = conn.cursor() # Создание курсора для выполнения SQL-запросов

        # print('предварительная обработка')
        # чтение текущих максимальных значений id
        # ОДНОВРЕМЕННО МАКСИМАЛЬНЫЕ ID ПЕРЕВАЛА И ID ФОТОГРАФИИ В ПЕРЕВАЛЕ
        rez = self.zapusk_sql_progr(
            'select id,images from pereval_added where id in (select max(id) as id_ from pereval_added)')
        max_id_pereval = rez['rows'][0][0]
        max_fotos = rez['rows'][0][1]['images']
        max_id_image = 0
        for im in max_fotos:
            max_id_image = max(max_id_image, im['id'])

        # преобразование данных с добавлением новых id
        img = []
        # images=submitData['images']
        images=images['images']
        for im in images:
            max_id_image += 1
            im['id'] = max_id_image
            img.append({'title': im['title'], 'id': im['id']})

        max_id_pereval += 1
        submitData['id'] = max_id_pereval
        submitData['img'] = {'images': img} #только описания фотографий

        try:
            # запись данных о перевале
            cursor.execute("""
                    INSERT INTO "public"."pereval_added" ("id", "date_added", "raw_data", "images")
                    VALUES (%s, NOW(), %s, %s)
                """, (
                submitData['id'],
                json.dumps(submitData["raw_data"]),
                json.dumps(submitData["img"])
            ))

            conn.commit()  # КОММИТ

            # тепер запись собственно фотографий, по одной!
            for im in images:
                cursor.execute("""
                        INSERT INTO "public"."pereval_images" ("id", "date_added", "img")
                        VALUES (%s, NOW(), %s)
                    """, (im['id'],im['img'])
                               )
                conn.commit()  # КОММИТ
            rez=True

        except Exception as e:
            print(f"Ошибка при записи: {e}")
            conn.rollback()  # Откатываем изменения при ошибке
            rez=False

        finally:# Закрытие курсора и соединения
            cursor.close()
            conn.close()
        print('В БАЗУ ДАННЫХ СДЕЛАНА ЗАПИСЬ')
        return rez


































def dann_zapis(dann):  # программа записи в мою базу
    names = ['metod', 'x1', 'x2', 'ogr', 'tip', 'vid', 'y', 'spros', 'yy', 'spros_','time']
    names_str = ['metod']
    names_int = ['tip', 'vid']
    names_float = [ 'x1', 'x2', 'ogr', 'y', 'spros', 'yy', 'spros_','time']

    # print(f'zapis_dann==\n{dann}')

    l = len(dann)

    col = dann.columns
    # print(f'col=={col} len=={l}')
    inserts = []

    for (index, row) in dann.iterrows():
        str_ = []
        for nm in names:
            if nm in col:
                zn=row[nm];
                if nm in names_str:
                    str_.append(str(zn))
                if nm in names_int:
                    str_.append(int(zn))
                if nm in names_float:
                    str_.append(float(zn))

        str_ = tuple(str_)
        inserts.append(str_)

    names_ = '';
    vals = '';
    i = -1
    for nm in names:
        if nm in col:
            i += 1;
            if i == 0:
                names_ = nm;vals = '%s'
            else:
                names_ = f'{names_},{nm}';vals = vals + ', %s'
    comand = f'INSERT INTO dannie2({names_}) VALUES ({vals})'
    # print(f'comand==={comand}')

    conn = conn_param() #ПАРАМЕТРЫ СОЕДИНЕНИЯ

    # Создание курсора
    cur = conn.cursor()

    # inserts==[(2, 1, 3)]
    # Вставка данных в таблицу
    # cur.executemany('INSERT INTO dannie2(x1,tip,y) VALUES (%s, %s, %s)', inserts)
    cur.executemany(comand, inserts)
    # Сохранение изменений
    conn.commit()

    # # Проверка: чтение и вывод данных
    # cur.execute('SELECT * FROM dannie2');rows = cur.fetchall()
    # print("Записанные данные:")
    # for row in rows:print(row)

    # Закрытие соединения
    cur.close();
    conn.close()











