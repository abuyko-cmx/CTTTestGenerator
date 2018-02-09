# -*- coding: utf-8 -*-
import GeneratorConfig as GConfig

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
                            'onlyOpen':'only_open',
                            'SystemId':'SystemId',
                            'operating_date':'operating_date',
                            'agreement_id':'agreement_id',
                            'Сервис':'source_object_type',
                            'db_error_code':'db_error_code',
                            'db_error_text':'db_error_text',
                            'message_error_type':'message_error_type',
                            'tc_error_text':'tc_error_text'} # словарь параметров (значение из excel) : (значение в тесте)

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

def GetParamInTabId(prmInTmpl, prmTblList, prmDict):  
    for keyVal in list(prmDict.keys()):
        if prmDict.get(keyVal) == prmInTmpl:
            return prmTblList.index(keyVal)
    return 'Error'