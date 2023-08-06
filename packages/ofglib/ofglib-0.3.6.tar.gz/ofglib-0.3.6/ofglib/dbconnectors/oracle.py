from datetime import datetime
import pandas as pd
import cx_Oracle as cx


alias = {
        # HAVING :
        "СХЕМА_ПРОК":"max(rpm.ROLLINGPROGRAM)",
        "ДУО_ХОЛОСТ": "sum(decode(substr(rpm.STAFF,1,1),'Q',0,decode(rpm.PASSTYPE,'Idle',1)))",
        "ГИДРОСБИВ": "sum(decode(rpm.DESCALINGS1,'ON',1))",
        "ДУО_Т_3_ПР": "max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.LSTEMP)))",
        "ДУО_Т_ПОСЛ": """decode( sum(decode(substr(rpm.STAFF,1,1),'Q',0,decode(rpm.PASSTYPE,'Idle',1))),1,
        max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,-1,1),'T',rpm.FSTEMP))),
        max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,-1,1),'T',rpm.LSTEMP))))""",
        "КВР_Т_1_ПР": "max(decode(rpm.STAFF,'Q1',rpm.FSTEMP))",
        "s2_start": "max(rpm.S2START)",
        "ВМЕШ_ТЕМП": "max(rpm.PLATETEMPBIAS)",
        "ПЕЧЬ_ДУО": "max(decode(substr(rpm.STAFF,1,2),'H1',rpm.FORCESTART,'L1',rpm.FORCESTART))",
        "ДУО_ВРЕМЯ": """max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,2,1),'N',rpm.FORCEEND))) - max(decode(substr(rpm.STAFF,1,2),'H1',rpm.FORCESTART,'L1',rpm.FORCESTART))""",
        "ДУО_КВР": """max(decode(substr(rpm.STAFF,1,2),'Q1',rpm.FORCESTART)) - max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,2,1),'N',rpm.FORCEEND)))""",
        "КВР_ВРЕМЯ": "max(decode(rpm.STAFF,'QN',rpm.FORCEEND,'QNT',rpm.FORCEEND))- max(decode(substr(rpm.STAFF,1,2),'Q1',rpm.FORCESTART))",
        "УКО_ВРЕМЯ": "round(86400*(rrc.COL_STP_DAT-rrc.COL_STA_DAT),5)",

        # категориальные:
        'МАРКА': 'rpo.STEEL_GRADE',
        #'ПЛАВКА': 'rpo.HEAT',
        'ТЕХТРЕБ': 'rpo.STD_REQUIREMENTS',
        'К_МАРКИ': 'rpo.STEEL_CODE',
        'ПЕЧЬ_РЯД': 'rpms.FURNACE',
        'УМО': 'rpms.INTERCELL_COOLING',
        'УКО_СТРАТ': 'rtl.COOLING_STRATEGY',
        #'КОД_ОШИБКИ': 'rpms.VIOLATION_CODE',
        #'КОД_ЦЛК': 'rpms.TEXT_VIOLATION',
        "ТИПТЕХЭСПЦ": "decode(nvl(rpo.EAF_TECHNOLOGY_CODE,0), 1, 'ДСП', 2, 'ГМП')",
        "ПР_УВС": "decode(rpo.DEGASSING, 'Y', 'УВС')",
        #"СТОППИР":  "decode(rpo.ASSIGN_STOWING, 'Y', 1, 'N', 0)",

        # численные
        "H_СЛЯБ": "rpo.SLAB_THICKNESS",
        "B_СЛЯБ": "rpo.SLAB_WIDTH",
        "L_СЛЯБ": "rpo.SLAB_LENGTH",
        "ВЕС_СЛ": "rpo.SLAB_WEIGHT_COUNT/1000",
        "ВЕСФ_СЛ": "rpms.SLAB_WEIGHT/1000",
        "H_ЛИСТ": "rpo.THICKNESS",
        "B_ЛИСТ": "rpo.WIDTH",
        "L_ЛИСТ": "rpo.LENGTH",
        "ДЛИТ_ПЕЧЬ": "rpms.FURNACE_HEAT_DURATION",
        'КРАТ': "rpo.CUT_AMOUNT",
        'ФК_Т_ПЕЧЬ': "rpms.FURNACE_HEAT_TEMPERATURE",
        "ДУО_ПРОХ": "rpms.DUO_PASS_AMOUNT",
        "ПОДКАТ": "rpms.SHEET_ROLL",
        "КВР_Т_ПЛАН": "rtl.QUARTO_TEMPERATURE_OUT",
        "КВР_Т_ПОСЛ": "rpms.QUARTO_TEMPERATURE",
        "КВР_ПРОХ": "rpms.QUARTO_PASS_AMOUNT",
        "УКО_Т_ПЛАН": "rtl.COOLING_TEMPERATURE_OUT",
        "УКО_И_ПЛАН": "rtl.COOLING_INTENSITY",
        "УКО_Т_НАЧ": "rrc.COL_TMP_STA_TCK_MEA",
        "УКО_Т_КОН": "rrc.TMP_COL_STP_CAL",
        "УКО_ИНТ": "rrc.COL_RAT_AVG_CAL_ACC",
        "УКО_СКОР": "rrc.ADP_SPD",
        "УГЛ_ЭКВ": "rhc.CEV",
        "КХС": "rhc.CHEM_COMPOS_COEFF",
        "c": "rhc.ELEMENT_C",
        "si": "rhc.ELEMENT_SI",
        "mn": "rhc.ELEMENT_MN",
        "p": "rhc.ELEMENT_P",
        "s": "rhc.ELEMENT_S",
        "cr": "rhc.ELEMENT_CR",
        "ni": "rhc.ELEMENT_NI",
        "cu": "rhc.ELEMENT_CU",
        "ti": "rhc.ELEMENT_TI",
        "al": "rhc.ELEMENT_AL",
        "n2": "rhc.ELEMENT_N",
        "nb": "rhc.ELEMENT_NB",
        "v": "rhc.ELEMENT_V",
        "b": "rhc.ELEMENT_B",
        "mo": "rhc.ELEMENT_MO",

        # add temperatures
}


def create_where(equality_constraints, interval_constraints):
    res = []
    for name in equality_constraints:
        values = equality_constraints[name]
        tmp = [(name, value) for value in values]
        ans = ' or '.join([f"{name}='{value}'" if value else f"{name} is NULL" for name, value in tmp])
        res.append(f"({ans})")

    equality_constraints = ' and '.join(res)

    res = []
    for name in interval_constraints:
        values = interval_constraints[name]
        tmp = [(name, value1, value2) for value1, value2 in values]
        print(tmp)
        ans = ' or '.join([f"{name} between {value1} and {value2}" if value1 and value2 else
                            f"{name} >= {value1}" if value1 else
                            f"{name} <= {value2}" for name, value1, value2 in tmp])
        res.append(f"({ans})")

    interval_constraints = ' and '.join(res)

    if equality_constraints or interval_constraints:
        if equality_constraints and interval_constraints:
            return f"{equality_constraints} and {interval_constraints}"
        else:
            if equality_constraints:
                return f"{equality_constraints}"
            else:
                return f"{interval_constraints}"
    else:
        return ""


def query_init(start_date, features=True, targets=True, filters=None):
    # for key in alias:
    #     filters = filters.replace(key, alias[key])
    # filters = f"where {filters}" if filters else ""
    filters = f" {filters} and" if filters else ""

    count = "*"
    if not features and not targets:
        features = True
        targets = True
        count = "COUNT(*) NUM"

    features = "" if features else "--"
    targets = "" if targets else "--"

    print(f"features: <{features}>")
    print(f"targets: <{targets}>")
    print(f"filters: <{filters}>")

    return f'''
        select {count} from
        (select
        {targets}rtmr.PROTOCOL_DT ДАТА_ВВОД,
        --{features}rpms.DT_INS ДАТА_ВВОД,
        rpms.SLAB_ID ИД_СЛЯБА,
        max(rpm.DISCHARGE) НАЧ_ПРОКАТ,
        max(rpm.COMPLETION) КОН_ПРОКАТ,
        {features}decode(rpo.HOT_PUT, 'Y', 'HOT') ПР_ГП,
        {features}rpo.ORDER_POSITION ПОЗИЦИЯ,
        {features}rpo.HEAT ПЛАВКА,
        {features}decode(nvl(rpo.EAF_TECHNOLOGY_CODE,0), 1, 'ДСП', 2, 'ГМП') ТИПТЕХЭСПЦ,
        {features}decode(rpo.DEGASSING, 'Y', 'УВС') ПР_УВС,
        {features}rpo.ROLLED_LOT_ID ПАРТИЯ,
        {features}--to_char(rpo.SHEET_NUM)||'-'||to_char(rpo.SHEET_NUM + rpo.SHEET_AMOUNT -1) ДИАП_ПАРТ,
        {features}rpms.SLAB_NUM N_СЛЯБ,
        {features}--to_char(rpms.SHEET_NUM_1)||'-'||to_char(rpms.SHEET_NUM_1+rpo.CUT_AMOUNT-1) ДИАП_СЛЯБ,
        {features}rpo.STEEL_GRADE МАРКА,
        {features}rpo.STD_REQUIREMENTS ТЕХТРЕБ, --иной формат, чем в скинутых ими даннных
        {features}rpo.STEEL_CODE К_МАРКИ,
        {features}rpo.SLAB_THICKNESS H_СЛЯБ,
        {features}rpo.SLAB_WIDTH B_СЛЯБ,
        {features}rpo.SLAB_LENGTH L_СЛЯБ,
        {features}rpo.SLAB_WEIGHT_COUNT/1000 ВЕС_СЛ,
        {features}rpms.SLAB_WEIGHT/1000 ВЕСФ_СЛ,
        {features}rpo.THICKNESS H_ЛИСТ,
        {features}rpo.WIDTH B_ЛИСТ,
        {features}rpo.LENGTH L_ЛИСТ,
        {features}rpo.CUT_AMOUNT КРАТ,
        {features}rpms.LENGTH_PART_1 Д_Н_1_ДЛ,
        {features}rpms.LENGTH_PART_2 Д_Н_2_ДЛ,
        {features}rpms.LENGTH_PART_3 Д_Н_3_ДЛ,
        {features}rpms.FURNACE ПЕЧЬ_РЯД,
        {features}--to_char(rpms.FURNACE_IN_DT,'dd.mm.yyyy hh24:mi:ss') ЗАГР_ПЕЧЬ,
        {features}--to_char(rpms.FURNACE_OUT_DT,'dd.mm.yyyy hh24:mi:ss') ВЫГР_ПЕЧЬ,
        {features}rpms.FURNACE_HEAT_DURATION ДЛИТ_ПЕЧЬ,
        {features}(max(rpm.COMPLETION) - max(rpm.DISCHARGE))*24*60 ДЛИТ_ПРОКАТ,
        {features}rtl.FURNACE_HEAT_TEMPERATURE ПЛ_Т_ПЕЧЬ,
        {features}rpms.FURNACE_HEAT_TEMPERATURE ФК_Т_ПЕЧЬ,
        {features}max(rpm.ROLLINGPROGRAM) СХЕМА_ПРОК,
        {features}rpms.DUO_PASS_AMOUNT ДУО_ПРОХ,
        {features}sum(decode(substr(rpm.STAFF,1,1),'Q',0,decode(rpm.PASSTYPE,'Idle',1))) ДУО_ХОЛОСТ,
        {features}sum(decode(rpm.DESCALINGS1,'ON',1)) ГИДРОСБИВ,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 1,rpm.REDUCTION))) ДУО_ОБЖ_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 2,rpm.REDUCTION))) ДУО_ОБЖ_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.REDUCTION))) ДУО_ОБЖ_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 4,rpm.REDUCTION))) ДУО_ОБЖ_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 5,rpm.REDUCTION))) ДУО_ОБЖ_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 6,rpm.REDUCTION))) ДУО_ОБЖ_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 7,rpm.REDUCTION))) ДУО_ОБЖ_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 8,rpm.REDUCTION))) ДУО_ОБЖ_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 9,rpm.REDUCTION))) ДУО_ОБЖ_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,10,rpm.REDUCTION))) ДУО_ОБЖ_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,11,rpm.REDUCTION))) ДУО_ОБЖ_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,12,rpm.REDUCTION))) ДУО_ОБЖ_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,13,rpm.REDUCTION))) ДУО_ОБЖ_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,14,rpm.REDUCTION))) ДУО_ОБЖ_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,15,rpm.REDUCTION))) ДУО_ОБЖ_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 1,rpm.STANDFORCE))) ДУО_УСС_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 2,rpm.STANDFORCE))) ДУО_УСС_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.STANDFORCE))) ДУО_УСС_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 4,rpm.STANDFORCE))) ДУО_УСС_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 5,rpm.STANDFORCE))) ДУО_УСС_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 6,rpm.STANDFORCE))) ДУО_УСС_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 7,rpm.STANDFORCE))) ДУО_УСС_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 8,rpm.STANDFORCE))) ДУО_УСС_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 9,rpm.STANDFORCE))) ДУО_УСС_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,10,rpm.STANDFORCE))) ДУО_УСС_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,11,rpm.STANDFORCE))) ДУО_УСС_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,12,rpm.STANDFORCE))) ДУО_УСС_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,13,rpm.STANDFORCE))) ДУО_УСС_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,14,rpm.STANDFORCE))) ДУО_УСС_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,15,rpm.STANDFORCE))) ДУО_УСС_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 1,rpm.FORCEMA))) ДУО_УСП_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 2,rpm.FORCEMA))) ДУО_УСП_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.FORCEMA))) ДУО_УСП_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 4,rpm.FORCEMA))) ДУО_УСП_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 5,rpm.FORCEMA))) ДУО_УСП_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 6,rpm.FORCEMA))) ДУО_УСП_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 7,rpm.FORCEMA))) ДУО_УСП_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 8,rpm.FORCEMA))) ДУО_УСП_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 9,rpm.FORCEMA))) ДУО_УСП_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,10,rpm.FORCEMA))) ДУО_УСП_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,11,rpm.FORCEMA))) ДУО_УСП_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,12,rpm.FORCEMA))) ДУО_УСП_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,13,rpm.FORCEMA))) ДУО_УСП_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,14,rpm.FORCEMA))) ДУО_УСП_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,15,rpm.FORCEMA))) ДУО_УСП_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 1,rpm.TOPSPEED))) ДУО_СКР_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 2,rpm.TOPSPEED))) ДУО_СКР_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.TOPSPEED))) ДУО_СКР_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 4,rpm.TOPSPEED))) ДУО_СКР_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 5,rpm.TOPSPEED))) ДУО_СКР_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 6,rpm.TOPSPEED))) ДУО_СКР_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 7,rpm.TOPSPEED))) ДУО_СКР_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 8,rpm.TOPSPEED))) ДУО_СКР_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 9,rpm.TOPSPEED))) ДУО_СКР_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,10,rpm.TOPSPEED))) ДУО_СКР_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,11,rpm.TOPSPEED))) ДУО_СКР_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,12,rpm.TOPSPEED))) ДУО_СКР_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,13,rpm.TOPSPEED))) ДУО_СКР_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,14,rpm.TOPSPEED))) ДУО_СКР_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER,15,rpm.TOPSPEED))) ДУО_СКР_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(rpm.PASSNUMBER, 3,rpm.LSTEMP))) ДУО_Т_3_ПР,
        {features}decode( sum(decode(substr(rpm.STAFF,1,1),'Q',0,decode(rpm.PASSTYPE,'Idle',1))),1,max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,-1,1),'T',rpm.FSTEMP))),max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,-1,1),'T',rpm.LSTEMP))) ) ДУО_Т_ПОСЛ,

        {features}rpms.INTERCELL_COOLING УМО,
        {features}rpms.SHEET_ROLL ПОДКАТ,

        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 1,rpm.REDUCTION))) КВР_ОБЖ_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.REDUCTION))) КВР_ОБЖ_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.REDUCTION))) КВР_ОБЖ_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.REDUCTION))) КВР_ОБЖ_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.REDUCTION))) КВР_ОБЖ_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.REDUCTION))) КВР_ОБЖ_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.REDUCTION))) КВР_ОБЖ_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.REDUCTION))) КВР_ОБЖ_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.REDUCTION))) КВР_ОБЖ_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.REDUCTION))) КВР_ОБЖ_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.REDUCTION))) КВР_ОБЖ_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.REDUCTION))) КВР_ОБЖ_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.REDUCTION))) КВР_ОБЖ_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.REDUCTION))) КВР_ОБЖ_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,15,rpm.REDUCTION))) КВР_ОБЖ_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 1,rpm.STANDFORCE))) КВР_УСС_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.STANDFORCE))) КВР_УСС_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.STANDFORCE))) КВР_УСС_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.STANDFORCE))) КВР_УСС_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.STANDFORCE))) КВР_УСС_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.STANDFORCE))) КВР_УСС_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.STANDFORCE))) КВР_УСС_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.STANDFORCE))) КВР_УСС_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.STANDFORCE))) КВР_УСС_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.STANDFORCE))) КВР_УСС_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.STANDFORCE))) КВР_УСС_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.STANDFORCE))) КВР_УСС_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.STANDFORCE))) КВР_УСС_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.STANDFORCE))) КВР_УСС_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,15,rpm.STANDFORCE))) КВР_УСС_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 1,rpm.FORCEMA))) КВР_УСП_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.FORCEMA))) КВР_УСП_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.FORCEMA))) КВР_УСП_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.FORCEMA))) КВР_УСП_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.FORCEMA))) КВР_УСП_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.FORCEMA))) КВР_УСП_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.FORCEMA))) КВР_УСП_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.FORCEMA))) КВР_УСП_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.FORCEMA))) КВР_УСП_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.FORCEMA))) КВР_УСП_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.FORCEMA))) КВР_УСП_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.FORCEMA))) КВР_УСП_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.FORCEMA))) КВР_УСП_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.FORCEMA))) КВР_УСП_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,15,rpm.FORCEMA))) КВР_УСП_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 1,rpm.TOPSPEED))) КВР_СКР_01,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.TOPSPEED))) КВР_СКР_02,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.TOPSPEED))) КВР_СКР_03,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.TOPSPEED))) КВР_СКР_04,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.TOPSPEED))) КВР_СКР_05,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.TOPSPEED))) КВР_СКР_06,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.TOPSPEED))) КВР_СКР_07,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.TOPSPEED))) КВР_СКР_08,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.TOPSPEED))) КВР_СКР_09,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.TOPSPEED))) КВР_СКР_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.TOPSPEED))) КВР_СКР_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.TOPSPEED))) КВР_СКР_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.TOPSPEED))) КВР_СКР_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.TOPSPEED))) КВР_СКР_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,15,rpm.TOPSPEED))) КВР_СКР_15,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 1,rpm.FORCEEND))) delta1_2,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 2,rpm.FORCEEND))) delta2_3,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 3,rpm.FORCEEND))) delta3_4,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 4,rpm.FORCEEND))) delta4_5,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 5,rpm.FORCEEND))) delta5_6,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 6,rpm.FORCEEND))) delta6_7,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 7,rpm.FORCEEND))) delta7_8,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 8,rpm.FORCEEND))) delta8_9,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT, 9,rpm.FORCEEND))) delta9_10,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,10,rpm.FORCEEND))) delta10_11,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,11,rpm.FORCEEND))) delta11_12,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,12,rpm.FORCEEND))) delta12_13,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,13,rpm.FORCEEND))) delta13_14,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,15,rpm.FORCESTART)))-max(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSNUMBER-rpms.DUO_PASS_AMOUNT,14,rpm.FORCEEND))) delta14_15,

        {features}rtl.QUARTO_TEMPERATURE_OUT КВР_Т_ПЛАН,
        {features}max(decode(rpm.STAFF,'Q1',rpm.FSTEMP)) КВР_Т_1_ПР,
        {features}max(rpm.S2START) s2_start,
        {features}rpms.QUARTO_TEMPERATURE КВР_Т_ПОСЛ,
        {features}max(rpm.PLATETEMPBIAS) ВМЕШ_ТЕМП,
        {features}rpms.QUARTO_PASS_AMOUNT КВР_ПРОХ,

        {features}sum(decode(substr(rpm.STAFF,1,1),'Q',decode(rpm.PASSTYPE,'Idle',1))) КВР_ХОЛОСТ,

        {features}rtl.COOLING_STRATEGY УКО_СТРАТ,
        {features}rtl.COOLING_TEMPERATURE_OUT УКО_Т_ПЛАН,
        {features}rtl.COOLING_INTENSITY УКО_И_ПЛАН,
        {features}rrc.COL_TMP_STA_TCK_MEA УКО_Т_НАЧ,
        {features}rrc.TMP_COL_STP_CAL УКО_Т_КОН,
        {features}rrc.COL_RAT_AVG_CAL_ACC УКО_ИНТ,
        {features}rrc.ADP_SPD УКО_СКОР,

        {features}decode(rrc.WAT_FLW_AVG_THD01,null,'',0,'','1,') ||decode(rrc.WAT_FLW_AVG_THD02,null,'',0,'','2,') ||decode(rrc.WAT_FLW_AVG_THD03,null,'',0,'','3,') ||decode(rrc.WAT_FLW_AVG_THD04,null,'',0,'','4,') ||decode(rrc.WAT_FLW_AVG_THD05,null,'',0,'','5,') ||decode(rrc.WAT_FLW_AVG_THD06,null,'',0,'','6,') ||decode(rrc.WAT_FLW_AVG_THD07,null,'',0,'','7,') ||decode(rrc.WAT_FLW_AVG_THD08,null,'',0,'','8,') ||decode(rrc.WAT_FLW_AVG_THD09,null,'',0,'','9,') ||decode(rrc.WAT_FLW_AVG_THD10,null,'',0,'','10,') ||decode(rrc.WAT_FLW_AVG_THD11,null,'',0,'','11,') ||decode(rrc.WAT_FLW_AVG_THD12,null,'',0,'','12,') ||decode(rrc.WAT_FLW_AVG_THD13,null,'',0,'','13,') ||decode(rrc.WAT_FLW_AVG_THD14,null,'',0,'','14') УКО_ВЕРХ_С,
        {features}decode(rrc.WAT_FLW_AVG_BHD01,null,'',0,'','1,') ||decode(rrc.WAT_FLW_AVG_BHD02,null,'',0,'','2,') ||decode(rrc.WAT_FLW_AVG_BHD03,null,'',0,'','3,') ||decode(rrc.WAT_FLW_AVG_BHD04,null,'',0,'','4,') ||decode(rrc.WAT_FLW_AVG_BHD05,null,'',0,'','5,') ||decode(rrc.WAT_FLW_AVG_BHD06,null,'',0,'','6,') ||decode(rrc.WAT_FLW_AVG_BHD07,null,'',0,'','7,') ||decode(rrc.WAT_FLW_AVG_BHD08,null,'',0,'','8,') ||decode(rrc.WAT_FLW_AVG_BHD09,null,'',0,'','9,') ||decode(rrc.WAT_FLW_AVG_BHD10,null,'',0,'','10,') ||decode(rrc.WAT_FLW_AVG_BHD11,null,'',0,'','11,') ||decode(rrc.WAT_FLW_AVG_BHD12,null,'',0,'','12,') ||decode(rrc.WAT_FLW_AVG_BHD13,null,'',0,'','13,') ||decode(rrc.WAT_FLW_AVG_BHD14,null,'',0,'','14') УКО_НИЖН_С,


        {features}max(decode(substr(rpm.STAFF,1,2),'H1',rpm.FORCESTART,'L1',rpm.FORCESTART)) ПЕЧЬ_ДУО,
        {features}max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,2,1),'N',rpm.FORCEEND))) - max(decode(substr(rpm.STAFF,1,2),'H1',rpm.FORCESTART,'L1',rpm.FORCESTART)) ДУО_ВРЕМЯ,
        {features}max(decode(substr(rpm.STAFF,1,2),'Q1',rpm.FORCESTART)) - max(decode(substr(rpm.STAFF,1,1),'Q',to_number(null),decode(substr(rpm.STAFF,2,1),'N',rpm.FORCEEND))) ДУО_КВР,
        {features}max(decode(rpm.STAFF,'QN',rpm.FORCEEND,'QNT',rpm.FORCEEND))- max(decode(substr(rpm.STAFF,1,2),'Q1',rpm.FORCESTART)) КВР_ВРЕМЯ,
        {features}round(86400*(rrc.COL_STP_DAT-rrc.COL_STA_DAT),5) УКО_ВРЕМЯ,

        {features}--count(*) over(order by max(rpm.COMPLETION) range between numtodsinterval(nvl(max(rpm.COMPLETION),sysdate)-nvl(max(rpm.DISCHARGE),sysdate),'day') preceding and current row) КОЛ_СЛ_НАЧ,
        {features}--count(*) over(order by nvl(max(rpm.DISCHARGE),rpms.FURNACE_OUT_DT)  range between current row and numtodsinterval(nvl(max(rpm.COMPLETION),sysdate)-nvl(max(rpm.DISCHARGE),sysdate),'day') following) КОЛ_СЛ_КОН,


        {features}rpms.VIOLATION_CODE КОД_ОШИБКИ,
        {features}rpms.TEXT_VIOLATION КОД_ЦЛК,

        {features}rhc.CEV УГЛ_ЭКВ,
        {features}rhc.CHEM_COMPOS_COEFF КХС,
        {features}rhc.ELEMENT_C c,
        {features}rhc.ELEMENT_SI si,
        {features}rhc.ELEMENT_MN mn,
        {features}rhc.ELEMENT_P p,
        {features}rhc.ELEMENT_S s,
        {features}rhc.ELEMENT_CR cr,
        {features}rhc.ELEMENT_NI ni,
        {features}rhc.ELEMENT_CU cu,
        {features}rhc.ELEMENT_TI ti,
        {features}rhc.ELEMENT_AL al,
        {features}rhc.ELEMENT_N n2,
        {features}rhc.ELEMENT_NB nb,
        {features}rhc.ELEMENT_V v,
        {features}rhc.ELEMENT_B b,
        {features}rhc.ELEMENT_MO mo,
        {features}decode(rpo.ASSIGN_STOWING, 'Y', 1, 'N', 0) СТОППИР{targets},

        {targets}rtmr.ROLLED_LOT_ID NOMP,
        {targets}rtmr.HEAT_TREATMENT_CODE VTR,
        {targets}rtmr.SHEET_NUM NISP,
        {targets}rtmr.EQUIPMENT_TEST_CODE ISP_OB,
        {targets}rtmr.YIELD_STRENGTH FPT,
        {targets}rtmr.TENSILE_STRENGTH FVS,
        {targets}rtmr.ELOGATION FOYD,
        {targets}--rtmr.YIELD_TO_TENSILE_STRENGTH,
        {targets}rtmr.REDUCTION_OF_AREA FOS,
        {targets}rtmr.YIELD_STR_COMPLETE FPTP,
        {targets}rtmr.TENSILE_STRENGTH_ALONG FVSP,
        {targets}rtmr.ELOGATION_ALONG FOYDP,
        {targets}rtmr.UNIFROM_ELOGATION_ALONG FYDR,
        {targets}rtmr.SAMPLE_TYPE_KCU TUV1,
        {targets}rtmr.KCU_TEMPERATURE T_KCU,
        {targets}rtmr.IMPACT_STRENGTH_KCU_1 FUV_1,
        {targets}rtmr.IMPACT_STRENGTH_KCU_2 FUV_2,
        {targets}rtmr.IMPACT_STRENGTH_KCU_3 FUV_3,
        {targets}rtmr.SAMPLE_TYPE_KCV TUV2,
        {targets}rtmr.KCV_TEMPERATURE T_KCV,
        {targets}rtmr.IMPACT_STRENGTH_KCV_1 FDV_1,
        {targets}rtmr.IMPACT_STRENGTH_KCV_2 FDV_2,
        {targets}rtmr.IMPACT_STRENGTH_KCV_3 FDV_3,
        {targets}rtmr.DWTT_TEMPERATURE T_KCD,
        {targets}rtmr.DWTT_1 DWTT1,
        {targets}rtmr.DWTT_2 DWTT2,
        {targets}rtmr.KV_KCV_TEMPERATURE T_KCDV,
        {targets}rtmr.VISCOUS_COMPONENT_1 DVC1,
        {targets}rtmr.VISCOUS_COMPONENT_2 DVC2,
        {targets}rtmr.VISCOUS_COMPONENT_3 DVC3,
        {targets}rtmr.HARDNESS_1 NB1,
        {targets}rtmr.HARDNESS_2 NB2,
        {targets}rtmr.PARAMETER_OVERSTEPPING VPN,
        {targets}rtmr.PARAMETER_OVERSHOOT VPV,
        {targets}rtmr.YIELD_STR_PLASTIC_05 FPT05,
        {targets}rtmr.YIELD_STR_COMPLETE_05 FPTP05,
        {targets}rtmr.IMPACT_STR_FAILURE_1 PRVLU,
        {targets}rtmr.IMPACT_STR_FAILURE_2 PRVLV,
        {targets}rtmr.VISCOUS_COMPONENT_FAILURE PRVVC,
        {targets}rtmr.DWTT_FAILURE PRLDW

        from ROLL_REPORT_MILL_SHORT rpms
        left outer join ROLL_REPORT_MILL rpm on rpms.SLAB_ID = rpm.SLAB_ID
        {features}left outer join ROLL_TASK_LEVEL3 rtl on rpms.REPORT_ORDER_ID= rtl.REPORT_ORDER_ID
        inner join ROLL_REPORT_ORDER rpo on rpms.REPORT_ORDER_ID = rpo.REPORT_ORDER_ID
        {targets}inner join ROLL_TEST_MECHANIC_RESULT rtmr on rtmr.HEAT = rpo.HEAT
        {features}left outer join ROLL_HEAT_CHEMISTRY rhc on (rpo.HEAT= rhc.HEAT and rpo.STD_REQUIREMENTS= rhc.STD_REQUIREMENTS)
        {features}left outer join ROLL_REPORT_COOLING rrc on rpms.SLAB_ID=rrc.SLAB_ID

        where rpm.COMPLETION > TO_DATE('{start_date}', 'YYYY-MM-DD HH24:MI:SS')
              {targets}and rtmr.SHEET_NUM between rpms.SHEET_NUM_1 and rpms.SHEET_NUM_1+rpms.CUT_AMOUNT-1 -- get correct slab

        group by
            rpms.REPORT_ORDER_ID,rpms.SLAB_ID,rpms.SLAB_NUM,rpms.SHEET_NUM_1,rpms.SLAB_WEIGHT,rpms.LENGTH_PART_1, rpms.LENGTH_PART_2, rpms.LENGTH_PART_3,rpms.FURNACE, rpms.FURNACE_IN_DT,rpms.FURNACE_OUT_DT,rpms.FURNACE_HEAT_DURATION,rpms.FURNACE_HEAT_TEMPERATURE, rpms.DUO_PASS_AMOUNT,rpms.INTERCELL_COOLING,rpms.QUARTO_TEMPERATURE,rpms.SHEET_ROLL,rpms.QUARTO_PASS_AMOUNT,rpms.VIOLATION_CODE, rpms.TEXT_VIOLATION,
            rpo.HOT_PUT, rpo.ROLLING_DT, rpo.ORDER_NUM, rpo.ORDER_POSITION, rpo.HEAT,rpo.EAF_TECHNOLOGY_CODE, rpo.DEGASSING, rpo.ROLLED_LOT_ID, rpo.SHEET_NUM,rpo.SHEET_AMOUNT, rpo.STEEL_GRADE, rpo.STEEL_CODE, rpo.STD_REQUIREMENTS, rpo.THICKNESS, rpo.WIDTH,rpo.LENGTH, rpo.SLAB_THICKNESS, rpo.SLAB_WIDTH, rpo.SLAB_LENGTH, rpo.SLAB_WEIGHT_COUNT,rpo.CUT_AMOUNT, rpo.WEIGHT_SHEET_COUNT, rpo.ASSIGN_STOWING,
            {features}rpms.DT_INS, rtl.FURNACE_HEAT_TEMPERATURE,rtl.QUARTO_TEMPERATURE_OUT,rtl.COOLING_STRATEGY,rtl.COOLING_TEMPERATURE_OUT,rtl.COOLING_INTENSITY,rtl.FURNACE_HEAT_TEMPERATURE,rtl.QUARTO_TEMPERATURE_OUT, rtl.COOLING_STRATEGY, rtl.COOLING_TEMPERATURE_OUT,rtl.COOLING_INTENSITY,
            {features}rhc.CEV,rhc.CHEM_COMPOS_COEFF,rhc.ELEMENT_C,rhc.ELEMENT_SI,rhc.ELEMENT_MN,rhc.ELEMENT_P,rhc.ELEMENT_S,rhc.ELEMENT_CR,rhc.ELEMENT_NI,rhc.ELEMENT_CU,rhc.ELEMENT_TI,rhc.ELEMENT_AL,rhc.ELEMENT_N,rhc.ELEMENT_NB,rhc.ELEMENT_V,rhc.ELEMENT_B,rhc.ELEMENT_MO,
            {features}rrc.COL_STP_DAT, rrc.COL_STA_DAT, rrc.COL_TMP_STA_TCK_MEA, rrc.TMP_COL_STP_CAL,rrc.COL_RAT_AVG_CAL_ACC, rrc.ADP_SPD,rrc.WAT_FLW_AVG_THD01,rrc.WAT_FLW_AVG_THD02, rrc.WAT_FLW_AVG_THD03,rrc.WAT_FLW_AVG_THD04, rrc.WAT_FLW_AVG_THD05, rrc.WAT_FLW_AVG_THD06,rrc.WAT_FLW_AVG_THD07, rrc.WAT_FLW_AVG_THD08, rrc.WAT_FLW_AVG_THD09,rrc.WAT_FLW_AVG_THD10, rrc.WAT_FLW_AVG_THD11, rrc.WAT_FLW_AVG_THD12,rrc.WAT_FLW_AVG_THD13, rrc.WAT_FLW_AVG_THD14, rrc.WAT_FLW_AVG_BHD01,rrc.WAT_FLW_AVG_BHD02, rrc.WAT_FLW_AVG_BHD03, rrc.WAT_FLW_AVG_BHD04,rrc.WAT_FLW_AVG_BHD05, rrc.WAT_FLW_AVG_BHD06, rrc.WAT_FLW_AVG_BHD07,rrc.WAT_FLW_AVG_BHD08, rrc.WAT_FLW_AVG_BHD09, rrc.WAT_FLW_AVG_BHD10,rrc.WAT_FLW_AVG_BHD11,rrc.WAT_FLW_AVG_BHD12,rrc.WAT_FLW_AVG_BHD13,rrc.WAT_FLW_AVG_BHD14{targets},
            {targets}rtmr.ROLLED_LOT_ID,rtmr.HEAT_TREATMENT_CODE,rtmr.SHEET_NUM,rtmr.EQUIPMENT_TEST_CODE,rtmr.YIELD_STRENGTH,rtmr.TENSILE_STRENGTH,rtmr.ELOGATION,rtmr.REDUCTION_OF_AREA,rtmr.YIELD_STR_COMPLETE,rtmr.TENSILE_STRENGTH_ALONG,rtmr.ELOGATION_ALONG,rtmr.UNIFROM_ELOGATION_ALONG,rtmr.SAMPLE_TYPE_KCU,rtmr.KCU_TEMPERATURE,rtmr.IMPACT_STRENGTH_KCU_1,rtmr.IMPACT_STRENGTH_KCU_2,rtmr.IMPACT_STRENGTH_KCU_3,rtmr.SAMPLE_TYPE_KCV,rtmr.KCV_TEMPERATURE,rtmr.IMPACT_STRENGTH_KCV_1,rtmr.IMPACT_STRENGTH_KCV_2,rtmr.IMPACT_STRENGTH_KCV_3,rtmr.DWTT_TEMPERATURE, rtmr.DWTT_1, rtmr.DWTT_2,rtmr.KV_KCV_TEMPERATURE, rtmr.VISCOUS_COMPONENT_1, rtmr.VISCOUS_COMPONENT_2,rtmr.VISCOUS_COMPONENT_3,rtmr.HARDNESS_1, rtmr.HARDNESS_2,rtmr.PARAMETER_OVERSTEPPING, rtmr.PARAMETER_OVERSHOOT,rtmr.YIELD_STR_PLASTIC_05, rtmr.YIELD_STR_COMPLETE_05,rtmr.IMPACT_STR_FAILURE_1, rtmr.IMPACT_STR_FAILURE_2,rtmr.VISCOUS_COMPONENT_FAILURE, rtmr.DWTT_FAILURE,rtmr.PROTOCOL_DT

        order by max(rpm.DISCHARGE)
    )
    where
    {features} {filters}
    ROWNUM <= 100000
    order by КОН_ПРОКАТ

'''


class OracleDB_Connector:
    def __init__(self, user_oracle = '', password_oracle = '', dsn_oracle = ''):

        # cx.init_oracle_client(lib_dir= r'C:/Program Files/Oracle/instantclient_21_3')
        self.cx_conn = cx.connect(user=user_oracle, password=password_oracle, dsn=dsn_oracle)
        self.cx_cursor = self.cx_conn.cursor()

    def datet2str(self, value):
        # str representation has to be compatible with sql server
        # yyyy-mm-dd
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def get_filtered_data(self, start_date:str, features: bool, targets:bool,
                            equality_constraints: dict = {},
                            interval_constraints: dict = {}):
        # start_date in fmt '2019-01-01 00:00:00'

        # eq_constr = {}
        # for key in equality_constraints:
        #     if key in alias:
        #         eq_constr[alias[key]] = equality_constraints[key]

        # in_constr = {}
        # for key in interval_constraints:
        #     if key in alias:
        #         in_constr[alias[key]] = interval_constraints[key]

        df = pd.read_sql_query(query_init(start_date=self.datet2str(start_date),
                                          features=features,
                                          targets=targets,
                                          filters= create_where(equality_constraints, interval_constraints)),
                               self.cx_conn)

        return df

    def close(self):
        self.cx_conn.close()
