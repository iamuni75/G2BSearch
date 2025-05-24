import requests
from datetime import date, datetime


# 검색 키워드를 기반으로 G2B 본공고 검색하기
def G2B_search_by_keywords(search_keywords: list, begin_date: date, callback=None) -> dict:
    
    # 검색 키워드가 없으면 종료
    if len(search_keywords) == 0: return

    url = "http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch"
    params = {        
        "serviceKey": "MVoTD2rvZNfyUqlB1iwYk4FiSi6jR2jcVP4ZKUI+u6HKiyXcraeAVhSLBbsjSuDpfmScCy6R7bU3CcOP6ormdA==",             # 디코딩
        "pageNo": 1,      # 검색 결과 페이지 번호
        "numOfRows": 20,  # 페이지당 항목 수
        "type": "json",     # 검색결과 표현 방식
        "inqryDiv": 1,      # 조회구분(1:공고게시일시, 2:개찰일시)
        "inqryBgnDt": begin_date.strftime("%Y%m%d") + "0000",      # 검색시작날짜
    }

    searched_list = []

    # 입력된 키워드 리스트를 반복해서 파라메터를 추가해서 검색함
    for keyword in search_keywords:
        if keyword:
            if callback:
                callback(f"⏳ 나라장터 입찰공고에서 **'{keyword}'** 검색중...")

            params["bidNtceNm"] = keyword   # 공고명 검색어

            response = requests.get(url, params=params)

            if response.ok:
                searched_result = response.json()  # JSON 형태 응답 파싱
                searched_result_items = collect_item_info(keyword, searched_result)
                
                # 공고 항목을 리스트에서 꺼내서, 최종 활용할 검색결과 리스트에 담기
                for item in searched_result_items:
                    searched_list.append(item)
                
            else:
                print("요청 실패:", response.status_code)
    
    searched_result = {}
    searched_result["total_count"] = len(searched_list)
    searched_result["main_searched_list_md"] = dict_to_md(searched_list)
    return searched_result


# API 검색 결과 아이템에서 필요한 정보만 추출하여 리스트를 반환
def collect_item_info(search_keyword: str, g2b_searched: dict) -> list:       
    
    item_list = g2b_searched["response"]["body"]["items"]
    
    item_info_selected_list = []

    # 나라장터 검색 결과 중 필요한 항목만 추출
    for item in item_list:
        item_info = {}
        item_info["검색어"] = search_keyword
        item_info["입찰공고일시"] = item["bidNtceDt"]
        item_info["입찰마감일시"] = item["bidClseDt"]
        item_info["입찰공고명"] = item["bidNtceNm"]
        
        # 추정가격은 천단위 콤마와 '원'을 붙여서 텍스트로 저장
        item_price = int(item["presmptPrce"])
        item_price_unit = f"{item_price:,}원"
        item_info["추정가격"] = item_price_unit
        
        item_info["공고기관"] = item["ntceInsttNm"]
        item_info["수요기관"] = item["dminsttNm"]
        item_info["입찰공고번호"] = item["bidNtceNo"]
        item_info["입찰방식"] = item["bidMethdNm"]
        item_info["계약체결방법"] = item["cntrctCnclsMthdNm"]
        item_info["용역구분"] = item["srvceDivNm"]
        item_info["입찰공고상세URL"] = item["bidNtceDtlUrl"]
        
        item_info_selected_list.append(item_info)

    return item_info_selected_list


# 입력된 리스트안에 있는 딕셔너리의 값을 마크다운 표로 작성하여 반환
def dict_to_md(searched_items: list) -> str:
    
    # 마크다운 표 만들기
    headers = ["검색어", "입찰공고일시", "입찰마감일시", "입찰공고명", "추정가격", "공고기관", "수요기관", "입찰공고번호", "입찰방식", "계약체결방법", "용역구분", "입찰공고상세URL"]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    # 행 데이터 수집
    rows = []
    
    for item in searched_items:
        row = "| " + " | ".join(
            str(item.get(key, "")) if not key.endswith("URL") else f"[링크]({item.get(key, '')})"
            for key in headers
        ) + " |"
        rows.append(row)

    # 마크다운 테이블 출력
    markdown_table = "\n".join([header_row, separator_row] + rows)

    return markdown_table


# -------------------------------------------------------
# 위쪽의 내용은 본공고 내용 검색해서 마크다운으로 변경하는 코드
# 아래쪽의 내용은 사전규격 내용 검색해서 마크다운으로 변경하는 코드
# 두코드 모두 똑같음. 단 API 호출할때 사용되는 인자 차이에 의한 차이일쁀
# -------------------------------------------------------


# 검색 키워드를 기반으로 G2B 사전규격 검색하기
def preG2B_search_by_keywords(search_keywords: list, begin_date: date, callback=None) -> dict:
    
    # 검색 키워드가 없으면 종료
    if len(search_keywords) == 0: return

    url = "http://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServcPPSSrch"

    params = {        
        "serviceKey": "MVoTD2rvZNfyUqlB1iwYk4FiSi6jR2jcVP4ZKUI+u6HKiyXcraeAVhSLBbsjSuDpfmScCy6R7bU3CcOP6ormdA==",             # 디코딩
        "pageNo": 1,      # 검색 결과 페이지 번호
        "numOfRows": 20,  # 페이지당 항목 수
        "type": "json",     # 검색결과 표현 방식
        "inqryDiv": 1,      # 조회구분(1:접수일시)
        "inqryBgnDt": begin_date.strftime("%Y%m%d") + "0000",   # 검색시작날짜
        "inqryEndDt": datetime.now().strftime("%Y%m%d%H%M"),    # 검색종료날짜(현재 시간), 입력안하면 오류나서 입력함
    }

    searched_list = []

    # 입력된 키워드 리스트를 반복해서 파라메터를 추가해서 검색함
    for keyword in search_keywords:
        if keyword:
            if callback:
                callback(f"⏳ 나라장터 사전규격에서 **'{keyword}'** 검색중...")

            params["prdctClsfcNoNm"] = keyword   # 사전규격 품명

            response = requests.get(url, params=params)

            if response.ok:
                searched_result = response.json()  # JSON 형태 응답 파싱
                searched_result_items = preCollect_item_info(keyword, searched_result)
                
                # 사전규격 항목을 리스트에서 꺼내서, 최종 활용할 검색결과 리스트에 담기
                for item in searched_result_items:
                    searched_list.append(item)
                
            else:
                print("요청 실패:", response.status_code)
    
    searched_result = {}
    searched_result["total_count"] = len(searched_list)
    searched_result["main_searched_list_md"] = preDict_to_md(searched_list)
    return searched_result


# API 검색 결과 사전규격 아이템에서 필요한 정보만 추출하여 리스트를 반환
def preCollect_item_info(search_keyword: str, g2b_searched: dict) -> list:       
    
    item_list = g2b_searched["response"]["body"]["items"]
    
    item_info_selected_list = []

    # 나라장터 검색 결과 중 필요한 항목만 추출
    for item in item_list:
        item_info = {}
        item_info["검색어"] = search_keyword
        item_info["접수일시"] = item["rcptDt"]
        item_info["의견등록마감일시"] = item["opninRgstClseDt"]
        item_info["품명"] = item["prdctClsfcNoNm"]

        # 추정가격은 천단위 콤마와 '원'을 붙여서 텍스트로 저장
        item_price = int(item["asignBdgtAmt"])
        item_price_unit = f"{item_price:,}원"
        item_info["배정예산금액"] = item_price_unit
        
        item_info["발주기관"] = item["orderInsttNm"]
        item_info["실수요기관"] = item["rlDminsttNm"]
        item_info["사전규격등록번호"] = item["bfSpecRgstNo"]
        item_info["참조번호"] = item["refNo"]
        # item_info["규격문서파일URL"] = item["specDocFileUrl1"]    # 현재 사전규격 API에서는 URL 서비스를 제공하지 않고 있음
        
        item_info_selected_list.append(item_info)

    return item_info_selected_list


# 입력된 사전규격 리스트안에 있는 딕셔너리의 값을 마크다운 표로 작성하여 반환
def preDict_to_md(searched_items: list) -> str:
    
    # 마크다운 표 만들기
    headers = ["검색어", "접수일시", "의견등록마감일시", "품명", "배정예산금액", "발주기관", "실수요기관", "사전규격등록번호", "참조번호"]  #, "규격문서파일URL"]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    # 행 데이터 수집
    rows = []
    
    for item in searched_items:
        row = "| " + " | ".join(
            str(item.get(key, "")) if not key.endswith("URL") else f"[링크]({item.get(key, '')})"
            for key in headers
        ) + " |"
        rows.append(row)

    # 마크다운 테이블 출력
    markdown_table = "\n".join([header_row, separator_row] + rows)

    return markdown_table
