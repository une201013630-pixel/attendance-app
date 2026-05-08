import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import io, zipfile

st.title("🏫 학급 출결 리포트 생성기")

uploaded_file = st.file_uploader("엑셀 업로드", type=["xlsx"])

def preprocess(file):
    df = pd.read_excel(file, header=7)

    # 첫 줄 제거
    df = df.drop(0)

    # 🔥 엑셀 구조 확인용 (중요)
    st.subheader("🔍 원본 데이터 확인")
    st.write(df.head())

    # 👉 일단 전체 열 보여주기
    st.write("컬럼 목록:", list(df.columns))

    # 👉 임시로 앞 15개 열만 사용
    df = df.iloc[:, :15]

    return df

def create_card(name, num, absence, late, early):
    img = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(img)

    # 🔴 강조 조건
    if absence >= 5:
        color = "red"
    elif absence > 0:
        color = "orange"
    else:
        color = "green"

    draw.text((20, 50), f"{num}번 {name}", fill="black")
    draw.text((20, 120), f"결석 {absence}회", fill=color)
    draw.text((20, 170), f"지각 {late} / 조퇴 {early}", fill="black")

    return img

if uploaded_file:
    df = preprocess(uploaded_file)

    st.subheader("📊 데이터 미리보기")
    st.dataframe(df)

    st.warning("👉 위 표에서 '번호, 이름, 결석, 지각, 조퇴' 위치 확인 후 다음 단계 진행")

    # 👉 임시 카드 생성 (테스트용)
    if st.button("📦 테스트 카드 생성"):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for _, row in df.iterrows():
                try:
                    name = str(row.iloc[1])
                    num = int(row.iloc[0])
                    absence = int(row.iloc[3])
                    late = int(row.iloc[4])
                    early = int(row.iloc[5])

                    img = create_card(name, num, absence, late, early)

                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    zf.writestr(f"{num}_{name}.png", buf.getvalue())

                except:
                    continue

        st.download_button("📦 전체 다운로드", zip_buffer.getvalue(), file_name="출결.zip")
