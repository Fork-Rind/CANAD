# canad : CAN Anomaly Detector
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import sys
# from tqdm import tqdm
from typing import List, Dict
import os

DEBUG = False

class Dispatcher:
    NO_IDX = 0
    TIME_OFFSET_IDX = 1
    TYPE_IDX = 2
    ID_IDX = 3
    DATA_LENGTH_IDX = 4
    BYTE1_IDX = 5
    BYTE2_IDX = 6
    BYTE3_IDX = 7
    BYTE4_IDX = 8
    BYTE5_IDX = 9
    BYTE6_IDX = 10
    BYTE7_IDX = 11
    BYTE8_IDX = 12
    detection_dir_path = "./detection"
    
    def __init__(self):
        # func: 함수 포인터
        # type: 타입
        # element_size: 원소 1개의 크기 (스택에 들어가는 원소 1개의 크기를 뜻 함)
        # desc: 설명
        self.chk_func_info = [
            {"func":self.__chk_seatbelt_off_engine_on, "type":"chk_seatbelt_off_engine_on", 'element_size':1, 'desc':"안전벨트를 풀고 엔진을 킨 상태"},
            {"func":self.__chk_gear_R_seatbelt_off, "type":"chk_gear_R_seatbelt_off", 'element_size':2, 'desc':"안전벨트를 풀고 후진하는 상태"},
            {"func":self.__chk_gear_D_seatbelt_off, "type":"chk_gear_D_seatbelt_off", 'element_size':2, 'desc':"안전벨트를 풀고 전진하는 상태"},
            {"func":self.__chk_engine_on_handbreak_off_seatbelt_off, "type":"chk_engine_on_handbreak_off_seatbelt_off", 'element_size':1, 'desc':"안전벨트를 풀고, 엔진을 키고, 핸드 브레이크를 off한 상태"},
            {"func":self.__chk_gear_P_push_accelerator, "type":"chk_gear_P_push_accelerator", 'element_size':2, 'desc':"P기어 중에 엑셀을 밟은 상태 (차량 손상)"},
            
            {"func":self.__chk_gear_P_inc_speed, "type":"chk_gear_P_inc_speed", 'element_size':2, 'desc':"P기어 중에 속도가 증가하는 상태 (잠재적 시스템 손상)"}, # 결과 3개만 나옴
            
            {"func":self.__chk_gear_N_push_accelerator, "type":"chk_gear_N_push_accelerator", 'element_size':2, 'desc':"N기어 중에 엑셀을 밟는 상태 (차량 손상)"},
            
            {"func":self.__chk_gear_D_handbreak_on, "type":"chk_gear_D_handbreak_on", 'element_size':2, 'desc':"D기어 중에 핸드 브레이크를 끄지 않은 상태"},
            {"func":self.__chk_gear_R_handbreak_on, "type":"chk_gear_R_handbreak_on", 'element_size':2, 'desc':"R기어 중에 핸드브레이크를 끄지 않은 상태"},
            {"func":self.__chk_gear_R_engine_off, "type":"chk_gear_R_engine_off", 'element_size':2, 'desc':"R 기어 중 엔진을 끈 상태 (기어 손상)"},
            {"func":self.__chk_gear_D_engine_off, "type":"chk_gear_D_engine_off", 'element_size':2, 'desc':"D 기어 중 엔진을 끈 상태"},
            {"func":self.__chk_engine_off_gear_D, "type":"chk_engine_off_gear_D", 'element_size':2, 'desc':"엔진이 꺼진 상태에서 D기어로 올린 상태"},
            {"func":self.__chk_driver_door_open_gear_D, "type":"chk_driver_door_open_gear_D", 'element_size':2, 'desc':"운전석 문이 열린 상태에서 D기어로 올린 상태"},
            {"func":self.__chk_driver_door_open_gear_R, "type":"chk_driver_door_open_gear_R", 'element_size':2, 'desc':"운전석 문이 열린 상태에서 R기어로 올린 상태"},
            
            # {"func":self.__chk_high_low_beam, "type":"chk_high_low_beam", 'element_size':1, 'desc':"high, low 모두 키고 운행"}, # 아래꺼랑 결과가 같음 # 삭제
            {"func":self.__chk_high_middle_low_beam, "type":"chk_high_middle_low_beam", 'element_size':1, 'desc':"high beam, middle beam, low beam 모두 On 인 상태"},
            {"func":self.__chk_middle_fog_low, "type":"chk_middle_fog_low", 'element_size':1, 'desc':"middle beam, fog beam, low beam 모두 On 인 상태"},
            
            # {"func":self.__chk_push_accelerator_not_inc_speed, "type":"chk_push_accelerator_not_inc_speed", 'element_size':2, 'desc':"엑셀을 밟았는데(rpm이 올라갔는데) 속도가 오르지 않음"}, # 삭제
            {"func":self.__chk_emergency_light_on_high_speed, "type":"chk_emergency_light_on_high_speed", 'element_size':2, 'desc':"비상등이 켜진 상태에서 speed가 증가하는 상태"},
            
            {"func":self.__chk_sub_door_open_gear_D, "type":"chk_sub_door_open_gear_D", 'element_size':2, 'desc':"조수석 문이 열린 상태에서 D기어로 올린 상태"},
            {"func":self.__chk_sub_door_open_gear_R, "type":"chk_sub_door_open_gear_R", 'element_size':2, 'desc':"조수석 문이 열린 상태에서 R기어로 올린 상태"},
            
            {"func":self.__chk_seatbelt_off_engine_on_2, "type":"chk_seatbelt_off_engine_on_2", 'element_size':1, 'desc':"안전벨트를 풀고 엔진을 킨 상태 (낮,밤)"},
            
            {"func":self.__chk_gear_R_seatbelt_off_2, "type":"chk_gear_R_seatbelt_off_2", 'element_size':2, 'desc':"안전벨트를 풀고 후진하는 상태(낮,밤)"},
            {"func":self.__chk_gear_D_seatbelt_off_2, "type":"chk_gear_D_seatbelt_off_2", 'element_size':2, 'desc':"안전벨트를 풀고 전진하는 상태(낮,밤)"},
            {"func":self.__chk_engine_on_handbreak_off_seatbelt_off_2, "type":"chk_engine_on_handbreak_off_seatbelt_off_2", 'element_size':1, 'desc':"안전벨트를 풀고 엔진을 키고 핸드브래이크를 off한 상태(낮,밤)"},
            
            {"func":self.__chk_electricity_on_high_beam_on, "type":"chk_electricity_on_high_beam_on", 'element_size':1, 'desc':"전기만 켜진 상태에서 상향등을 사용하는 상태 (배터리 수명 단축 및 주변 환경 방해)"},
            {"func":self.__chk_electricity_on_fog_beam_on, "type":"chk_electricity_on_fog_beam_on", 'element_size':1, 'desc':"전기만 켜진 상태에서 안개등을 사용하는 상태 (배터리 수명 단축 및 주변 환경 방해)"},
            
            {"func":self.__chk_day_high_beam_on, "type":"chk_day_high_beam_on", 'element_size':1, 'desc':"낮에 High beam을 키고 운행하는 상태 (배터리 수명 단축 및 주변 환경 방해)"},
            {"func":self.__chk_day_fog_beam_on, "type":"chk_day_fog_beam_on", 'element_size':1, 'desc':"낮에 Fog light를 키고 운행하는 상태 (배터리 수명 단축 및 주변 환경 방해)"},
        ]
        self.CAN_msgs_stack:Dict[str:list] = {} # {type_name: [CAN_msg, ...], ...}
        
        self.find_anomaly:Dict[str:list] = {} # {type_name: [[CAN_msg_start, CAN_msg_end], [CAN_msg_start, CAN_msg_end], ...], ...}
        
        self.time_offset_list:Dict[str:list] = {} # 시간차이를 저장한 리스트
        
    def __get_desc(self, type_name:str) -> str:
        for func_info in self.chk_func_info:
            if (func_info['type'] == type_name):
                return func_info['desc']
        
    def __calc_time_offset(self, func_info:dict) -> float:
        '''
        self.time_offset_list에 이전 로그와의 시간차 등록 함수
        '''
        # 이전 원소와의 시간차
        now_msg = self.CAN_msgs_stack[func_info['type']][-func_info['element_size']:]
        time_offset = 0
        if (len(self.CAN_msgs_stack[func_info['type']]) > func_info['element_size']):
            before_msg = self.CAN_msgs_stack[func_info['type']][-func_info['element_size'] * 2: -func_info['element_size']]
            time_offset = float(now_msg[0][self.TIME_OFFSET_IDX]) - float(before_msg[0][self.TIME_OFFSET_IDX])
        try:
            self.time_offset_list[func_info['type']].append(time_offset)
        except KeyError:
            self.time_offset_list[func_info['type']] = [time_offset]
        return time_offset
        
    def __average_time_offset(self, type_name:str) -> float:
        by = max((len(self.time_offset_list[type_name]) - 1), 1)
        return sum(self.time_offset_list[type_name]) / by
        
    def get_resuit(self):
        '''
        각 로그 타입별로 시작 시간 및 종료 시간 출력 함수
        # 기준 time offset 평군
        '''
        for func_info in self.chk_func_info:
            type_name = func_info['type']
            
            # 로그 한 세트가 완성되지 못한 경우, 마지막 불필요한 로그 제거
            try:
                if ((len(self.CAN_msgs_stack[type_name]) % func_info['element_size']) != 0):
                    self.CAN_msgs_stack[type_name].pop(-1)
            except KeyError: # 해당하는 경우가 없어 로그 세트가 생성되지 않은 타입의 경우 넘어가기
                continue

            # 로그 세트 스택이 비어있는 경우 넘어가기
            if (len(self.CAN_msgs_stack[type_name]) == 0):
                continue
            
            # 해당 type의 평균 구하기
            average = self.__average_time_offset(type_name)
            average = max([average, 1000.0]) # 최소 1초
            
            if DEBUG:
                print(f"time offset average : {average}")
                print(f"self.CAN_msgs_stack[type_name] length : {len(self.CAN_msgs_stack[type_name])}") # test
                print(f"self.time_offset_list[type_name] length : {len(self.time_offset_list[type_name])}") # test
            # len(self.CAN_msgs_stack[type_name]) / func_info['element_size'] - 1 == len(self.time_offset_list[type_name])
            
            # 각 시간 오프셋 값과 평균값과 비교하여 연속값 데이터프레임 생성
            # : 각 시간 오프셋 <= 평균값 : 연달아 진행된 이벤트
            # : 각 시간 오프셋 >  평균값 : 별개의 이벤트
            continuous_log_list:Dict[int:list] = {} # {continuous_id:[start_can_msg, end_can_msg], continuous_id_2:[...], ...}
            continuous_id_count = 0
            for i in range(len(self.time_offset_list[type_name])):
                can_msg_log_set = []
                for j in range(func_info['element_size']):
                    can_msg_log_set.append(self.CAN_msgs_stack[type_name][i *  func_info['element_size'] + j])
                # print(can_msg_log_set)
                if (self.time_offset_list[type_name][i] == 0): # 새로운 시작
                    continuous_log_list[continuous_id_count] = [can_msg_log_set]
                elif (self.time_offset_list[type_name][i] <= average): # 연달아 진행된 이벤트
                    continuous_log_list[continuous_id_count].append(can_msg_log_set)
                else: # 새로운 시작
                    continuous_id_count += 1
                    continuous_log_list[continuous_id_count] = [can_msg_log_set]
                
            # 최종 로그 출력
            if DEBUG:
                print(f"(continuous_log_list)") # test
                for t in continuous_log_list:
                    print(f"{t}:")
                    for log in continuous_log_list[t]:
                        print(log)
                
            # 최종 로그 저장
            self.find_anomaly[type_name] = []
            for t in continuous_log_list:
                self.find_anomaly[type_name].append(continuous_log_list[t])
    
    def __save_pie_graph(self, events:list):
        # 데이터 추출
        labels = [event['type'] for event in events]
        sizes = [event['count'] for event in events]

        # 실제 개수를 표시하는 함수
        def absolute_value(val):
            total = sum(sizes)
            absolute = int(round(val / 100.0 * total))
            return absolute

        # 파이 차트 생성
        fig, ax = plt.subplots()
        # ax.pie(sizes, labels=labels, autopct=absolute_value, startangle=90)
        ax.pie(sizes, labels=labels, autopct=absolute_value, startangle=90, textprops={'fontsize': 5})
        ax.axis('equal')  # 원형 차트를 위한 설정

        # 차트 저장
        plt.savefig('result_pie.png')
        
    def __save_bar_graph(self, events:list):
        font_size = 8
        tick_font_size = 5
        
        # 데이터 추출
        labels = [event['type'] for event in events]
        counts = [event['count'] for event in events]

        # # 차트 크기 설정 (너비, 높이)
        fig, ax = plt.subplots(figsize=(20, len(labels)))

        # 가로 막대 그래프 생성
        y_positions = range(len(labels))  # 레이블 위치 설정
        fig, ax = plt.subplots()
        ax.barh(y_positions, counts, align='center')
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels, fontsize=font_size)  # 레이블의 폰트 크기 설정
        ax.invert_yaxis()  # 레이블을 위에서 아래로 읽기
        ax.set_xlabel('Counts', fontsize=font_size)  # x축 레이블 폰트 크기 설정
        ax.set_title('Event Detection Results', fontsize=font_size)  # 제목의 폰트 크기 설정

		# x축 눈금 간격 설정
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        
        # x축 및 y축 눈금 폰트 크기 설정 ##
        ax.tick_params(axis='x', labelsize=tick_font_size)

        # 여백 조절
        plt.subplots_adjust(left=0.45)  # 왼쪽 여백 증가

        # 차트 저장
        plt.savefig('result_bar.png')
    
    def save_result(self):
        if DEBUG:
            print("[save_result]") # test
            for type_name in self.find_anomaly:
                print(f"{type_name})")
                for msg in self.find_anomaly[type_name]:
                    print(f"Start: {msg[0][0]}\nEnd: {msg[-1][-1]}")
                print("")
        
        print("[+] Save Result...")
        if (not os.path.isdir(self.detection_dir_path)):
            os.mkdir(self.detection_dir_path) # 검출 저장용 디렉토리
        
        all_events_cols = ["CAN_Message_No", "Time_Offset/msec", "Type", "ID", "Data_Length", 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'desc']
        cols = ["Type_Name", "Description", "Anomaly_No", "Start/End", "Duration/sec", "CAN_Message_No", "Time_Offset/msec", "Type", "ID", "Data_Length", 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight']
        result = []
        events_count_info = []
        for type_name in self.find_anomaly:
            anomaly_no = 0
            all_events = []
            description = self.__get_desc(type_name)
            # print(description) # test
            for msg in self.find_anomaly[type_name]:
                # 모든 이벤트 메시지 저장 (검출 제출용)
                for ms in msg:
                    for m in ms:
                        tmp = list(m) # list copy
                        tmp.append(description)
                        all_events.append(tmp)
                df_all = pd.DataFrame(all_events, columns=all_events_cols)
                file_name = f"{type_name}_all_events.csv"
                file_path = os.path.join(self.detection_dir_path, file_name)
                df_all.to_csv(file_path, index=False, encoding='cp949')
                
                # 연속된 이벤트 메시지 단위로 저장 (종합)
                duration = (float(msg[-1][-1][self.TIME_OFFSET_IDX]) - float(msg[0][0][self.TIME_OFFSET_IDX])) / 1000 # 진행시간 # 초 단위로 변경
                start_msg = [
                    type_name,
                    description,
                    anomaly_no, 
                    "Start",
                    duration,
                    msg[0][0][self.NO_IDX], 
                    msg[0][0][self.TIME_OFFSET_IDX], 
                    msg[0][0][self.TYPE_IDX], 
                    msg[0][0][self.ID_IDX], 
                    msg[0][0][self.DATA_LENGTH_IDX], 
                    msg[0][0][self.BYTE1_IDX], 
                    msg[0][0][self.BYTE2_IDX],
                    msg[0][0][self.BYTE3_IDX],
                    msg[0][0][self.BYTE4_IDX],
                    msg[0][0][self.BYTE5_IDX],
                    msg[0][0][self.BYTE6_IDX],
                    msg[0][0][self.BYTE7_IDX],
                    msg[0][0][self.BYTE8_IDX],
                ]
                end_msg = [
                    type_name, 
                    description,
                    anomaly_no,
                    "End", 
                    duration,
                    msg[-1][-1][self.NO_IDX], 
                    msg[-1][-1][self.TIME_OFFSET_IDX], 
                    msg[-1][-1][self.TYPE_IDX], 
                    msg[-1][-1][self.ID_IDX], 
                    msg[-1][-1][self.DATA_LENGTH_IDX], 
                    msg[-1][-1][self.BYTE1_IDX], 
                    msg[-1][-1][self.BYTE2_IDX],
                    msg[-1][-1][self.BYTE3_IDX],
                    msg[-1][-1][self.BYTE4_IDX],
                    msg[-1][-1][self.BYTE5_IDX],
                    msg[-1][-1][self.BYTE6_IDX],
                    msg[-1][-1][self.BYTE7_IDX],
                    msg[-1][-1][self.BYTE8_IDX],
                ]
                result.append(start_msg)
                result.append(end_msg)
                anomaly_no += 1
            events_count_info.append({
                'type':type_name,
                'count':anomaly_no,
                'total_count': len(all_events)
            })

        df = pd.DataFrame(result, columns=cols)
        df.to_csv("result.csv", index=False, encoding='cp949')
        
        cols = ["Type_Name", "Count","Total_Count"]
        count_result = [[x['type'], x['count'], x['total_count']] for x in events_count_info]
        count_df = pd.DataFrame(count_result, columns=cols)
        count_df.to_csv("count_result.csv", index=False, encoding='cp949')
        
        # draw graph
        # self.__save_pie_graph(events_count_info)
        self.__save_bar_graph(events_count_info)
        print("[+] Done!")
        
    def print_warn(self, func_info:dict):
        """
        워닝 문구 출력 함수
        """
        msg = self.CAN_msgs_stack[func_info['type']][-func_info['element_size']:]
        print(f"[+] Warnning : {func_info['type']}")
        print(f"  (+) Description : {func_info['desc']}")
        
        # 로그 출력
        for i, m in enumerate(msg):
            print(f'  (msg {i+1})', "\t".join(m))
            
        time_offset = self.__calc_time_offset(func_info)
        # print(f"  (+) Time Offset: {time_offset}")

    def check(self, can_msg:str) -> bool:
        can_msg = can_msg.split()
                
        if len(can_msg) == 0:
            return False
        
        try:
            data_length = int(can_msg[self.DATA_LENGTH_IDX], 16)
        except ValueError: # ValueError: invalid literal for int() with base 10: 'Data_Length'
            return False
        if data_length != 8:
            can_msg += ['-1' for x in range(8-data_length)]
        
        if (len(can_msg) == 0):
            return
        
        for func_info in self.chk_func_info:
            if (func_info['func'](can_msg)):
                if ((len(self.CAN_msgs_stack[func_info['type']]) % func_info['element_size']) != 0):
                    print(f"[!] Wrong! : {func_info['type']} stack size % func_info['element_size'] != 0")
                    exit(0)
                self.print_warn(func_info)
                if DEBUG:
                    print(len(self.CAN_msgs_stack[func_info['type']]))
                    print(self.CAN_msgs_stack[func_info['type']][:5])
            
    def __chk_condition(self, type:str, ID:str, Byte_IDX:int, Byte_value:str) -> bool:
        if ((len(self.CAN_msgs_stack[type]) > 0) and
            (self.CAN_msgs_stack[type][-1][self.ID_IDX] == ID) and
            (self.CAN_msgs_stack[type][-1][Byte_IDX] == Byte_value)):
            return True
        return False
            
    def __chk_seatbelt_off_engine_on(self, can_msg:list):
        '''
        안전벨트를 풀고 엔진 on
        '''
        if (can_msg[self.ID_IDX] != "0018"):
            return False
        
        if ((can_msg[self.BYTE4_IDX] == "70") and 
            (can_msg[self.BYTE8_IDX] == "10")):
            if ("chk_seatbelt_off_engine_on" not in self.CAN_msgs_stack):
                self.CAN_msgs_stack["chk_seatbelt_off_engine_on"] = []
            self.CAN_msgs_stack["chk_seatbelt_off_engine_on"].append(can_msg)
            return True
        
        return False
        
    def __chk_gear_R_seatbelt_off(self, can_msg:list):
        """
        안전벨트를 풀고 후진
        """         
        if ("chk_gear_R_seatbelt_off" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_R_seatbelt_off"] = []      
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if (can_msg[self.BYTE8_IDX] == '10'):
                    if (self.__chk_condition("chk_gear_R_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                        return False
                    self.CAN_msgs_stack["chk_gear_R_seatbelt_off"].append(can_msg)
                else:
                    # 안전벨트를 하는 경우 -> 스택에서 제거
                    if (self.__chk_condition("chk_gear_R_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                        if (can_msg[self.BYTE8_IDX] == "00"):
                            self.CAN_msgs_stack["chk_gear_R_seatbelt_off"].pop(-1)
            case ("043F"):
                if (self.__chk_condition("chk_gear_R_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                    if (can_msg[self.BYTE2_IDX] == '47'):
                        self.CAN_msgs_stack["chk_gear_R_seatbelt_off"].append(can_msg)
                        return True
        return False
        
    def __chk_gear_D_seatbelt_off(self, can_msg:list):
        '''
        안전벨트를 풀고 전진
        '''    
        if ("chk_gear_D_seatbelt_off" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_D_seatbelt_off"] = []      
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if (can_msg[self.BYTE8_IDX] == '10'):
                    if (self.__chk_condition("chk_gear_D_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                        return False
                    self.CAN_msgs_stack["chk_gear_D_seatbelt_off"].append(can_msg)
                else:
                    # 안전벨트를 하는 경우 -> 스택에서 제거
                    if (self.__chk_condition("chk_gear_D_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                        if (can_msg[self.BYTE8_IDX] == "00"):
                            self.CAN_msgs_stack["chk_gear_D_seatbelt_off"].pop(-1)
            case ("043F"):
                if (self.__chk_condition("chk_gear_D_seatbelt_off", "0018", self.BYTE8_IDX, "10")):
                    if (can_msg[self.BYTE2_IDX] == '45'):
                        self.CAN_msgs_stack["chk_gear_D_seatbelt_off"].append(can_msg)
                        return True
        return False
        
    def __chk_engine_on_handbreak_off_seatbelt_off(self, can_msg:list):
        '''
        안전벨트를 풀고 엔진 on, 핸드 브레이크 off
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE4_IDX], can_msg[self.BYTE8_IDX]):
            case ('0018', '60' , '10'):
                if ("chk_engine_on_handbreak_off_seatbelt_off" not in self.CAN_msgs_stack):
                    self.CAN_msgs_stack["chk_engine_on_handbreak_off_seatbelt_off"] = []
                self.CAN_msgs_stack["chk_engine_on_handbreak_off_seatbelt_off"].append(can_msg)
                return True
        return False
    
    def __chk_gear_P_push_accelerator(self, can_msg:list):
        '''
        P기어 중에 엑셀을 밟음. (차량 손상)
        '''
        if ("chk_gear_P_push_accelerator" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_P_push_accelerator"] = []      
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '40'):
                    if (self.__chk_condition("chk_gear_P_push_accelerator", "043F", self.BYTE2_IDX, "40")):
                        return False
                    self.CAN_msgs_stack["chk_gear_P_push_accelerator"].append(can_msg)
                else:
                    # 기어가 다른 것으로 바뀌는 경우 == 정상 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_P_push_accelerator", "043F", self.BYTE2_IDX, "40")):
                        if (can_msg[self.BYTE2_IDX] != "40"):
                            self.CAN_msgs_stack["chk_gear_P_push_accelerator"].pop(-1)
            case ("0316"):
                if (self.__chk_condition("chk_gear_P_push_accelerator", "043F", self.BYTE2_IDX, "40")):
                    if (int(can_msg[self.BYTE4_IDX], 16) > 0xe):
                        self.CAN_msgs_stack["chk_gear_P_push_accelerator"].append(can_msg)
                        return True
        return False
    
    def __chk_gear_P_inc_speed(self, can_msg:list):
        '''
        P기어 중에 속도가 증가. (잠재적 시스템 손상)
        '''
        if ("chk_gear_P_inc_speed" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_P_inc_speed"] = []
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '40'):
                    if (self.__chk_condition("chk_gear_P_inc_speed", "043F", self.BYTE2_IDX, "40")):
                        return False
                    self.CAN_msgs_stack["chk_gear_P_inc_speed"].append(can_msg)
                else:
                    # 기어가 P에서 D혹은 R로 바뀌는 경우 == 정상 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_P_inc_speed", "043F", self.BYTE2_IDX, "40")):
                            if (can_msg[self.BYTE2_IDX] == "45") or (can_msg[self.BYTE2_IDX] == "47"):
                                self.CAN_msgs_stack["chk_gear_P_inc_speed"].pop(-1)
            case ("0440"):
                if (self.__chk_condition("chk_gear_P_inc_speed", "043F", self.BYTE2_IDX, "40")):
                    if (can_msg[self.BYTE3_IDX] != '00'):
                        self.CAN_msgs_stack["chk_gear_P_inc_speed"].append(can_msg)
                        return True
        return False
            
    def __chk_gear_N_push_accelerator(self, can_msg:list):
        '''
        N기어 중에 엑셀을 밟음. (차량 손상)
        '''
        if ("chk_gear_N_push_accelerator" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_N_push_accelerator"] = []
        
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '46'):
                    if (self.__chk_condition("chk_gear_N_push_accelerator", "043F", self.BYTE2_IDX, "46")):
                        return False
                    self.CAN_msgs_stack["chk_gear_N_push_accelerator"].append(can_msg)
                else:
                    # 기어가 P에서 D혹은 R로 바뀌는 경우 == 정상 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_N_push_accelerator", "043F", self.BYTE2_IDX, "46")):
                            if (can_msg[self.BYTE2_IDX] == "45") or (can_msg[self.BYTE2_IDX] == "47"):
                                self.CAN_msgs_stack["chk_gear_N_push_accelerator"].pop(-1)
            case ("0316"):
                if (self.__chk_condition("chk_gear_N_push_accelerator", "043F", self.BYTE2_IDX, "46")):
                    if (can_msg[self.BYTE4_IDX] != '00'):
                        self.CAN_msgs_stack["chk_gear_N_push_accelerator"].append(can_msg)
                        return True
        return False
        
    def __chk_gear_D_handbreak_on(self, can_msg:list):
        '''
        D기어 중에 핸드 브레이크를 끄지 않음.
        '''
        if ("chk_gear_D_handbreak_on" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_D_handbreak_on"] = []
                        
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '45'):
                    if (self.__chk_condition("chk_gear_D_handbreak_on", "043F", self.BYTE2_IDX, "45")):
                        return False
                    self.CAN_msgs_stack["chk_gear_D_handbreak_on"].append(can_msg)
                else:
                    # 기어가 D에서 N혹은 P로 바뀌면 괜찮음 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_D_handbreak_on", "043F", self.BYTE2_IDX, "45")):
                            if (can_msg[self.BYTE2_IDX] == "46") or (can_msg[self.BYTE2_IDX] == "40"):
                                self.CAN_msgs_stack["chk_gear_D_handbreak_on"].pop(-1)
            case ("0018"):
                if (self.__chk_condition("chk_gear_D_handbreak_on", "043F", self.BYTE2_IDX, "45")):
                    if (can_msg[self.BYTE4_IDX] != '60'):
                        self.CAN_msgs_stack["chk_gear_D_handbreak_on"].append(can_msg)
                        return True
        return False
    
    def __chk_gear_R_handbreak_on(self, can_msg:list):
        '''
        R기어 중에 핸드 브레이크를 끄지 않음.
        '''
        if ("chk_gear_R_handbreak_on" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_R_handbreak_on"] = []
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '47'):
                    if (self.__chk_condition("chk_gear_R_handbreak_on", "043F", self.BYTE2_IDX, "47")):
                        return False
                    self.CAN_msgs_stack["chk_gear_R_handbreak_on"].append(can_msg)
                else:
                    # 기어가 R에서 N혹은 P로 바뀌면 괜찮음 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_R_handbreak_on", "043F", self.BYTE2_IDX, "47")):
                        if (can_msg[self.BYTE2_IDX] == "40") or (can_msg[self.BYTE2_IDX] == "46"):
                            self.CAN_msgs_stack["chk_gear_R_handbreak_on"].pop(-1)
            case ("0018"):
                if (self.__chk_condition("chk_gear_R_handbreak_on", "043F", self.BYTE2_IDX, "47")):
                    if (can_msg[self.BYTE4_IDX] != '60'):
                        self.CAN_msgs_stack["chk_gear_R_handbreak_on"].append(can_msg)
                        return True
        return False
    
    def __chk_gear_R_engine_off(self, can_msg:list):
        '''
        R기어 중에 엔진을 끔 (기어 손상)
        '''
        if ("chk_gear_R_engine_off" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_R_engine_off"] = []
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '47'):
                    if (self.__chk_condition("chk_gear_R_engine_off", "043F", self.BYTE2_IDX, "47")):
                        return False
                    self.CAN_msgs_stack["chk_gear_R_engine_off"].append(can_msg)
                else:
                    # 기어가 R에서 N혹은 P로 바뀌면 괜찮음 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_R_engine_off", "043F", self.BYTE2_IDX, "47")):
                            if (can_msg[self.BYTE2_IDX] == "40") or (can_msg[self.BYTE2_IDX] == "46"):
                                self.CAN_msgs_stack["chk_gear_R_engine_off"].pop(-1)
            case ("0018"):
                if (self.__chk_condition("chk_gear_R_engine_off", "043F", self.BYTE2_IDX, "47")):
                    if (can_msg[self.BYTE4_IDX] == '10'):
                        self.CAN_msgs_stack["chk_gear_R_engine_off"].append(can_msg)
                        return True
        return False
    
    def __chk_gear_D_engine_off(self, can_msg:list):
        '''
        D기어중에 엔진을 끔.
        '''
        if ("chk_gear_D_engine_off" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_D_engine_off"] = []
        match (can_msg[self.ID_IDX]):
            case ("043F"):
                if (can_msg[self.BYTE2_IDX] == '45'):
                    if (self.__chk_condition("chk_gear_D_engine_off", "043F", self.BYTE2_IDX, "45")):
                        return False
                    self.CAN_msgs_stack["chk_gear_D_engine_off"].append(can_msg)
                else:
                    # 기어가 D에서 N혹은 P로 바뀌면 괜찮음 => 스택에서 제거
                    if (self.__chk_condition("chk_gear_D_engine_off", "043F", self.BYTE2_IDX, "45")):
                            if (can_msg[self.BYTE2_IDX] == "40") or (can_msg[self.BYTE2_IDX] == "46"):
                                self.CAN_msgs_stack["chk_gear_D_engine_off"].pop(-1)
            case ("0018"):
                if (self.__chk_condition("chk_gear_D_engine_off", "043F", self.BYTE2_IDX, "45")):
                    if (can_msg[self.BYTE4_IDX] == '10'):
                        self.CAN_msgs_stack["chk_gear_D_engine_off"].append(can_msg)
                        return True
        return False
    
    def __chk_engine_off_gear_D(self, can_msg:list):
        '''
        엔진이 꺼진 상태에서 D기어로 올림
        '''
        if ("chk_engine_off_gear_D" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_engine_off_gear_D"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if (can_msg[self.BYTE4_IDX] == '10'):
                    if (self.__chk_condition("chk_engine_off_gear_D", "0018", self.BYTE4_IDX, "10")):
                        return False
                    self.CAN_msgs_stack["chk_engine_off_gear_D"].append(can_msg)
                else:
                    # 엔진 다시 켜지면 정상으로 간주 => 스택에서 제거
                    if (self.__chk_condition("chk_engine_off_gear_D", "0018", self.BYTE4_IDX, "10")):
                            if (can_msg[self.BYTE4_IDX] == "60"):
                                self.CAN_msgs_stack["chk_engine_off_gear_D"].pop(-1)
            case ("043F"):
                if (self.__chk_condition("chk_engine_off_gear_D", "0018", self.BYTE4_IDX, "10")):
                    if (can_msg[self.BYTE2_IDX] == '45'):
                        self.CAN_msgs_stack["chk_engine_off_gear_D"].append(can_msg)
                        return True
        return False
        
    def __chk_driver_door_open_gear_D(self, can_msg:list):
        '''
        운전자 문이 열린 상태에서 D기어로 올림
        '''
        if ("chk_driver_door_open_gear_D" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_driver_door_open_gear_D"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '10') or # day 
                    (can_msg[self.BYTE1_IDX] == '30')):  # night
                    if ((self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "10")) or 
                        (self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "30"))):
                        return False
                    self.CAN_msgs_stack["chk_driver_door_open_gear_D"].append(can_msg)
                else:
                    # 문이 다시 닫히면 정상 => 스택에서 제거
                    if ((self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "10")) or 
                        (self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "30"))):
                        if (can_msg[self.BYTE1_IDX] == "00"):
                            self.CAN_msgs_stack["chk_driver_door_open_gear_D"].pop(-1)
            case ("043F"):
                if ((self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "10")) or 
                    (self.__chk_condition("chk_driver_door_open_gear_D", "0018", self.BYTE1_IDX, "30"))):
                    if (can_msg[self.BYTE2_IDX] == '45'):
                        self.CAN_msgs_stack["chk_driver_door_open_gear_D"].append(can_msg)
                        return True
        return False
                
    def __chk_driver_door_open_gear_R(self, can_msg:list):
        '''
        운전자 문이 열린 상태에서 R기어로 올림
        '''
        if ("chk_driver_door_open_gear_R" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_driver_door_open_gear_R"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '10') or # day 
                    (can_msg[self.BYTE1_IDX] == '30')):  # night
                    if ((self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "10")) or 
                        (self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "30"))):
                        return False
                    self.CAN_msgs_stack["chk_driver_door_open_gear_R"].append(can_msg)
                else:
                    # 문이 다시 닫히면 정상 => 스택에서 제거
                    if ((self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "10")) or 
                        (self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "30"))):
                        if (can_msg[self.BYTE1_IDX] == "00"):
                            self.CAN_msgs_stack["chk_driver_door_open_gear_R"].pop(-1)
            case ("043F"):
                if ((self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "10")) or 
                    (self.__chk_condition("chk_driver_door_open_gear_R", "0018", self.BYTE1_IDX, "30"))):
                    if (can_msg[self.BYTE2_IDX] == '47'):
                        self.CAN_msgs_stack["chk_driver_door_open_gear_R"].append(can_msg)
                        return True
        return False
    
    # def __chk_high_low_beam(self, can_msg:list): # 삭제
    #     '''
    #     high, low 모두 키고 운행
    #     '''
    #     match (can_msg[self.ID_IDX], can_msg[self.BYTE3_IDX], can_msg[self.BYTE5_IDX]):
    #         case ("0018", "01", "01"):
    #             if ("chk_high_low_beam" not in self.CAN_msgs_stack):
    #                 self.CAN_msgs_stack["chk_high_low_beam"] = []
    #             self.CAN_msgs_stack["chk_high_low_beam"].append(can_msg)
    #             return True
    #     return False
    
    def __chk_high_middle_low_beam(self, can_msg:list):
        '''
        high, middle, low 모두 키고 운행
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE2_IDX], can_msg[self.BYTE3_IDX], can_msg[self.BYTE5_IDX]):
            case ("0018", "02", "01", "01"):
                if ("chk_high_middle_low_beam" not in self.CAN_msgs_stack):
                    self.CAN_msgs_stack["chk_high_middle_low_beam"] = []
                self.CAN_msgs_stack["chk_high_middle_low_beam"].append(can_msg)
                return True
        return False
    
    def __chk_middle_fog_low(self, can_msg:list):
        '''
        middle, fog, low 모두 키고 운행.
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE2_IDX], can_msg[self.BYTE3_IDX], can_msg[self.BYTE5_IDX]):
            case ("0018", "02", "03", "01"):
                if ("chk_middle_fog_low" not in self.CAN_msgs_stack):
                    self.CAN_msgs_stack["chk_middle_fog_low"] = []
                self.CAN_msgs_stack["chk_middle_fog_low"].append(can_msg)
                return True
        return False
    
    # def __chk_push_accelerator_not_inc_speed(self, can_msg:list): # 삭제
    #     '''
    #     엑셀을 밟았는데(rpm이 올라갔는데) 속도가 오르지 않음
    #     '''
    #     if ("chk_push_accelerator_not_inc_speed" not in self.CAN_msgs_stack):
    #         self.CAN_msgs_stack["chk_push_accelerator_not_inc_speed"] = []
    #     match (can_msg[self.ID_IDX]):
    #         case ("043F"):
    #             if (can_msg[self.BYTE2_IDX] == '45'):
    #                 if ((self.__chk_condition("chk_push_accelerator_not_inc_speed", "043F", self.BYTE2_IDX, "45")) or 
    #                     (self.__chk_condition("chk_push_accelerator_not_inc_speed", "0316", self.BYTE4_IDX, "0E"))):
    #                     return False
    #                 self.CAN_msgs_stack["chk_push_accelerator_not_inc_speed"].append(can_msg)
    #         case ("0316"):
    #             if (can_msg[self.BYTE4_IDX] == '0E'):
    #                 if ((self.__chk_condition("chk_push_accelerator_not_inc_speed", "043F", self.BYTE2_IDX, "45")) or 
    #                     (self.__chk_condition("chk_push_accelerator_not_inc_speed", "0316", self.BYTE4_IDX, "0E"))):
    #                     return False
    #                 self.CAN_msgs_stack["chk_push_accelerator_not_inc_speed"].append(can_msg)
    #             else:
    #                 if (self.__chk_condition("chk_push_accelerator_not_inc_speed", "0316", self.BYTE4_IDX, "0E")):
    #                     if (can_msg[self.BYTE3_IDX] != '01'):
    #                         self.CAN_msgs_stack["chk_push_accelerator_not_inc_speed"].pop(-1)
    #         case ("0440"):
    #             if (self.__chk_condition("chk_push_accelerator_not_inc_speed", "0316", self.BYTE4_IDX, "0E")):
    #                 if (can_msg[self.BYTE3_IDX] == '01'):
    #                     self.CAN_msgs_stack["chk_push_accelerator_not_inc_speed"].append(can_msg)
    #                     return True
    #     return False           
         
    def __chk_emergency_light_on_high_speed(self, can_msg:list):
        '''
        비상등 키고 속도 증가
        '''
        if ("chk_emergency_light_on_high_speed" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_emergency_light_on_high_speed"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if (can_msg[self.BYTE6_IDX] == '60'):
                    if (self.__chk_condition("chk_emergency_light_on_high_speed", "0018", self.BYTE6_IDX, "60")):
                        return False
                    self.CAN_msgs_stack["chk_emergency_light_on_high_speed"].append(can_msg)
                else:
                    # 비상등이 꺼지면 정상
                    if (self.__chk_condition("chk_emergency_light_on_high_speed", "0018", self.BYTE6_IDX, "60")):
                        if (int(can_msg[self.BYTE3_IDX], 16) == 0): # 비상등 꺼짐
                            self.CAN_msgs_stack["chk_emergency_light_on_high_speed"].pop(-1)
                            return False
            case ("0440"):
                if (self.__chk_condition("chk_emergency_light_on_high_speed", "0018", self.BYTE6_IDX, "60")):
                    if (int(can_msg[self.BYTE3_IDX], 16) > 0x28): # 속도 임계치
                        self.CAN_msgs_stack["chk_emergency_light_on_high_speed"].append(can_msg)
                        return True
        return False
    
    def __chk_sub_door_open_gear_D(self, can_msg:list):
        '''
        문이 열린 상태에서 D기어로 올림
        '''
        if ("chk_sub_door_open_gear_D" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_sub_door_open_gear_D"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '80') or # day 
                    (can_msg[self.BYTE1_IDX] == 'A0')):  # night
                    if (self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "80") or 
                        self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "A0")):
                        return False
                    self.CAN_msgs_stack["chk_sub_door_open_gear_D"].append(can_msg)
                else:
                    # 비상등이 꺼지면 정상
                    if (self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "80") or 
                        self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "A0")):
                        if (can_msg[self.BYTE1_IDX] == '00'): # 문 닫음
                            self.CAN_msgs_stack["chk_sub_door_open_gear_D"].pop(-1)
                            return False
            case ("043F"):
                if (self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "80") or 
                    self.__chk_condition("chk_sub_door_open_gear_D", "0018", self.BYTE1_IDX, "A0")):
                    if (can_msg[self.BYTE2_IDX] == '45'):
                        self.CAN_msgs_stack["chk_sub_door_open_gear_D"].append(can_msg)
                        return True
        return False
    
    def __chk_sub_door_open_gear_R(self, can_msg:list):
        '''
        문이 열린 상태에서 R기어로 올림
        '''
        if ("chk_sub_door_open_gear_R" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_sub_door_open_gear_R"] = []
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '80') or # day 
                    (can_msg[self.BYTE1_IDX] == 'A0')):  # night
                    if (self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "80") or 
                        self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "A0")):
                        return False
                    self.CAN_msgs_stack["chk_sub_door_open_gear_R"].append(can_msg)
                else:
                    # 비상등이 꺼지면 정상
                    if (self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "80") or 
                        self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "A0")):
                        if (can_msg[self.BYTE1_IDX] == '00'): # 문 닫음
                            self.CAN_msgs_stack["chk_sub_door_open_gear_R"].pop(-1)
                            return False
            case ("043F"):
                if (self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "80") or 
                    self.__chk_condition("chk_sub_door_open_gear_R", "0018", self.BYTE1_IDX, "A0")):
                    if (can_msg[self.BYTE2_IDX] == '47'):
                        self.CAN_msgs_stack["chk_sub_door_open_gear_R"].append(can_msg)
                        return True
        return False
    
    def __chk_seatbelt_off_engine_on_2(self, can_msg:list):
        '''
        안전벨트를 풀고 엔진 on
        '''
        if (can_msg[self.ID_IDX] != "0018"):
            return False
        
        if ((can_msg[self.BYTE4_IDX] == "70") and 
            ((can_msg[self.BYTE1_IDX] == "08") or
             (can_msg[self.BYTE1_IDX] == "28"))
            ):
            if ("chk_seatbelt_off_engine_on_2" not in self.CAN_msgs_stack):
                self.CAN_msgs_stack["chk_seatbelt_off_engine_on_2"] = []
            self.CAN_msgs_stack["chk_seatbelt_off_engine_on_2"].append(can_msg)
            return True
        
        return False
    
    def __chk_gear_R_seatbelt_off_2(self, can_msg:list):
        """
        안전벨트를 풀고 후진 2
        """         
        if ("chk_gear_R_seatbelt_off_2" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_R_seatbelt_off_2"] = []      
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '08') or # day 
                    (can_msg[self.BYTE1_IDX] == '28')):  # night
                    if ((self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                        (self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                        return False
                    self.CAN_msgs_stack["chk_gear_R_seatbelt_off_2"].append(can_msg)
                else:
                    # 안전벨트를 하는 경우 -> 스택에서 제거
                    if ((self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                        (self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                        if (can_msg[self.BYTE1_IDX] != "08"):
                            self.CAN_msgs_stack["chk_gear_R_seatbelt_off_2"].pop(-1)
            case ("043F"):
                if ((self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                    (self.__chk_condition("chk_gear_R_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                    if (can_msg[self.BYTE2_IDX] == '47'):
                        self.CAN_msgs_stack["chk_gear_R_seatbelt_off_2"].append(can_msg)
                        return True
        return False
        
    def __chk_gear_D_seatbelt_off_2(self, can_msg:list):
        '''
        안전벨트를 풀고 전진 2
        '''    
        if ("chk_gear_D_seatbelt_off_2" not in self.CAN_msgs_stack):
            self.CAN_msgs_stack["chk_gear_D_seatbelt_off_2"] = []      
        match (can_msg[self.ID_IDX]):
            case ("0018"):
                if ((can_msg[self.BYTE1_IDX] == '08') or # day 
                    (can_msg[self.BYTE1_IDX] == '28')):  # night
                    if ((self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                        (self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                        return False
                    self.CAN_msgs_stack["chk_gear_D_seatbelt_off_2"].append(can_msg)
                else:
                    # 안전벨트를 하는 경우 -> 스택에서 제거
                    if ((self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                        (self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                        if (can_msg[self.BYTE1_IDX] != "08"):
                            self.CAN_msgs_stack["chk_gear_D_seatbelt_off_2"].pop(-1)
            case ("043F"):
                if ((self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "08")) or
                    (self.__chk_condition("chk_gear_D_seatbelt_off_2", "0018", self.BYTE1_IDX, "28"))):
                    if (can_msg[self.BYTE2_IDX] == '45'):
                        self.CAN_msgs_stack["chk_gear_D_seatbelt_off_2"].append(can_msg)
                        return True
        return False

    def __chk_engine_on_handbreak_off_seatbelt_off_2(self, can_msg:list):
        '''
        안전벨트를 풀고 엔진 on, 핸드 브레이크 off 2
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE4_IDX]):
            case ('0018', '60'):
                if ((can_msg[self.BYTE1_IDX] == '08') or
                    (can_msg[self.BYTE1_IDX] == '28')):
                    if ("chk_engine_on_handbreak_off_seatbelt_off_2" not in self.CAN_msgs_stack):
                        self.CAN_msgs_stack["chk_engine_on_handbreak_off_seatbelt_off_2"] = []
                    self.CAN_msgs_stack["chk_engine_on_handbreak_off_seatbelt_off_2"].append(can_msg)
                    return True
        return False

    def __chk_electricity_on_high_beam_on(self, can_msg:list):
        '''
        전기만 켜진 상태에서 상향등 사용 (배터리 수명 단축 및 주변 환경 방해)
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE3_IDX]):
            case ("0018", "01"):
                if ((can_msg[self.BYTE4_IDX] == '40') or
                    (can_msg[self.BYTE4_IDX] == '50')):
                    if ("chk_electricity_on_high_beam_on" not in self.CAN_msgs_stack):
                        self.CAN_msgs_stack["chk_electricity_on_high_beam_on"] = []
                    self.CAN_msgs_stack["chk_electricity_on_high_beam_on"].append(can_msg)
                    return True
        return False
    
    def __chk_electricity_on_fog_beam_on(self, can_msg:list):
        '''
        전기만 켜진 상태에서 안개등 사용 (배터리 수명 단축 및 주변 환경 방해)
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE3_IDX]):
            case ("0018", "03"):
                if ((can_msg[self.BYTE4_IDX] == '40') or
                    (can_msg[self.BYTE4_IDX] == '50')):
                    if ("chk_electricity_on_fog_beam_on" not in self.CAN_msgs_stack):
                        self.CAN_msgs_stack["chk_electricity_on_fog_beam_on"] = []
                    self.CAN_msgs_stack["chk_electricity_on_fog_beam_on"].append(can_msg)
                    return True
        return False

    def __chk_day_high_beam_on(self, can_msg:list):
        '''
        낮에 상향등 사용 (배터리 수명 단축 및 주변 환경 방해)
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE1_IDX], can_msg[self.BYTE3_IDX]):
            case ("0018", "00", '01'):
                if ("chk_day_high_beam_on" not in self.CAN_msgs_stack):
                    self.CAN_msgs_stack["chk_day_high_beam_on"] = []
                self.CAN_msgs_stack["chk_day_high_beam_on"].append(can_msg)
                return True
        return False

    def __chk_day_fog_beam_on(self, can_msg:list):
        ''' 
        낮에 안개등 사용 (배터리 수명 단축 및 주변 환경 방해)
        '''
        match (can_msg[self.ID_IDX], can_msg[self.BYTE1_IDX], can_msg[self.BYTE3_IDX]):
            case ("0018", "00", '03'):
                if ("chk_day_fog_beam_on" not in self.CAN_msgs_stack):
                    self.CAN_msgs_stack["chk_day_fog_beam_on"] = []
                self.CAN_msgs_stack["chk_day_fog_beam_on"].append(can_msg)
                return True
        return False


if __name__ == "__main__":
    dp = Dispatcher()
    data = None
    # file_path = './backup/result0.txt'
    file_path = "../해커톤 비정상 이벤트-CCAN.txt"
    with open(file_path, 'r') as fp:
        data = fp.read().split("\n")
    for line in data:
        dp.check(line)
    dp.get_resuit()
    dp.save_result()
    