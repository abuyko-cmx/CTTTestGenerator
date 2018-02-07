# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xlrd, xlwt
import shutil
import os
import GeneratorConfig as GC
import time

__author__ = "Alex_Buy"
############################
##### download config ######
############################


Project_path = GC.Project_path
CTT_dir_list = GC.CTT_dir_list
#Test_type = GC.Test_types[0]
# param_element_list = GC.param_element_list
TestCases_book_path = GC.TestCases_book_name
TC_tmlt_xml_path = GC.TC_tmlt_xml_name
TS_tmlt_xml_path = GC.TS_tmlt_xml_name
settings_path = GC.settings_name
stub_path_list = [GC.bq_stub_name, GC.cft_stub_name, GC.cif_stub_name, GC.corr_table_stub_name, GC.IsMigrate_stub_name]
param_element_dict = GC.param_element_dictionary
# -------------------------------------
NeedTestsAndSute = GC.NeedTestsAndSute
NeedTemplates = GC.NeedTemplates
NeedConfigAndXMnem = GC.NeedConfigAndXMnem
NeedSettings = GC.NeedSettings
NeedStubs = GC.NeedStubs
# -------------------------------------
try:#открываем файлы
    TestCases_book = xlrd.open_workbook(TestCases_book_path)
except:
    print('-------Open file error!')
# Загружаем глобальные данные
sheet_1 = TestCases_book.sheet_by_name(GC.Test_types[0])
TC_vals = [sheet_1.row_values(rownum) for rownum in range(sheet_1.nrows)] #получаем список значений из всех записей
ServiceNumber = TC_vals[0][0] # номер сервиса.
ServiceName = TC_vals[0][1] # имя сервиса
SystemName = TC_vals[0][2] # имя системы (BPM/APP/CRM)


for Test_type in GC.Test_types: # Positive + Negative
    
    try:#открываем файлы
        TC_tmlt_xml = open(TC_tmlt_xml_path, "r")
        TS_tmlt_xml = open(TS_tmlt_xml_path, "r")
    except:
        print('-------Open file error!')
    # Загружаем данные
    sheet = TestCases_book.sheet_by_name(Test_type)
    TC_vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] #получаем список значений из всех записей
    TC_template = ET.parse(TC_tmlt_xml)
    Test = TC_template.getroot()
    TS_template = ET.parse(TS_tmlt_xml)
    Sute = TS_template.getroot()
    print("---------------------------------------------------")
    print(Project_path, CTT_dir_list, ServiceName, Test_type)
    GC.projectDirGenerator(Project_path, CTT_dir_list, ServiceName, Test_type)
    param_element_list = 0
    param_element_list = GC.getParamList(TC_vals[1], param_element_dict)
    print(Test_type)
    print(param_element_list)
    #####################################################
    # Создать файлы тестов построчно
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0])) # TODO переделать под "№"

        Test.attrib['name'] = TC_name
        Test.attrib['description'] = str(tc_element[1])# TODO переделать под словарь

        for attr in Test.iter('AddValueToMap'):
            if(attr.get('key') == 'test_case'):
                attr.set('value', TC_name)
            if(attr.get('key') == 'tc_type'):
                attr.set('value', Test_type)
            for paramType in param_element_list:
                if(attr.get('key') == paramType):
                    try:
                        attr.set('value', str(tc_element[GC.GetParamInTabId(attr.get('key'), TC_vals[1], param_element_dict)])) # поправить срочно!
                    except:
                        pass

        try:
            os.makedirs(Project_path + "Tests\\" + ServiceName + '\\' + Test_type)
        except:
            pass
        try:
            os.makedirs(Project_path + "Tests\\" + ServiceName + '\\' + Test_type + '\\' + TC_name)
        except:
            print("-------Didn't generate dir:" + Test_type)
        TC_template.write(Project_path + "Tests\\" + ServiceName + '\\' + Test_type + '\\' + TC_name + '\\settings.xml', 'utf-8', True)
    #####################################################
    # Добавить генерацию Sute
    TC_workpath = 0
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]))# TODO переделать под "№"
        Sute.attrib['name'] = Test_type
        Sute.attrib['description'] = ServiceName
        TC_element = ET.Element('TestCase')
        TC_element.set('name', TC_name)
        TC_element.set('description', tc_element[1])# TODO переделать под словарь
        TC_workpath = ET.SubElement(TC_element, 'workpath')
        TC_workpath.text = '/Tests/' + ServiceName + '/' + Test_type + '/' + TC_name
        Sute.append(TC_element)
        try:
            os.makedirs(Project_path + 'Suits\\' + ServiceName)
        except:
            print("-------Didn't generate dir:" + Test_type)
        TS_template.write(Project_path + 'Suits\\' + ServiceName + '\\' + Test_type + '.xml', 'utf-8', True)
    print("++@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",ServiceName)
    TC_tmlt_xml.close()
    TS_tmlt_xml.close()
#####################################################
Test_type = GC.Test_types[0]
#####################################################
# Добавить генерацию Templates
print("&&&&&&&&&&&&&&&&&&&&&&&", ServiceName)
try:
    #os.makedirs(Project_path + "Templates\\" + ServiceName + '\\' + Test_type)
    os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Positive\\resp_io')
    os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Common')
except:
    print("--------Didn't generate Template dir's!")
for tc_element in TC_vals[2:]:
    TC_name = GC.TC_NAME(int(tc_element[0]))
    Empty_element = ET.Element(ServiceName + 'Resp')
    Empty_tree = ET.ElementTree(Empty_element)
    Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\' + Test_type + '\\resp_io'+ '\\'+ TC_name + '.xml', 'utf-8', True)
#####################################################
# Добавить генерацию config и XMnemonics

Empty_element = ET.Element('config')
Empty_tree = ET.ElementTree(Empty_element)
Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\Common\\config.xml', 'utf-8', True)
open(Project_path + 'Mnemonics\\Xpath\\' + ServiceName + '\\XMnemonics', 'tw', encoding='utf-8').write("filial = //*[local-name()='FilialId']/*[local-name()='ObjectId']")
#####################################################
# Добавить settings
shutil.copy(settings_path, Project_path + 'Settings\\' + ServiceName + '.xml')
#####################################################
# Добавить stubs 

for stub_name in stub_path_list:
    shutil.copy(GC.Templates_dir + stub_name, Project_path + 'Stubs\\' + ServiceName + '\\' + stub_name)


#time.sleep(3)