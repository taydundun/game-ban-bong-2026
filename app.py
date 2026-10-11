import streamlit as st

st.title("🎯 Game Bắn Bóng (Bubble Shooter)")
st.write("Chào mừng bạn đến với dự án game bắn bóng nộp bài Tin học!")

# Giao diện điều khiển game đơn giản trên Streamlit
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Bảng điều khiển")
    angle = st.slider("Chọn góc bắn", 0, 180, 90)
    power = st.slider("Chọn lực bắn", 1, 100, 50)
    
    if st.button("🔥 Bắn bóng!", type="primary"):
        st.success(f"Đã bắn quả bóng với góc {angle}° và lực {power}!")
        st.balloons()

with col2:
    st.subheader("Trạng thái")
    st.info("Điểm số hiện tại: 0")
    st.info("Số bóng còn lại: 15")

st.markdown("---")
st.write("Mẹo: Bạn có thể lưu đoạn code này thành file `app.py` và tải lên GitHub repo `game-ban-bong-2026` của bạn nhé!")
