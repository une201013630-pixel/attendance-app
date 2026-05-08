import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import io, zipfile

st.set_page_config(page_title="출결 리포트", layout="wide")

st.title("🏫 학급 출결 리포트 생성기")

uploaded_file = st.file_uploader("엑셀 업로드", type=["xlsx"])

def preprocess(file):
    # 👉 그냥 전체 읽기 (헤더 추측 X)
    raw = pd.read_excel(file, header=None)

    # 👉 화면에 원본 보여주기 (확인용)
    st.subheader("🔍 원본 데이터")
    st.dataframe(raw)

    result = []

    for i in range(len(raw)):
        row = raw.iloc[i]

        try:
            # 👉 이름이 있는 행만 필터
            name = row[1]
            if pd.isna(name):
                continue

            num = int(row[0])
            days = int(row[2])

            # 👉 여기 중요 (네 파일 구조 기준)
            absence = int(row[3]) if not pd.isna(row[3]) else 0
            late = int(row[6]) if not pd.isna(row[6]) else 0
            early = int(row[9]) if not pd.isna(row[9]) else 0
            result_val = int(row[12]) if not pd.isna(row[12]) else 0

            result.append([num, name, days, absence, late, early, result_val])

        except:
            continue

    df = pd.DataFrame(result, columns=[
        "번호","이름","수업일수","결석","지각","조퇴","결과"
    ])

    return df


def highlight(row):
    if row["결석"] >= 5:
        return ['background-color: #ffcccc'] * len(row)
    elif row["결석"] > 0:
        return ['background-color: #fff2cc'] * len(row)
    else:
        return [''] * len(row)


def create_card(row):
    img = Image.new("RGB", (600, 300), "white")
    draw = ImageDraw.Draw(img)

    # 색상
    if row["결석"] >= 5:
        color = "red"
    elif row["결석"] > 0:
        color = "orange"
    else:
        color = "green"

    draw.text((30, 40), f"{row['번호']}번 {row['이름']}", fill="black")
    draw.text((30, 110), f"수업일수: {row['수업일수']}", fill="black")
    draw.text((30, 150), f"결석: {row['결석']}", fill=color)
    draw.text((30, 190), f"지각: {row['지각']} / 조퇴: {row['조퇴']}", fill="black")

    return img


if uploaded_file:
    df = preprocess(uploaded_file)

    st.subheader("📊 전체 출결 현황")

    st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

    st.divider()

    st.subheader("📥 개별 리포트 다운로드")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for _, row in df.iterrows():
            img = create_card(row)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            zf.writestr(f"{row['번호']}_{row['이름']}.png", buf.getvalue())

    st.download_button("📦 전체 다운로드 (이미지)", zip_buffer.getvalue(), file_name="출결리포트.zip")
