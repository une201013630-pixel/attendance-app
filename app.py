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
st.write(df.head())  # 
    # 👉 필요한 열 위치로 정확히 선택 (너 엑셀 기준)
    df = df.iloc[:, [0, 1, 2, 3, 6, 9, 12]]

    df.columns = ["번호","이름","수업일수","결석","지각","조퇴","결과"]

    df = df.fillna(0)
    return df

def create_card(row):
    img = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(img)

    # 🔴 강조 조건
    if row["결석"] >= 5:
        color = "red"
    elif row["결석"] > 0:
        color = "orange"
    else:
        color = "green"

    draw.text((20, 50), f"{int(row['번호'])}번 {row['이름']}", fill="black")
    draw.text((20, 120), f"결석 {int(row['결석'])}회", fill=color)
    draw.text((20, 170), f"지각 {int(row['지각'])} / 조퇴 {int(row['조퇴'])}", fill="black")

    return img

if uploaded_file:
    df = preprocess(uploaded_file)

    st.dataframe(df)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for _, row in df.iterrows():
            img = create_card(row)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            zf.writestr(f"{row['번호']}_{row['이름']}.png", buf.getvalue())

    st.download_button("📦 전체 다운로드", zip_buffer.getvalue(), file_name="출결.zip")
