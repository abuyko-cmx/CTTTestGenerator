# CTTTestGenerator
# Vresion 0.2.3
CTTTestGenerator


- В GeneratorConfig прописать:
	- путь к проекту
	- путь до файла с тест-кейсам (пока работает с форматом .xls). Пример в папке Templates.

	

Запустить Generate.bat
Создаются шаблоны тестов.


================================================================================================
В РУЧНУЮ:
- Изменить файл настроек
	-очереди
	-имя сервиса
	-source_system

- Добавить необходимые мнемоники (xpath)
- собрать и добавить файлы xsd
- изменить config файл (Tests/*/Common/config.xml)
- заполнить файлы resp_io
- изменить условия заглушки согласно логике тестов
-----------------------------------------------------------------------------------------------
///////////////////////////////////////////////////////////////////////////////////////////////
-----------------------------------------------------------------------------------------------
тесты готовы!