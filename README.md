# CANAD

## What is
CANAD는 CCAN Anomaly Detector 모듈입니다.
</br></br>
총 27개의 이상 탐지 규칙을 정의 하였고 실시간 이상 탐지 분석이 가능합니다.
</br></br>
실시간 탐지 종료시, 수집된 이상 탐지 이벤트를 저장합니다.
</br></br>
2023 LISA HACKATHON (CCAN 이상 탐지 분석 도구 개발 해커톤)에 참가하여 개발하였습니다.

## Construction
```
[파일 구성]
- result.csv : 모든 이벤트에 대한 종합 결과 저장
- count_result.csv : 모든 이벤트에 대한 발생 횟수 결과 저장
- result_bar.png : 각 이벤트에 대한 발생 횟수를 저장한 막대 그래프
- detection 디렉토리 : 검출 결과 저장 디렉토리(특정 이벤트에 대한 모든 CAN 메시지 로그가 이벤트 별로 csv 파일로 저장되어있음)

[파일 세부]
+ result.csv (결과를 종합해서 저장한 파일, 연속된 이벤트 단위로 결과가 저장됨)
 - Type_Name        : 이벤트 종류 키워드
 - Description      : 이벤트에 대한 설명
 - Anomaly_No       : 연속된 이벤트를 구분하기 위한 넘버 (연속된 이벤트라면 같은 넘버를 갖음)
 - Start/End        : 이벤트의 시작과 끝을 구분짓는 값
 - Duration/sec     : 이벤트가 진행된 시간 (초 단위)
 - CAN_Message_No   : 수집된 CAN 메시지 넘버
 - Time_Offset/msec : 분석 시작 시점으로부터 수집된 시간차 (밀리 세컨드 단위)
 - Type             : 
 - ID               : CAN ID
 - Data_Length      : CAN 메시지 데이터의 길이
 - One ~ Eight      : CAN 메시지 데이터

+ count_result.csv
 - Type_Name        : 이벤트 종류 키워드
 - Count            : 이벤트 발생 횟수 (연속된 이벤트 단위)
 - Total_Count      : 이벤트 발생 횟수 (이벤트 검출 횟수)

+ detection 디렉토리의 각 파일들
 + 파일명 규칙: {이벤트 종류 키워드}_all_events.csv
 - CAN_Message_No   : 수집된 CAN 메시지 넘버
 - Time_Offset/msec : 분석 시작 시점으로부터 수집된 시간차
 - Type             : 
 - ID               : CAN ID
 - Data_Length      : CAN 메시지 데이터의 길이
 - One ~ Eight      : CAN 메시지 데이터
 - desc             : 이벤트에 대한 설명
```

## Refer
PCAN 드라이버를 사용하여 CCAN 메시지를 읽어오는 main.py의 대부분의 코드는 [ARK_CAN](https://github.com/ARKPROJECT2023/ARK_CAN/blob/main/READ_CH1%20-%20C.py)의 코드를 베이스로 사용하였음을 알립니다. 

## Contributors
- OZ1NG  (홍택균) : 팀장, 개발
- lmxx   (임종준) : 이상 탐지 규칙 정의, CCAN 메시지 분석
- K0n9   (이정주) : 이상 탐지 규칙 정의, CCAN 메시지 분석
