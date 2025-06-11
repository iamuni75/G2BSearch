import pandas as pd
import io
from io import StringIO

# 입력된 테이블 형태의 마크다운을 엑셀로 변환하는 함수
# 리턴값 : 엑셀 바이너리 바이너리 데이터
def markdown_to_excel(markdown: str):
    """
    마크다운 테이블을 엑셀로 변환하는 함수 (모든 데이터 유지)
    Args:
        markdown (str): 마크다운 형식의 테이블 문자열
    Returns:
        bytes: 엑셀 파일의 바이너리 데이터
    """
    markdown_input = markdown

    # 구분선과 빈 줄 제거
    cleaned = "\n".join([
        line for line in markdown_input.strip().split("\n")
        if not set(line.strip()) <= {"|", "-"}
    ])
    
    # DataFrame 생성
    df = pd.read_csv(StringIO(cleaned), sep="|")
    
    # Unnamed 칼럼 제거 (첫번째와 마지막 칼럼이 보통 Unnamed임)
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    # 구분선("---" 등) 이 있는 행 제거
    df = df[~df.apply(lambda row: row.astype(str).str.contains('---').any(), axis=1)]

    # 칼럼명 공백 제거
    df.columns = [col.strip() for col in df.columns]

    # 데이터 전처리
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
        # 마크다운 링크에서 https 주소만 추출
        df[col] = df[col].map(lambda x: extract_https_url(x) if isinstance(x, str) and '[' in x and '](' in x else x)

    # 엑셀 파일 생성
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    
    return output.getvalue()

def extract_https_url(text: str) -> str:
    """
    마크다운 링크에서 https URL을 추출하는 함수
    예: "[텍스트](https://example.com)" -> "https://example.com"
    """
    if '](' not in text or ')' not in text:
        return text
    
    start_idx = text.find('](') + 2
    end_idx = text.find(')', start_idx)
    
    if start_idx > 1 and end_idx > start_idx:
        url = text[start_idx:end_idx]
        if url.startswith('https://'):
            return url
    
    return text