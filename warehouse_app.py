import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="نظام طلبات المخزن — عصير تايم",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp {
        background-color: #181b1a;
        color: #e5e7eb;
    }
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .info-box {
        background-color: #202422;
        border: 1px solid #2e3532;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #d1d5db;
        font-size: 15px;
        line-height: 1.7;
    }
    div.stButton > button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-family: 'Cairo', sans-serif;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #059669;
        color: white;
    }
    .stNumberInput label p {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "warehouse_orders_data.json"

INVENTORY_ITEMS = [
    "كلينكس حمامات",
    "كلينكس طاولة",
    "قاصر",
    "فلاش",
    "معطر ارضيه",
    "معطر جو",
    "وصل مسح",
    "وصل مسح طاولة",
    "كيس نفايات كبير",
    "كيس نفايات صغير",
    "جفوف",
    "خواشيك ايس",
    "حمالات رباعيه",
    "علاكه عصير"
]

def load_orders():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_orders(orders):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

orders_list = load_orders()

st.markdown("<div class='main-title'>📦 نظام طلبات المخزن والمستلزمات — عصير تايم</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af;'>نظام مخصص لطلبات صالة المطعم والمخزن اليومية</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #2e3532;'>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 إرسال طلب جديد (للمطعم / الويتر)", "📋 متابعة الطلبات الواردة (للمخزن)"])

with tab1:
    st.markdown("""
    <div class="info-box">
        اختر الكميات المطلوبة لكل مادة ليوم غد، ثم اضغط على زر إرسال الطلب ليظهر مباشرة عند مسؤول المخزن.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_order_form"):
        order_quantities = {}
        cols = st.columns(2)
        for idx, item in enumerate(INVENTORY_ITEMS):
            with cols[idx % 2]:
                q = st.number_input(f"{item}", min_value=0.0, step=1.0, value=0.0, key=f"item_{idx}")
                if q > 0:
                    order_quantities[item] = q
        
        submitted = st.form_submit_button("📤 إرسال الطلب إلى المخزن")
        if submitted:
            if order_quantities:
                new_entry = {
                    "الوقت": pd.Timestamp.now().strftime("%Y-%m-%d %I:%M %p"),
                    "المواد": order_quantities,
                    "الحالة": "قيد الانتظار"
                }
                orders_list.insert(0, new_entry)
                save_orders(orders_list)
                st.success("✅ تم إرسال الطلب إلى المخزن بنجاح!")
                st.rerun()
            else:
                st.warning("يرجى تحديد كمية مادة واحدة على الأقل قبل الإرسال.")

with tab2:
    st.markdown("#### الطلبات الواردة للمخزن")
    if orders_list:
        for i, ord_item in enumerate(orders_list):
            badge_color = "#10b981" if ord_item["الحالة"] == "تم التجهيز" else "#f59e0b"
            st.markdown(f"""
            <div style="background-color:#202422; border:1px solid #2e3532; border-radius:10px; padding:15px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#9ca3af; font-size:14px;">📅 {ord_item['الوقت']}</span>
                    <span style="background-color:{badge_color}; color:white; padding:2px 10px; border-radius:5px; font-size:12px;">{ord_item['الحالة']}</span>
                </div>
                <hr style="border-color:#2e3532; margin:10px 0;">
            </div>
            """, unsafe_allow_html=True)
            
            details_str = " &nbsp;|&nbsp; ".join([f"<b>{k}:</b> <span style='color:#10b981; font-weight:bold;'>{v}</span>" for k, v in ord_item["المواد"].items()])
            st.markdown(f"<div style='font-size:15px; line-height:1.8;'>{details_str}</div>", unsafe_allow_html=True)
            
            if ord_item["الحالة"] == "قيد الانتظار":
                st.write("")
                if st.button("✔️ تم تجهيز وتسليم الطلب", key=f"done_btn_{i}"):
                    orders_list[i]["الحالة"] = "تم التجهيز"
                    save_orders(orders_list)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        if st.button("🗑️ مسح سجل الطلبات السابقة"):
            save_orders([])
            st.rerun()
    else:
        st.info("لا توجد طلبات واردة حالياً.")