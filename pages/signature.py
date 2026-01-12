import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64
from datetime import datetime

st.set_page_config(
    page_title="חתימה דיגיטלית - TikTik",
    page_icon="✍️",
    layout="centered"
)

RTL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Heebo', sans-serif !important;
}

.main .block-container {
    direction: rtl;
    text-align: right;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    direction: rtl;
    text-align: right;
}

.signature-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    text-align: center;
}

.signature-container h1 {
    color: #fff;
    font-size: 2rem;
}

.confirmation-box {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid #333;
    margin: 1rem 0;
}

.success-box {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    color: white;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 10px;
}

canvas {
    border: 2px solid #667eea !important;
    border-radius: 10px !important;
}
</style>
"""

st.markdown(RTL_CSS, unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="signature-container">
        <h1>✍️ אישור וחתימה דיגיטלית</h1>
        <p style="color: #a0a0a0;">אנא קרא את התנאים וחתום למטה</p>
    </div>
    """, unsafe_allow_html=True)
    
    order_id = st.query_params.get("order", "")
    customer = st.query_params.get("customer", "לקוח יקר")
    
    st.markdown(f"### שלום {customer}! 👋")
    
    st.markdown("---")
    
    st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
    st.markdown("### 📋 אישור תנאים")
    
    st.markdown("""
    **בחתימתי למטה אני מאשר/ת כי:**
    
    ✅ קראתי את כל תנאי ההזמנה והתקנון המצורף והבנתי אותם במלואם
    
    ✅ אני מסכים/ה לתנאי השירות, מדיניות הביטולים ותנאי התשלום
    
    ✅ כל הפרטים שמסרתי נכונים ומדויקים
    
    ✅ אני מודע/ת כי מרגע אישור ההזמנה חלים דמי ביטול בהתאם לתקנון
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    agree = st.checkbox("אני מאשר/ת שקראתי והבנתי את כל התנאים", key="agree_terms")
    
    if agree:
        st.markdown("---")
        st.markdown("### ✍️ חתום כאן")
        st.markdown("*השתמש בעכבר או באצבע (בנייד) לחתימה*")
        
        try:
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=200,
                width=400,
                drawing_mode="freedraw",
                key="signature_canvas",
            )
        except:
            st.info("📝 שדה חתימה דיגיטלי זמין")
            signature_text = st.text_input("או הקלד את שמך המלא כחתימה:", placeholder="שם מלא")
            canvas_result = None
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 נקה חתימה", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("✅ אשר ושלח", type="primary", use_container_width=True):
                st.markdown("""
                <div class="success-box">
                    <h2>🎉 תודה רבה!</h2>
                    <p>ההזמנה שלך אושרה בהצלחה</p>
                    <p>נשלח לך אישור במייל בקרוב</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                
                st.markdown(f"""
                ---
                📅 **תאריך אישור:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
                
                📧 אישור נשלח לאימייל שלך
                
                📞 לשאלות: 972-732726000
                """)
    else:
        st.info("📝 סמן את תיבת האישור כדי להמשיך לחתימה")

if __name__ == "__main__":
    main()
