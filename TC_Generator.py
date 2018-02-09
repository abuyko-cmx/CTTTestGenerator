# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xlrd
import shutil
import os
import GeneratorCore as GC
import time

__author__ = "Alex_Buy"

############################
##### download config ######
############################


Project_path = GC.Project_path
CTT_dir_list = GC.CTT_dir_list

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
sheet_1 = TestCases_book.sheet_by_name('Positive')
TC_vals_positive = [sheet_1.row_values(rownum) for rownum in range(sheet_1.nrows)] #получаем список значений из всех записей
ServiceNumber = str(int(TC_vals_positive[0][0])) # номер сервиса.
ServiceName = TC_vals_positive[0][1] # имя сервиса
SystemName = TC_vals_positive[0][2] # имя системы (BPM/APP/CRM)


for Test_type in GC.Test_types: # Positive + Negative
    
    try:#открываем файлы
        TC_tmlt_xml = open(TC_tmlt_xml_path, "r")
        TS_tmlt_xml = open(TS_tmlt_xml_path, "r")
    except:
        print('-------Open file error!')
    # Загружаем данные
    sheet = TestCases_book.sheet_by_name(Test_type)
    TC_vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] # получаем список значений из всех записей
    TC_template = ET.parse(TC_tmlt_xml)
    Test = TC_template.getroot()
    TS_template = ET.parse(TS_tmlt_xml)
    Sute = TS_template.getroot()
    print("---------------------------------------------------", Test_type)
    GC.projectDirGenerator(Project_path, CTT_dir_list, ServiceName, Test_type)
    param_element_list = 0
    param_element_list = GC.getParamList(TC_vals[1], param_element_dict)

    #####################################################
    # Создать файлы тестов построчно
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]),Test_type) 
        description = str(tc_element[1])
        TC_xml_path = Project_path + "Tests\\" + ServiceName + '\\' + Test_type + '\\' + TC_name
        value_list = [str(tc_element[GC.GetParamInTabId(prm, TC_vals[1], param_element_dict)]) for prm in param_element_list]
     
        parameters = zip(param_element_list, value_list)
        
        try:
            os.makedirs(TC_xml_path)
            GC.makeTCprms(TC_tmlt_xml_path, TC_xml_path + '\\settings.xml', TC_name, Test_type, description, parameters)
        except:
            print("-------Didn't generate dir:" + Test_type)
        


    #####################################################
    # Генерация Sute
    TC_workpath = 0
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]), Test_type)
        Sute.attrib['name'] = Test_type
        Sute.attrib['description'] = ServiceName
        Sute.attrib['globalSettingsFile'] = 'Settings/' + ServiceName + '.xml'
        TC_element = ET.Element('TestCase')
        TC_element.set('name', TC_name)
        TC_element.set('description', tc_element[1])
        TC_workpath = ET.SubElement(TC_element, 'workpath')
        TC_workpath.text = '/Tests/' + ServiceName + '/' + Test_type + '/' + TC_name
        Sute.append(TC_element)
        try:
            os.makedirs(Project_path + 'Suits\\' + ServiceName)
        except:
            print("-------Didn't generate dir:" + Test_type)
        GC.indent(Sute)
        TS_template.write(Project_path + 'Suits\\' + ServiceName + '\\' + Test_type + '.xml', 'utf-8', True)
    print("ServiceName============================= ",ServiceName)
    TC_tmlt_xml.close()
    TS_tmlt_xml.close()
#####################################################
#####################################################
# Добавить генерацию Templates
if NeedTemplates:
    try:
        os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Positive\\resp_io')
        os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Common')
    except:
        print("--------Didn't generate Template dir's!")
    for tc_element in TC_vals_positive[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]), 'Positive')
        Empty_element = ET.Element(ServiceName + 'Resp')
        Empty_tree = ET.ElementTree(Empty_element)
        Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\Positive\\resp_io'+ '\\'+ TC_name + '.xml', 'utf-8', True)
#####################################################
# Добавить файлы config и XMnemonics
if NeedConfigAndXMnem:
    Empty_element = ET.Element('config')
    Empty_tree = ET.ElementTree(Empty_element)
    Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\Common\\config.xml', 'utf-8', True)
    open(Project_path + 'Mnemonics\\Xpath\\' + ServiceName + '\\XMnemonics', 'tw', encoding='utf-8').write("filial = //*[local-name()='FilialId']/*[local-name()='ObjectId']")
#####################################################
# Добавить settings
if NeedSettings:
    new_settings = Project_path + 'Settings\\' + ServiceName + '.xml'
     #TODO сделать склейку двух словарей
    prmList  = [ServiceNumber, ServiceName, SystemName]
    prmToChange = dict(zip(GC.settingsPatternList, prmList))
    print(prmToChange)
    GC.changeWrighteSettings(settings_path, new_settings, prmToChange)
#####################################################
# Добавить stubs 
if NeedStubs: 
    for stub_name in stub_path_list:
        shutil.copy(GC.Templates_dir + stub_name, Project_path + 'Stubs\\' + ServiceName + '\\' + stub_name)


time.sleep(3)