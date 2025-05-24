import pandas as pd
import io
from io import StringIO

# 입력된 테이블 형태의 마크다운을 엑셀로 변환하는 함수
# 리턴값 : 엑셀 바이너리 바이너리 데이터
def markdown_to_excel(markdown: str):

    markdown_input = markdown

    cleaned = "\n".join([
        line for line in markdown_input.strip().split("\n")
        if not set(line.strip()) <= {"|", "-"}
    ])
    df = pd.read_csv(StringIO(cleaned), sep="|")
    if "" in df.columns:
        df = df.drop(columns=[""])

    # Remove columns A and K during creation (0 and 10 index) if they exist
    desired_columns = [
        col for idx, col in enumerate(df.columns)
        if idx != 0 and idx != 10
    ]
    df = df[desired_columns]

    # Skip the 2nd record (index 1) if it exists
    if df.shape[0] > 1:
        df = df.drop(index=0)

    df.columns = [col.strip() for col in df.columns]
    # df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # 엑셀로 저장 후 다운로드 링크 제공    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    
    return output.getvalue()