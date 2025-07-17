# 우리동네 명장면
<br/>

## 0. 프로젝트 개요


"TV 속 사람들이 갔던 장소는 어디일까? 우리 동네에도 있을까?”

최근 많은 사람들이 방송 콘텐츠 속 장소에 대한 관심이 높아지고 있다. 

본 프로젝트는 **방송 콘텐츠에 등장한 촬영지 데이터를 기반으로, 사용자가 입력한 정보에 따라 쉽게 찾을 수 있는 시각화 정보 및 서비스**를 목표로 한다.

사용자는 자신의 **주소**나 **제목**을 입력하면, 해당 지역 혹은 작품의 촬영 장소를 지도 기반으로 한 눈에 확인할 수 있다.
<br/>
<br/>
## 1. 사용 데이터 - 소셜데이터 속 K-무비 연관 관광지 데이터


15034 rows × 14 column로 구성되었다.

<img width="1588" height="353" alt="Image" src="https://github.com/user-attachments/assets/1aed9527-fc09-4a2d-b7db-1f87b61580b5" />

<table border="1" align="center">
  <tr>
    <td align="center">연번</td>
    <td align="center">미디어타입</td>
    <td align="center">제목</td>
    <td align="center">장소명</td>
    <td align="center">장소타입</td>
    <td align="center">장소설명</td>
    <td align="center">영업시간</td>
  </tr>
  <tr>
    <td align="center">브레이크타임</td>
    <td align="center">휴무일</td>
    <td align="center">주소</td>
    <td align="center">위도</td>
    <td align="center">경도</td>
    <td align="center">전화번호</td>
    <td align="center">최종작성일</td>
  </tr>
</table>



다음은 데이터 변수에 대한 설명이다.

- 연번(int64) : 고유 식별번호 또는 일련번호 (순번). 1부터 15034까지 존재
- 미디어타입(object) :  해당 콘텐츠의 유형 (예: drama, movie, show, artist)
- 제목(object) : 콘텐츠 제목 (작품명)
- 장소명(object) : 촬영 장소의 이름
- 장소타입(object) : 장소의 분류 (예 : cafe, playground, restaurant, stay, station, store, cvs, stay, shop)
- 영업시간(object) : 장소의 운영 시간
- 브레이크타임(object) : 장소의 휴식 시간
- 휴무일(object) : 휴무일 정보(정기 휴일 등) (예 : 연중무휴)
- 주소(object)
- 위도(float64)
- 경도(float64)
- 전화번호(object)
- 최종작성일(object) : 데이터가 작성된 날짜
  
<br/>

## 2. 프로토타입


<table align="center">
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/e1057c22-2a7a-4c8d-86ab-250b81c855af" width="300px"><br>
      <b>📌 주소 기반 장소 추천 화면</b>
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/ff907909-fc03-4b73-8ebb-4b6fc8c1f145" width="300px"><br>
      <b>📌 작품명 기반 장소 추천 화면</b>
    </td>
  </tr>
</table>

<br/>

## 3. 데이터 전처리

확인할 부분

**① 결측치의 유무?**

전화번호 column의 경우 전체 中 14598개의 행만 존재하는 것을 확인. 이를 제외하면 존재하지 않고, 전화번호를 따로 시각화에 사용하지 않음 → 따로 결측치 제거 X

**② 이상치의 유무?**

이상치가 발생할만한 위∙경도를 확인해본 결과, 대한민국을 벗어난 위∙경도가 존재 → 제거

<img width="1207" height="183" alt="Image" src="https://github.com/user-attachments/assets/575283d0-74c1-418f-bec6-598c6f2c8a86" />

**③ 오타의 유무?**

장소타입을 확인해본 결과, ‘stay’와 ‘stay ‘가 발견됨 → 데이터 입력 시 띄어쓰기가 포함된 행 전처리

**④ 의미 중복의 유무?**

장소타입의 ‘csv’(편의점), ‘shop’(잡화점)은 ‘store’(대형 마트)와 중복된 의미를 가짐

개수도 한 자리 수로 적기 때문에 큰 범주인 ‘store’로 합침 

**⑤ 식별하기 편한가?**

장소타입을 시각화했을 때 ‘restaurant’은 ‘식당’보다 식별하기 불편함 → 한글로 변환

‘cafe’ → 카페

‘restaurant’ → 식당

‘stay’ → 숙박 시설

‘station’ → 역

‘store’ → 상점

‘playground’ → 촬영지
<br/>

또한 주소를 살펴보았을 때, 구주소와 신주소가 통합되지 않은 모습을 보여 식별하기 불편함 → 구주소로 통합한 상세주소 열을 만들어 통합

<br/>

## 4. 웹 어플리케이션

https://fisa05-stream-team1.streamlit.app/

<br/>

## 5. 해결한 트러블 슈팅

https://drive.google.com/file/d/1tZ4D380kxmQEOpNzo_Ue-vAGyeDFdfiC/view?usp=sharing

위도, 경도로 표시한 곳과 실제 주소가 다름을 확인, '주소'의 데이터엔 구주소와 신주소가 혼재되어 있음 → 이 트러블 슈팅을 해결

**① 역지오코딩(위도, 경도로 주소 추출)으로 얻은 주소가 기존 주소와 상이하면 행 삭제**
- 카카오맵 API로 '위도', '경도'로 구주소가 들어있는 '상세주소' 칼럼 생성
- '상세주소'의 앞 2글자가 '주소'에 있으면 정상 데이터로 판단
- '주소'로 검색시 '상세주소'이용 -> 기존 OO구 까지만되던 검색이 OO동까지 가능
 
**② '상세주소'에서 '전남', '경북' 등의 표현이 이상치 제거에 오류를 발생시킴을 확인**
- '상세주소' 앞 2글자를 매핑된 문자열로 변환
<br/>

한글관련 문제

**③ K-means Clustering 수행 과정 중 충돌 문제 확인**
- 한글 출력의 어려움을 겪음
