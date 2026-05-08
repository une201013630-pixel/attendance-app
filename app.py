import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io, zipfile

st.title("🏫 학급 출결 리포트 생성기")

school = st.text_input("학교명", "○○고등학교")
class_name = st.text_input("반", "1학년 5반")
period = st.text_input("기간", "2026.03 ~ 04")

uploaded_file = st.file_uploader("엑셀 업로드", type=["xlsx"])

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

def preprocess(file):
    df = pd.read_excel(file, header=7)
    df = df.drop(0)

    df.columns = [
        "학번","이름","수업일수",
        "결석","지각","조퇴","결과",
        "질병결석","미인정결석",
        "질병지각","미인정지각",
        "질병조퇴","미인정조퇴",
        "질병결과","미인정결과"
    ]
    return df.fillna(0)

# 🎨 카드 이미지 생성
def create_card(row):
    img = Image.new("RGB", (800, 420), "#f9fafb")
    draw = ImageDraw.Draw(img)

    # 위험도 색상
    if row["결석"] >= 5:
        color = "red"
        badge = "🔴 위험"
    elif row["결석"] > 0:
        color = "orange"
        badge = "🟡 주의"
    else:
        color = "green"
        badge = "🟢 양호"

    # 상단
    draw.text((20, 20), f"{school} | {class_name}", fill="black")
    draw.text((20, 50), f"📅 {period}", fill="gray")

    # 이름
    draw.text((20, 100), f"{int(row['학번'])}번 {row['이름']}", fill="black")

    # 상태
    draw.text((600, 100), badge, fill=color)

    # 출결
    draw.text((20, 160),
              f"결석 {int(row['결석'])} / 지각 {int(row['지각'])} / 조퇴 {int(row['조퇴'])} / 결과 {int(row['결과'])}",
              fill="black")

    return img


# ✉️ 카톡용 메시지
def make_msg(row):
    return f"""[출결 안내]
{school} {class_name}

{row['이름']} 학생

📅 {period}

결석 {int(row['결석'])}
지각 {int(row['지각'])}
조퇴 {int(row['조퇴'])}
결과 {int(row['결과'])}

지도 부탁드립니다 🙏"""


if uploaded_file:
    df = preprocess(uploaded_file)

    # 누적
    if not st.session_state.data.empty:
        df = pd.concat([st.session_state.data, df])
        df = df.groupby(["학번","이름"]).sum().reset_index()

    st.session_state.data = df

    # 🚨 위험 학생
    st.subheader("🚨 결석 5회 이상")
    st.dataframe(df[df["결석"] >= 5])

    # 📋 전체
    st.subheader("📋 전체")
    st.dataframe(df)

    # 📦 다운로드
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for _, row in df.iterrows():
            img = create_card(row)

            buf = io.BytesIO()
            img.save(buf, format="PNG")

            name = f"{int(row['학번'])}_{row['이름']}"

            zf.writestr(f"{name}.png", buf.getvalue())

            # 개별 UI
            st.image(img, width=300)
            st.download_button(f"{row['이름']} 카드 다운로드", buf.getvalue(), file_name=f"{name}.png")

            msg = make_msg(row)
            st.text_area(f"{row['이름']} 메시지", msg, height=120)

    st.download_button("📦 전체 ZIP", zip_buffer.getvalue(), file_name="출결.zip")