# -*- coding: utf-8 -*-
import GeneratorConfig as GConfig
import xml.etree.cElementTree as ET
############################################################################################
############################################################################################
Project_path = GConfig.Project_path
TestCases_book_name = GConfig.TestCases_book_name

NeedTestsAndSute = GConfig.NeedTestsAndSute
NeedTemplates = GConfig.NeedTemplates
NeedConfigAndXMnem = GConfig.NeedConfigAndXMnem
NeedSettings = GConfig.NeedSettings
NeedStubs = GConfig.NeedStubs
############################################################################################
############################################################################################
CTT_dir_list = ['Mnemonics\\Xpath', 'Stubs', 'Suits', 'Templates', 'Tests', 'XSD', 'Settings'] # где генерим папку #Sute_Name#
Test_types = ["Positive", "Negative"]
param_element_dictionary = {'TC':'have_corr_table',
                            'isMigrate':'have_isMigrate',
                            'BQ':'have_bq', 
                            'CIF':'have_cif', 
                            'CIF2':'have_cif_crmml',
                            'CFT':'have_cft', 
                            'filial':'filial', 
                            'client_id':'client_id', 
                            'agreement_id':'agreement_id',
                            'SystemId':'SystemId',
                            'partyUid':'partyUid',
                            'only_open':'only_open',
                            'operating_date':'operating_date',
                            'begin_date':'begin_date',
                            'end_date':'end_date',
                            'personId_or_partyUid_for_req':'personId_or_partyUid_for_req',
                            'source_object_type':'source_object_type',
                            'to_branch':'to_branch',
                            'db_error_code':'db_error_code',
                            'db_error_text':'db_error_text',
                            'db_error_type':'db_error_type',
                            'message_error_type':'message_error_type',
                            'tc_error_text':'tc_error_text'} # словарь параметр`ов (значение из excel) : (значение в тесте)
settingsPatternList = [r'№№servNum№№', r'@@servName@@', r'##sysName##']
Templates_dir = 'ProjectTemplates\\'

TC_tmlt_xml_name = Templates_dir + 'TC_template.xml'
TS_tmlt_xml_name = Templates_dir + 'TS_template.xml'
settings_name = Templates_dir + 'settings.xml'
bq_stub_name = 'bq_stub.xml'
cft_stub_name = 'cft_stub.xml'
cif_stub_name = 'cif_stub.xml'
corr_table_stub_name = 'corr_table_stub.xml'
IsMigrate_stub_name = 'IsMigrate_stub.xml'

############################################################################################
############################################################################################
# возвращает имена TC
def TC_NAME(Number, TC_type):
    if(TC_type == 'Negative'):
        return 'TC_N_' + "{0:0=2}".format(Number)
    else:
        return 'TC_' + "{0:0=2}".format(Number)
# создаёт нужные папки если нет
def projectDirGenerator(Prjct_path, dir_list, Svc_Name, T_type):
    import os
    for ctt_dir in dir_list:
        try:
            os.makedirs(Prjct_path + ctt_dir)
        except:
            pass
        try:
            if ctt_dir != 'Settings':
                os.makedirs(Prjct_path + ctt_dir + '\\' + Svc_Name)
        except:
            print("-------Didn't generate all dir:" + Prjct_path + ctt_dir + '\\' + Svc_Name)
        if ctt_dir is 'Tests':
            try:
                os.makedirs(Project_path + "Tests\\" + Svc_Name + '\\' + T_type)
            except:
                pass
        elif ctt_dir is 'Templates':
            try:
                os.makedirs(Prjct_path + "Templates\\" + Svc_Name + '\\' + "Common")
                os.makedirs(Prjct_path + "Templates\\" + Svc_Name + '\\' + T_type + '\\resp_io')
            except:
                pass

# получает строку с параметрами из таблицы и словарь параметров
def getParamList(xl_prm_line, element_dict):
    paramList = []
    for tc_element in xl_prm_line:
        if element_dict.get(tc_element):
            paramList.append(element_dict[tc_element])
    return paramList

# получает id параметра
def GetParamInTabId(prmInTmpl, prmTblList, prmDict):  
    for keyVal in list(prmDict.keys()):
        if prmDict.get(keyVal) == prmInTmpl:
            return prmTblList.index(keyVal)
    return 'Error'

# отступы в XML
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

# Генератор файла тестового сценария
# передать шаблон, куда пишем, zip(список параметров, список значений
def makeTCprms(templatePath, new_templatePath, TC_name, TC_type, description, parameters_tuple):

    tree = ET.parse(templatePath)
    root = tree.getroot()
    root.attrib['name'] = TC_name
    root.attrib['description'] = description
    root.text = '\n\n'
    
    new_element = ET.Element('CreateMap')
    new_element.set('variable', "MapOfParams")
    root.append(new_element)
    new_element.tail = '\n\n'
    
    new_element = ET.Element('AddValueToMap')
    new_element.set('key', "test_case")
    new_element.set('map', 'MapOfParams')
    new_element.set('value', TC_name)
    root.append(new_element)
    
    new_element = ET.Element('AddValueToMap')
    new_element.set('key', 'tc_type')
    new_element.set('map', 'MapOfParams')
    new_element.set('value', TC_type)
    root.append(new_element)
    
    
    for prmName, value in parameters_tuple: 
        new_element = ET.Element('AddValueToMap')
        new_element.set('key', prmName)
        new_element.set('map', 'MapOfParams')
        new_element.set('value', value)
        root.append(new_element)
    new_element.tail = '\n\n'
    RunTest_element = ET.Element('RunTest')
    RunTest_element.set('workpath', "Tests\Functions\Main")
    inputParams_element = ET.SubElement(RunTest_element, 'inputParams')
    variable_element = ET.SubElement(inputParams_element, 'variable')
    variable_element.set('name',"MapOfParams")
    RunTest_element.tail = '\r\n'
    root.append(RunTest_element)
    indent(root)
    tree.write(new_templatePath, 'utf-8', True)
    
    # make pritty
    with open(new_templatePath, 'r') as f:
        text = f.read()
    with open(new_templatePath, 'w') as file:
        for line in text.splitlines():
            line += '\n'
            if line == '  <CreateMap variable="MapOfParams" />\n':
                file.write('\n  <CreateMap variable="MapOfParams" />\n\n')
            elif line == '  <RunTest workpath="Tests\Functions\Main">\n':
                file.write('\n  <RunTest workpath="Tests\Functions\Main">\n')
            elif line == '  </RunTest>\n':
                file.write('  </RunTest>\n\n')
            else:
                file.write(line)


# Заменяем значения в файле глобальных настроек
def changeWrighteSettings(sgPath, newSettings, patternDictionary):
    oldSettings = open(sgPath, mode="r", encoding='utf-8', newline='')
    nwSgs = open(newSettings, mode="w", encoding='utf-8', newline='')
    for line in oldSettings:
        s=line
        for oldVal, newVal in patternDictionary.items():
            s = s.replace(oldVal, newVal)
        nwSgs.write(s)
    oldSettings.close()
    nwSgs.close()
