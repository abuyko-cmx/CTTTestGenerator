# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xlrd
import shutil
import os
import GeneratorCore as GC
import time

__author__ = "Alex_Buy"

################################################
############### download config ################
################################################

print('--------=========----------')
print("Можете 2 раза нажать 'Enter' если хотите использовать данные из конфига.")
Project_path = input("Введите путь до проекта(используйте '/'):\n") 
TestCases_book_path = input("Введите путь до тест кейсов(используйте '/'):\n") 

if Project_path == "":
    Project_path = GC.Project_path
if TestCases_book_path == "":
    TestCases_book_path = GC.TestCases_book_name

CTT_dir_list = GC.CTT_dir_list
TC_tmlt_xml_path = GC.TC_tmlt_xml_name
TS_tmlt_xml_path = GC.TS_tmlt_xml_name
settings_path = GC.settings_name
stub_path_list = GC.stub_path_list
param_element_dict = GC.param_element_dictionary
# -------------------------------------
NeedTestsAndSute = GC.NeedTestsAndSute
NeedTemplates = GC.NeedTemplates
NeedConfigAndXMnem = GC.NeedConfigAndXMnem
NeedSettings = GC.NeedSettings
NeedStubs = GC.NeedStubs
NeedXSD = GC.NeedXSD
# -------------------------------------
#открываем файлы
try:
    TestCases_book = xlrd.open_workbook(TestCases_book_path)
except:
    print('-------Open file error!Can not open ', TestCases_book_path)
# Загружаем глобальные данные
sheet_1 = TestCases_book.sheet_by_name('Positive')
TC_vals_positive = [sheet_1.row_values(rownum) for rownum in range(sheet_1.nrows)] #получаем список значений из всех записей
#ServiceNumber = str(int(TC_vals_positive[0][0])) # номер сервиса.
ServiceNumber = str(TC_vals_positive[0][0]) # номер сервиса.
ServiceName = TC_vals_positive[0][1] # имя сервиса
ServiceNumberName = ServiceNumber + '_' + ServiceName
SystemName = TC_vals_positive[0][2] # имя системы (BPM/APP/CRM)
################################################
################################################
#############Let's Generate Tests###############
################################################
for Test_type in GC.Test_types: # Positive + Negative
    
    try:#открываем файлы
        TC_tmlt_xml = open(TC_tmlt_xml_path, "r")
        TS_tmlt_xml = open(TS_tmlt_xml_path, "r")
    except:
        print('-------Open file error! Can not open ', TC_tmlt_xml_path)
    # Загружаем данные
    sheet = TestCases_book.sheet_by_name(Test_type)
    TC_vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] # получаем список значений из всех записей
    TC_template = ET.parse(TC_tmlt_xml)
    Test = TC_template.getroot()
    TS_template = ET.parse(TS_tmlt_xml)
    Sute = TS_template.getroot()
    print("-------------------------{0}--------------------------".format(Test_type))
    GC.projectDirGenerator(Project_path, CTT_dir_list, ServiceNumberName, Test_type)
    param_element_list = 0
    param_element_list = GC.getParamList(TC_vals[1], param_element_dict)

    #####################################################
    # Создать файлы тестов построчно
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]),Test_type) 
        description = str(tc_element[1])
        TC_xml_path = Project_path + "Tests\\" + ServiceNumberName + '\\' + Test_type + '\\' + TC_name
        value_list = [str(tc_element[GC.GetParamInTabId(prm, TC_vals[1], param_element_dict)]) for prm in param_element_list]
     
        parameters = zip(param_element_list, value_list)
        
        try:
            os.makedirs(TC_xml_path)
            GC.makeTCprms(TC_tmlt_xml_path, TC_xml_path + '\\settings.xml', TC_name, Test_type, description, parameters)
            print("--Generated: ", TC_name)
        except:
            #print("-------Didn't generate dir:" + Test_type)
            pass
        


    #####################################################
    # Генерация Sute
    TC_workpath = 0
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]), Test_type)
        Sute.attrib['name'] = ServiceNumberName + '_' + Test_type
        Sute.attrib['description'] = ServiceName
        Sute.attrib['globalSettingsFile'] = 'Settings/' + 'GlobalSettings.xml'
        TC_element = ET.Element('TestCase')
        TC_element.set('name', TC_name)
        TC_element.set('description', tc_element[1])
        TC_workpath = ET.SubElement(TC_element, 'workpath')
        TC_workpath.text = '/Tests/' + ServiceNumberName + '/' + Test_type + '/' + TC_name
        Sute.append(TC_element)
        try:
            os.makedirs(Project_path + 'Suits\\' + ServiceNumberName)
        except:
            #print("-------Didn't generate dir:" + Test_type)
            pass
        GC.indent(Sute)
        TS_template.write(Project_path + 'Suits\\' + ServiceNumberName + '\\' + Test_type + '.xml', 'utf-8', True)
    print("Generated Sute============================= ", Test_type)
    TC_tmlt_xml.close()
    TS_tmlt_xml.close()
#####################################################
#####################################################
# Добавить генерацию Templates
if NeedTemplates:
    try:
        os.makedirs(Project_path + "Templates\\" + ServiceNumberName + '\\Positive\\resp_io')
        os.makedirs(Project_path + "Templates\\" + ServiceNumberName + '\\Common')
    except:
        print("--------Templates dir-s loading...")
    for tc_element in TC_vals_positive[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]), 'Positive')
        Empty_element = ET.Element(ServiceName + 'Resp')
        Empty_tree = ET.ElementTree(Empty_element)
        Empty_tree.write(Project_path + 'Templates\\' + ServiceNumberName + '\\Positive\\resp_io'+ '\\'+ TC_name + '.xml', 'utf-8', True)
    print("--------Generated empty Templates.")
#####################################################
# Добавить файлы config и XMnemonics
if NeedConfigAndXMnem: 
    try:
        Config_path = GC.Project_root + 'src\\' + ServiceName + '\\resources\\settings\\' 
        for conf in os.listdir(Config_path):
            if 'settings' in conf.lower() or 'config' in conf.lower():
                Config_name = Config_path + conf


        shutil.copy(Config_name, Project_path + 'Templates\\' + ServiceNumberName + '\\Common\\config.xml')
        print("++++++++++Generated FULL CONFIG!!!.")
    except:
        Empty_element = ET.Element('config')
        Empty_tree = ET.ElementTree(Empty_element)
        Empty_tree.write(Project_path + 'Templates\\' + ServiceNumberName + '\\Common\\config.xml', 'utf-8', True)
        print("--------Generate empty Config.")
    
    open(Project_path + 'Mnemonics\\Xpath\\' + ServiceNumberName + '\\XMnemonics', 'tw', encoding='utf-8').write("filial = //*[local-name()='FilialId']/*[local-name()='ObjectId']")
    print("--------Generated empty XPath.")
#####################################################
# Добавить settings
if NeedSettings:
    new_settings = Project_path + 'Settings\\' + ServiceNumberName + '.xml'

    prmList  = [ServiceNumber, ServiceName, SystemName]
    prmToChange = dict(zip(GC.settingsPatternList, prmList))
    print(prmToChange)
    GC.changeWrighteSettings(settings_path, new_settings, prmToChange)
    print("--------Generated raw Settings.")
#####################################################
# Добавить stubs 
if NeedStubs: 
    for stub_name in stub_path_list:
        shutil.copy(GC.Templates_dir + stub_name, Project_path + 'Stubs\\' + ServiceNumberName + '\\' + stub_name)
    print("--------Added all Stubs.")

if NeedXSD: 
    print("--------Didn't find XSD.")
time.sleep(3)