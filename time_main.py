# -*- coding: utf-8 -*-
#!/usr/bin/python3
import sys, os, math, csv, requests, json, webbrowser
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel, QWidget, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTranslator, QLocale
from PIL import Image
from my_forms import Ui_MainWindow
from datetime import datetime
from datetime import timedelta
from datetime import time 
import time
import resurse_rc


#Список путей к картинкам
my_patch_list=[]
#Список путей к картинкам для предварительного просмотра
my_patch_list_view=[]
#Папка темы
folder_theme = "Theme"
#Папка цветовой схемы
folder_color = "Color"
#Папка цифербладов
folder_face = "Face"
#Папка задних фонов
folder_bg = "Bg"
#Папка - стрелки часы
folder_hours = "hours"
#Папка - стрелки минуты
folder_minutes = "minutes"
#Папка - стрелки секунды
folder_seconds = "seconds"
#имя превью часов
img_time = "/time.png"
#имя превью часов при открытии
none_time_img = "none.png"
#Путь к папке для храниения CSV файла
patch_csv_folder = "data/"
#Файл настроек
filename_setting = "setting.txt"
#-------------------------------------------
class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.my_timer)

        # Добовляем в statusBar виджет label для отображения информации
        self.label_info = QLabel('Для работы программы примените выбранную тему и нажмите кнопку "СТАРТ"', self)
        self.label_info.setStyleSheet("color:#0095B2; margin-bottom:10px")
        self.label_info.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBar().addWidget(self.label_info, 1)
        
        self.ui.comboBox.currentIndexChanged.connect(self.fill_comboBox)
        #Клик на кнопку применить тему
        self.ui.pushButton.clicked.connect(self.my_patch_list)
        #Клик на кнопку Предпросмотр
        self.ui.pushButton_5.clicked.connect(self.my_images) 

        #Старт основного таймера
        self.ui.pushButton_6.clicked.connect(self.timer_start)
        #Стоп основного таймера
        self.ui.pushButton_7.clicked.connect(self.timer_stop) 

        #Обработчик клика по tabWidget (остановка таймеров)
        #self.ui.tabWidget.tabBarClicked.connect(self.click_tabWidget) 

        #Старт второго таймера
        self.ui.pushButton_4.clicked.connect(self.timer2_start)
        #Стоп второго таймера
        self.ui.pushButton_2.clicked.connect(self.timer2_stop)
        #Пауза второго таймера
        self.ui.pushButton_3.clicked.connect(self.timer2_pause)

        #Сохраняем настрйки при клике меню сохранить настрйоки
        self.ui.action.triggered.connect(self.save_setting) 
        #Открываем настрйки при клике меню открыть настрйоки
        self.ui.action_2.triggered.connect(self.load_setting) 
        #выход из программы
        self.ui.action_8.triggered.connect(self.my_close) 

        #Версия программы
        self.ui.action_3.triggered.connect(self.my_version)
        #Справка
        self.ui.action_4.triggered.connect(self.my_help) 
        #Открываем страницу автора на github
        self.ui.action_6.triggered.connect(self.my_site) 
        #Сохраняем под vMix (csv) файл
        self.ui.action_7.triggered.connect(self.save_as_csv)

        #переменная для таймера 2 (свое время)
        self.my_s = 0
        timer2 = 0  

        #Имя CSV файла при сохранении
        self.fname = "time_data"
        #путь к файлу CSV
        self.my_fileName = ''

        #Заполняем comboBox
        def mystart(self):
            try:
                root_patch = os.path.join(os.getcwd(),folder_theme)
                #Темы
                for theme in os.listdir(folder_theme):
                    self.ui.comboBox.addItem(theme)
                #назначаем время поумолчанию равным 00:00:00
                self.ui.label_6.setText('00:00:00')
                self.ui.label_5.setText('01:00:00')
                # Отображаем превью темы в label_8
                thema_default = self.ui.comboBox.currentText()
                patch_none = none_time_img
                pixmap = QPixmap(patch_none)
                self.ui.label_8.setPixmap(pixmap)
                #Загружаем предыдущие настройки
                #self.load_setting()
            except Exception as e:
                print(e)
        mystart(self)


    #получаем переменную пути для сохранения данных в csv файл
    def save_as_csv(self):
        try:
            global my_fileName
            options = QFileDialog.Options()
            options = QFileDialog.DontUseNativeDialog
            fileName =  QFileDialog.getSaveFileName(self,"Сохранение данных", patch_csv_folder , "Тип файлов CSV (*.csv)", options=options)
            #Отделяем тип файла
            type_f = fileName[1].split("(*")
            type_files = type_f[1].split(')')
            #если тип файла в выбраном файле есть то удаляем и подставляем свой тип файла
            if fileName:
                f1 = fileName[0] 
                f2 = f1.split('.')
                my_fileName = f2[0] + type_files[0]
            print(my_fileName)
            #применяем тему
            self.my_patch_list()
            #Запускаем таймер в зависимости от активной вкладки
            index = self.ui.tabWidget.currentIndex() 
            #запускаем системное врмея
            if int(index) == 0:
                self.timer2_stop() #метод
                self.timer.start(1000)
            #запускаем произвольное врмея
            if int(index) == 1:
                self.timer_stop() #метод
                self.timer2.start(1000)
        except Exception as e:
            print("Ошибка имени файла для сохранения - " + str(e))


    #Сохраняем файл csv
    def save_csv(self,hh,mm,ss,face,background):
        h = hh
        m = mm
        s = ss
        f = face
        bg = background
        try:
            with open(my_fileName, 'w', encoding='utf-8', newline='') as file:
                t = csv.writer(file)
                t.writerow((bg,f,h,m,s))
            #информируем о сохранении файла CSV
            self.label_info.setText('Данные сохраняются в '  + os.path.abspath(my_fileName)) 
            self.label_info.setStyleSheet("color:green; margin-bottom:10px") 
        except Exception as e:
            #останавливаем таймеры
            self.timer.stop()
            self.timer2.stop()
            #вызываем диалоговое окно сохранения
            self.save_as_csv()
            #Для пролоджения работы нажмите кнопку "СТАРТ"
            self.label_info_pause()


    #Для работы программы примените выбранную тему и нажмите кнопку "СТАРТ"
    def label_info_start(self):
        self.label_info.setText('Для работы программы примените выбранную тему и нажмите кнопку "СТАРТ"')
        self.label_info.setStyleSheet("color:#0095B2; margin-bottom:10px")


    #Для работы программы необходимо примените тему
    def label_info_apply(self):
        if len(my_patch_list)==0:
            self.label_info.setText('Для работы программы необходимо примените тему')
            self.label_info.setStyleSheet("color:red; margin-bottom:10px")


    #Очищаем label_info
    def label_info_clear(self):
        self.label_info.setText('')
        self.label_info.setStyleSheet("color:black; margin-bottom:10px")


    #Свой таймер пауза
    def label_info_pause(self):
        self.label_info.setText('Для пролоджения работы нажмите кнопку "СТАРТ"')
        self.label_info.setStyleSheet("color:#0095B2; margin-bottom:10px")       


    #Закрытие приложения из меню
    def my_close(self):
        self.close()


    #Сообщение о релизе программы
    def my_version(self):
        reply = QMessageBox.question(self, 'О релизе', 'Программа "Стрелочные часы для vMix"\n\nАвтор: Котов Александр Иванович\nE-mail: ItPython@yandex.ru\n\nРелиз программы от 19 февраля 2019 года ', QMessageBox.Close)


    def my_help(self):
        try:
            webbrowser.open('https://alecsandrkotov.github.io/Time', new = 2)
        except Exception as e:
            print (e)    


    #открываем страницу автора на github
    def my_site(self):
        try:
            webbrowser.open('https://alecsandrkotov.github.io', new = 2)
        except Exception as e:
            print (e)        


    #Сохранение настроек
    def save_setting(self):
        try:
            myfile = open(filename_setting, mode='w',encoding='utf-8')
            #поправка времени
            correctiontime = self.ui.spinBox.value()
            #тема
            theme = self.ui.comboBox.currentIndex()
            #циферблат
            face = self.ui.comboBox_3.currentIndex()
            #стрелки
            arrow = self.ui.comboBox_2.currentIndex()            
            #подложка
            bg = self.ui.comboBox_4.currentIndex() 
            #Вкладка переключения системного времени или произволного времени
            tab_select = self.ui.tabWidget.currentIndex() 
            #Прозвольный таймер время
            my_time = self.ui.timeEdit.text()

            #Словарь для сохранения настроек
            setting ={
                'correction_time': correctiontime,
                'theme': theme,
                'face': face,
                'arrow': arrow,
                'bg': bg,
                'tab_select': tab_select,
                'my_time': my_time
            }
            json.dump(setting, myfile)
            myfile.close()
        except Exception as e:
            print(e)
        

    def load_setting(self):
        try:
            myfile = open(filename_setting, mode='r',encoding='utf-8')
            json_data = json.load(myfile)
            #поправка времени 
            self.ui.spinBox.setValue(json_data['correction_time']) 
            #Позиция выбора темы
            self.ui.comboBox.setCurrentIndex(json_data['theme']) 
            #Позиция выбора стрелок
            self.ui.comboBox_2.setCurrentIndex(json_data['arrow'])  
            #Позиция выбора циферблата 
            self.ui.comboBox_3.setCurrentIndex(json_data['face'])
            #Позиция выбора подложки
            self.ui.comboBox_4.setCurrentIndex(json_data['bg'])  
            #Вкладка переключения системного времени или произволного времени
            self.ui.tabWidget.setCurrentIndex(json_data['tab_select'])  
            #свое время
            item_time = json_data['my_time'].split(':')
            finalTime = QtCore.QTime(int(item_time[0]),int(item_time[1]),int(item_time[2]))
            self.ui.timeEdit.setTime(finalTime)
            #предпросмотр темы
            self.my_images()
        except Exception as e:
            print(e)


    #останавливаем таймер не активной вкладки
    def click_tabWidget(self):
        index = self.ui.tabWidget.currentIndex() 
        #останавливаем системное врмея
        if int(index) == 0:
            self.timer.stop()
            self.timer2.stop()
        #останавливаем произвольное  врмея
        if int(index) == 1:
            self.timer.stop()
            self.timer2.stop()
        #Очищаем статусбар
        self.label_info_start()


    #Старт основного таймера
    def timer_start(self):
        #останавливаем свой таймер
        self.timer2.stop()
        #изменяем отображаемое значение
        self.ui.label_5.setText('01:00:00')
        #Запускаем таймер
        self.timer.start(1000)
        #Очищаем статусбар
        self.label_info_clear()
        #Проверяем применина тема или нет и выводим сообщение
        self.label_info_apply()


    #Стоп основного таймера
    def timer_stop(self):   
        self.timer.stop()
        self.ui.label_6.setText('00:00:00')
        self.ui.label_12.setText('00:00:00')
        #нажмите кнопку "СТАРТ"
        self.label_info_start()


    #Старт своего таймера
    def timer2_start(self):
        #останавливаем системное время
        self.timer.stop()
        #изменяем отображаемое значение
        self.ui.label_12.setText('00:00:00')
        self.ui.label_6.setText('00:00:00')
        self.timer2.start(1000)
        if 'pause' in globals():
            if pause == 0:
                self.my_s = 0
                timer2 = 0
        if not 'pause' in globals():
            self.my_s = 0
            timer2 = 0
        #Проверяем применина тема или нет и выводим сообщение
        self.label_info_apply()


    #Пауза своего таймера
    def timer2_pause(self):
        global pause
        pause = 1
        self.timer2.stop()
        #Очищаем статусбар
        self.label_info_clear()
        #Для работы программы нажмите кнопку "СТАРТ"
        self.label_info_pause()        


    #Стоп своего таймера
    def timer2_stop(self):
        global pause
        self.timer2.stop()
        set_time = self.ui.timeEdit.text()
        self.ui.label_5.setText(set_time)
        timer2 = 0
        pause = 0
        #Для работы программы примените выбранную тему и нажмите кнопку "СТАРТ"
        self.label_info_start()


    #Таймер с выставляемым временем
    def my_timer(self):
        global timer2
        #получаем время
        set_time = self.ui.timeEdit.text()
        #разбиваем на часы минуты и секунды (список)
        list_time = set_time.split(':')
        #назначаем значения соответствующим переменным
        timer2_h = int(list_time[0])
        timer2_m = int(list_time[1])
        timer2_s = int(list_time[2])
        #находим общее число секунд из всех данных
        sum_second = int((timer2_h*3600) + (timer2_m*60) + timer2_s)
        #Таймер
        self.my_s += 1
        timer2 = sum_second + self.my_s

        #Преобразовать секунды в время
        sec_of_time = time.strftime('%I:%M:%S', time.gmtime(timer2))
        #выводим на экран
        self.ui.label_5.setText(sec_of_time)

        my_time_vew = self.ui.label_5.text()
        list_my_time_vew = my_time_vew.split(':')

        hours = str(list_my_time_vew[0])
        minutes = str(list_my_time_vew[1])
        seconds = str(list_my_time_vew[2])

        #расчитываем смещение часовой стрелки в часе относительно минут
        if int(hours) == 12:
            hours = 0

        if int(hours) > 0:
            my_h = int(hours) * 5
            my_m = (int(minutes) / 12)
            my_hours = round(my_h + my_m)

        if int(hours) == 0:
            my_m = (int(minutes) / 12)
            my_hours = round( my_m)
  
        #если список с путями не пуст 
        if not len(my_patch_list)==0:
            #получаем ссылку на часовую стрелку
            if int(my_hours)  <= 9:
                h_file = f'hour_000{my_hours}.png'
                h = os.path.join(my_patch_list[1],folder_hours,h_file)
            if int(my_hours)  > 9:
                h_file = f'hour_00{my_hours}.png'
                h = os.path.join(my_patch_list[1],folder_hours,h_file)
            #получаем ссылку на минутную стрелку
            m_file = f'minute_00{minutes}.png'
            m = os.path.join(my_patch_list[1],folder_minutes,m_file)
            #получаем ссылку на секундную стрелку
            s_file = f'second_00{seconds}.png'
            s = os.path.join(my_patch_list[1],folder_seconds,s_file)
            f = my_patch_list[2]
            bg = my_patch_list[3]
            #вызываем метод сохранения в файл CSV
            self.save_csv(h,m,s,f,bg)
                

    def tick(self):
         #Коррекция времени
        correction_time = self.ui.spinBox.value()
        #Добавляем коррекцию к текущему времени
        my_time = datetime.now() +  timedelta(seconds=correction_time, microseconds=5000)
        #Получаем нужный формт вывода (12 часовой)
        time1 = str(my_time.strftime("%I:%M:%S"))
        #Получаем отдельные значения (часы, минуты и секунды)
        hours = str(my_time.strftime("%I"))
        minutes = str(my_time.strftime("%M"))
        seconds = str(my_time.strftime("%S"))
        self.ui.label_12.setText(time1)

        #Отображаем время на форме в вкладке "Системное время" без учета поправки
        sistem_time = datetime.now()
        time_vew = str(sistem_time.strftime("%I:%M:%S"))
        self.ui.label_6.setText(time_vew)

        #расчитываем смещение часовой стрелки в часе относительно минут
        if int(hours) == 12:
            hours = 0

        if int(hours) > 0:
            my_h = int(hours) * 5
            my_m = (int(minutes) / 12)
            my_hours = round(my_h + my_m)

        if int(hours) == 0:
            #my_h = int(hours) * 5
            my_m = (int(minutes) / 12)
            my_hours = round( my_m)
  
          #если список с путями не пусть 
        if not len(my_patch_list)==0:
            #получаем ссылку на часовую стрелку
            if int(my_hours)  <= 9:
                h_file = f'hour_000{my_hours}.png'
                h = os.path.join(my_patch_list[1],folder_hours,h_file)
            if int(my_hours)  > 9:
                h_file = f'hour_00{my_hours}.png'
                h = os.path.join(my_patch_list[1],folder_hours,h_file)
            #получаем ссылку на минутную стрелку
            m_file = f'minute_00{minutes}.png'
            m = os.path.join(my_patch_list[1],folder_minutes,m_file)
            #получаем ссылку на секундную стрелку
            s_file = f'second_00{seconds}.png'
            s = os.path.join(my_patch_list[1],folder_seconds,s_file)
            f = my_patch_list[2]
            bg = my_patch_list[3]
            #вызываем метод сохранения в файл CSV
            self.save_csv(h,m,s,f,bg)


    #Заполняем comboBox(2-4) данными на основе comboBox
    def fill_comboBox(self):
        try:
            self.ui.comboBox_2.clear()
            self.ui.comboBox_3.clear()
            self.ui.comboBox_4.clear()
            root_patch = os.path.join(os.getcwd(),folder_theme)

            #Стрелки
            arrow = self.ui.comboBox.currentText()
            patch_arrow = os.path.join(root_patch, arrow, folder_color)

            for hours in os.listdir(patch_arrow):
                self.ui.comboBox_2.addItem(hours)

            #Циферблад  
            face = self.ui.comboBox.currentText()
            patch_face = os.path.join(root_patch, face, folder_face)

            for my_face in os.listdir(patch_face):
                if my_face.endswith( '.png'):
                    self.ui.comboBox_3.addItem(my_face)

            #Подложка 
            face = self.ui.comboBox.currentText()
            patch_bg = os.path.join(root_patch, face, folder_bg)

            for my_bg in os.listdir(patch_bg):
                if my_bg.endswith( '.png'):
                    self.ui.comboBox_4.addItem(my_bg)
        except Exception as e:
            print(e)


    def my_patch_list(self):
        index = self.ui.tabWidget.currentIndex() 
        if int(index) == 0:
            self.timer2.stop()
            #self.timer.start(1000)
            #print(index)
        if int(index) == 1:
            self.timer.stop()
            #self.timer2.start(1000)
            #print(index)

        #Выбранная тема из списка comboBox
        theme = self.ui.comboBox.currentText()
        #Выбранная тема из списка comboBox
        arrow = self.ui.comboBox_2.currentText()
        #Выбранный циферблат из списка comboBox
        face = self.ui.comboBox_3.currentText()
        #Выбранный фон из списка comboBox
        bg = self.ui.comboBox_4.currentText() 

        #Путь к папке с темой
        pacth_folder_theme = os.path.join(os.getcwd(), folder_theme, theme)
        #Путь к папке с стрелками
        pacth_arrow = os.path.join(pacth_folder_theme, folder_color, arrow)
        #Путь к папке с циферблатом и сам файл
        pacth_face = os.path.join(pacth_folder_theme, folder_face, face)
        #Путь к папке с фонами и сам файл
        pacth_bg = os.path.join(pacth_folder_theme, folder_bg, bg)

        #Список путей к картинкам         
        my_patch_list.clear()
        my_patch_list.append(pacth_folder_theme)
        my_patch_list.append(pacth_arrow)
        my_patch_list.append(pacth_face)
        my_patch_list.append(pacth_bg)


    #Отображение картинки в окне предварительного просмотра
    def my_images(self):
        try:
            #Выбранная тема из списка comboBox
            theme = self.ui.comboBox.currentText()
            #Выбранная тема из списка comboBox
            arrow = self.ui.comboBox_2.currentText()
            #Выбранный циферблат из списка comboBox
            face = self.ui.comboBox_3.currentText()
            #Выбранный фон из списка comboBox
            bg = self.ui.comboBox_4.currentText() 

            #Путь к папке с темой
            pacth_folder_theme = os.path.join(os.getcwd(), folder_theme, theme)
            #Путь к папке с стрелками
            pacth_arrow = os.path.join(pacth_folder_theme, folder_color, arrow)
            #Путь к папке с циферблатом и сам файл
            pacth_face = os.path.join(pacth_folder_theme, folder_face, face)
            #Путь к папке с фонами и сам файл
            pacth_bg = os.path.join(pacth_folder_theme, folder_bg, bg)

            #Список путей к картинкам         
            #my_patch_list.append((pacth_folder_theme, pacth_arrow, pacth_face, pacth_bg))
            my_patch_list_view.clear()
            my_patch_list_view.append(pacth_folder_theme)
            my_patch_list_view.append(pacth_arrow)
            my_patch_list_view.append(pacth_face)
            my_patch_list_view.append(pacth_bg)

            #создаем ссылки на основе списка my_patch_list_view
            img_h = os.path.join(my_patch_list_view[1],folder_hours) +  r'/hour_0028.png'
            img_m = os.path.join(my_patch_list_view[1],folder_minutes) +  r'/minute_0052.png'
            img_s = os.path.join(my_patch_list_view[1],folder_seconds) +  r'/second_0038.png'
            img_f = os.path.join(my_patch_list_view[2])
            img_bg = os.path.join(my_patch_list_view[3])

            bg = Image.open(img_bg)
            img = Image.open(img_f)
            hour = Image.open(img_h)
            minute = Image.open(img_m)
            second = Image.open(img_s)
            bg.paste(img, (0, 0), img)
            bg.paste(hour, (0, 0), hour)
            bg.paste(minute, (0, 0), minute)
            bg.paste(second, (0, 0), second)

            #Сохраняем
            patch_img_time = my_patch_list_view[0] + img_time
            bg.save(patch_img_time)

            # Отображаем превью темы в label_8
            pixmap = QPixmap(patch_img_time)
            self.ui.label_8.setPixmap(pixmap)
        except Exception as e:
            print(e)

    #диалоговое окно при закрытии
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Сообщение', "Вы действительно хотите выйти?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.timer.stop()
            self.timer2.stop()
            event.accept()
        else:
            event.ignore() 

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()

    #локализация PyQT5 (русский язык)
    locale = QLocale.system().name()
    translator = QTranslator(app)
    translator.load('qtbase_ru.qm')
    app.installTranslator(translator)
    ex = ApplicationWindow()

    application.show()
    sys.exit(app.exec_())
    app.quit() 

if __name__ == "__main__":
    main()
