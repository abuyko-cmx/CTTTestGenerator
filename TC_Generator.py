# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import xlrd
import shutil
import os
import GeneratorCore as GC
import time

__author__ = "Alex_Buy"

from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='t')
    
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

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
try:#îòêðûâàåì ôàéëû
    TestCases_book = xlrd.open_workbook(TestCases_book_path)
except:
    print('-------Open file error!')
# Çàãðóæàåì ãëîáàëüíûå äàííûå
sheet_1 = TestCases_book.sheet_by_name('Positive')
TC_vals_positive = [sheet_1.row_values(rownum) for rownum in range(sheet_1.nrows)] #ïîëó÷àåì ñïèñîê çíà÷åíèé èç âñåõ çàïèñåé
ServiceNumber = TC_vals_positive[0][0] # íîìåð ñåðâèñà.
ServiceName = TC_vals_positive[0][1] # èìÿ ñåðâèñà
SystemName = TC_vals_positive[0][2] # èìÿ ñèñòåìû (BPM/APP/CRM)


for Test_type in GC.Test_types: # Positive + Negative
    
    try:#îòêðûâàåì ôàéëû
        TC_tmlt_xml = open(TC_tmlt_xml_path, "r")
        TS_tmlt_xml = open(TS_tmlt_xml_path, "r")
    except:
        print('-------Open file error!')
    # Çàãðóæàåì äàííûå
    sheet = TestCases_book.sheet_by_name(Test_type)
    TC_vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] #ïîëó÷àåì ñïèñîê çíà÷åíèé èç âñåõ çàïèñåé
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
    # Ñîçäàòü ôàéëû òåñòîâ ïîñòðî÷íî
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]),Test_type) # TODO ïåðåäåëàòü ïîä "¹"

        Test.attrib['name'] = TC_name
        Test.attrib['description'] = str(tc_element[1])# TODO ïåðåäåëàòü ïîä ñëîâàðü

        for attr in Test.iter('AddValueToMap'):
            if(attr.get('key') == 'test_case'):
                attr.set('value', TC_name)
            if(attr.get('key') == 'tc_type'):
                attr.set('value', Test_type)
            for paramType in param_element_list:
                if(attr.get('key') == paramType):
                    try:
                        attr.set('value', str(tc_element[GC.GetParamInTabId(attr.get('key'), TC_vals[1], param_element_dict)])) # ïîïðàâèòü ñðî÷íî!
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
    # Äîáàâèòü ãåíåðàöèþ Sute
    TC_workpath = 0
    for tc_element in TC_vals[2:]:
        TC_name = GC.TC_NAME(int(tc_element[0]), Test_type)# TODO ïåðåäåëàòü ïîä "¹"
        Sute.attrib['name'] = Test_type
        Sute.attrib['description'] = ServiceName
        TC_element = ET.Element('TestCase')
        TC_element.set('name', TC_name)
        TC_element.set('description', tc_element[1])# TODO ïåðåäåëàòü ïîä ñëîâàðü
        TC_workpath = ET.SubElement(TC_element, 'workpath')
        TC_workpath.text = '/Tests/' + ServiceName + '/' + Test_type + '/' + TC_name
        Sute.append(TC_element)
        try:
            os.makedirs(Project_path + 'Suits\\' + ServiceName)
        except:
            print("-------Didn't generate dir:" + Test_type)
        indent(Sute)
        TS_template.write(Project_path + 'Suits\\' + ServiceName + '\\' + Test_type + '.xml', 'utf-8', True)
    print("++@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",ServiceName)
    TC_tmlt_xml.close()
    TS_tmlt_xml.close()
#####################################################
Test_type = GC.Test_types[0]
#####################################################
# Äîáàâèòü ãåíåðàöèþ Templates
print("&&&&&&&&&&&&&&&&&&&&&&&", ServiceName)
try:
    os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Positive\\resp_io')
    os.makedirs(Project_path + "Templates\\" + ServiceName + '\\Common')
except:
    print("--------Didn't generate Template dir's!")
for tc_element in TC_vals_positive[2:]:
    TC_name = GC.TC_NAME(int(tc_element[0]), 'Positive')
    Empty_element = ET.Element(ServiceName + 'Resp')
    Empty_tree = ET.ElementTree(Empty_element)
    Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\' + Test_type + '\\resp_io'+ '\\'+ TC_name + '.xml', 'utf-8', True)
#####################################################
# Äîáàâèòü ãåíåðàöèþ config è XMnemonics

Empty_element = ET.Element('config')
Empty_tree = ET.ElementTree(Empty_element)
Empty_tree.write(Project_path + 'Templates\\' + ServiceName + '\\Common\\config.xml', 'utf-8', True)
open(Project_path + 'Mnemonics\\Xpath\\' + ServiceName + '\\XMnemonics', 'tw', encoding='utf-8').write("filial = //*[local-name()='FilialId']/*[local-name()='ObjectId']")
#####################################################
# Äîáàâèòü settings
shutil.copy(settings_path, Project_path + 'Settings\\' + ServiceName + '.xml')
#####################################################
# Äîáàâèòü stubs 

for stub_name in stub_path_list:
    shutil.copy(GC.Templates_dir + stub_name, Project_path + 'Stubs\\' + ServiceName + '\\' + stub_name)


time.sleep(3)