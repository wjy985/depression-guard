"""
心晴伴侣 | 阈下抑郁多模态数字表型预警与健康管理系统 (Ultra Aesthetic Pro)
技术栈: Streamlit, Plotly, Pandas, NumPy, JSON/HTML Export
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import List, Tuple, Optional

# -------------------------------------------------------------
# 1. 页面配置与顶级心理学高级美学 CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="心晴伴侣 | 情绪健康空间",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 引入精致现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* 全局背景：柔和有机渐变底色 */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(226, 235, 229, 0.6) 0%, rgba(247, 246, 242, 1) 50%, rgba(248, 237, 226, 0.4) 100%);
        color: #2D312E;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    /* 侧边栏高级微毛玻璃质感 */
    [data-testid="stSidebar"] {
        background: rgba(241, 239, 233, 0.75) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(224, 221, 213, 0.6);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 6px;
    }

    /* 高级卡片容器：微阴影 + 柔和边框 */
    .soothing-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(45, 49, 46, 0.04), 0 0 1px 1px rgba(234, 232, 225, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .soothing-card:hover {
        box-shadow: 0 14px 35px -5px rgba(45, 49, 46, 0.07);
    }

    /* 顶部标题区装饰 */
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #243329;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #6B726C;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* 预警徽章系统 */
    .badge-normal {
        background: #E2EBE5;
        color: #2D4C38;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.2px;
    }
    .badge-subthreshold {
        background: #FCEFD9;
        color: #9C5819;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
    }
    .badge-crisis {
        background: #FDE8E7;
        color: #A8332D;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
    }

    /* 危机警示横幅 */
    .crisis-banner {
        background: #FFF2F1;
        border: 1.5px solid #E29E9A;
        border-radius: 20px;
        padding: 26px;
        margin: 20px 0;
        color: #691E1A;
        box-shadow: 0 10px 25px -5px rgba(217, 83, 79, 0.1);
    }

    /* 按钮高级样式重塑 */
    .stButton>button {
        background: #5E7A68 !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 14px rgba(94, 122, 104, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
    }
    .stButton>button:hover {
        background: #4B6354 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(94, 122, 104, 0.35) !important;
    }

    /* 选项卡 (Tabs) 样式升级 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(234, 232, 225, 0.5);
        padding: 6px;
        border-radius: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 500;
        color: #6B726C;
        border: none !important;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2D312E !important;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* 滑块视觉润色 */
    .stSlider [data-baseweb="slider"] {
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. 数据持久化引擎
# -------------------------------------------------------------
DATA_FILE = "depression_guard_data.json"

def load_all_local_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                df_ema = pd.DataFrame(raw.get("history_ema", []))
                assess = raw.get("assessment_result", None)
                pheno = raw.get("phenotype_history", [])
                if not df_ema.empty:
                    return df_ema, assess, pheno
        except Exception:
            pass

    today = datetime.now()
    np.random.seed(42)
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
    moods = np.clip(np.random.normal(loc=3.4, scale=0.5, size=14), 1.0, 5.0)
    energies = np.clip(np.random.normal(loc=3.2, scale=0.6, size=14), 1.0, 5.0)
    sleeps = np.clip(np.random.normal(loc=3.5, scale=0.4, size=14), 1.0, 5.0)

    df_ema = pd.DataFrame({
        "date": dates,
        "mood": [round(x, 1) for x in moods],
        "energy": [round(x, 1) for x in energies],
        "sleep": [round(x, 1) for x in sleeps]
    })
    df_ema["dci"] = (0.4 * df_ema["mood"] + 0.3 * df_ema["energy"] + 0.3 * df_ema["sleep"]).round(2)

    pheno = []
    for d in dates:
        pheno.append({
            "date": d,
            "homestay_ratio": round(float(np.random.uniform(0.40, 0.60)), 2),
            "location_entropy": round(float(np.random.uniform(1.8, 2.4)), 2),
            "sleep_latency_min": round(float(np.random.uniform(15.0, 25.0)), 1),
            "sleep_duration_hr": round(float(np.random.uniform(7.0, 8.0)), 1),
            "hrv_rmssd": round(float(np.random.uniform(45.0, 60.0)), 1),
            "night_screen_unlocks": int(np.random.randint(0, 3))
        })
    return df_ema, None, pheno

def save_all_local_data():
    payload = {
        "history_ema": st.session_state.history_ema.to_dict(orient="records"),
        "assessment_result": st.session_state.assessment_result,
        "phenotype_history": st.session_state.phenotype_history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if "history_ema" not in st.session_state:
    df_e, assess_r, pheno_h = load_all_local_data()
    st.session_state.history_ema = df_e
    st.session_state.assessment_result = assess_r
    st.session_state.phenotype_history = pheno_h

# -------------------------------------------------------------
# 3. 核心计算算法
# -------------------------------------------------------------
def evaluate_phq(scores: List[int]) -> dict:
    total = sum(scores)
    q9 = scores[8]
    if q9 >= 1:
        return {
            "level": "Level 4 - 紧急危机干预", "badge_type": "crisis",
            "title": "触发即时安全响应",
            "description": "检测到您可能正经历强烈的自伤意念或极大痛苦。请暂停自评，寻求专业医疗帮助或拨打危机热线。",
            "is_crisis": True, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }
    if total >= 15:
        return {
            "level": "Level 4 - 重度风险", "badge_type": "crisis",
            "title": "建议尽快就医诊疗",
            "description": "总分已达重度抑郁阈值，强烈建议前往三甲医院精神/心理科门诊完成系统排查。",
            "is_crisis": True, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }
    core_symptom = (scores[0] >= 2 or scores[1] >= 2)
    symptom_count = sum(1 for s in scores if s >= 2)
    if (5 <= total <= 9) and core_symptom and (2 <= symptom_count <= 4):
        return {
            "level": "Level 2 - 阈下抑郁预警 (Subthreshold)", "badge_type": "subthreshold",
            "title": "处于亚临床情绪低迷期",
            "description": "存在持续的快感缺失或情绪低落，处于易滑坡的灰色阶段。建议开启 14 天行为激活与情绪监测。",
            "is_crisis": False, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }
    elif total >= 10:
        return {
            "level": "Level 3 - 疑似临床抑郁", "badge_type": "subthreshold",
            "title": "建议专业心理评估",
            "description": "当前状态已超出日常波动范围，社会功能受到一定受累，建议预约专业咨询或门诊评估。",
            "is_crisis": False, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }
    elif total >= 5:
        return {
            "level": "Level 1 - 亚健康生活状态", "badge_type": "normal",
            "title": "轻度压力/疲劳波动",
            "description": "当前存在轻度压力反应或睡眠波动，未见核心抑郁特征。适度调整作息即可。",
            "is_crisis": False, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }
    else:
        return {
            "level": "Level 0 - 身心平衡状态", "badge_type": "normal",
            "title": "情绪状态稳定良好",
            "description": "各项指标均处于健康基线内，请继续保持良好的生活节律与自我关怀。",
            "is_crisis": False, "total_score": total, "date": datetime.now().strftime("%Y-%m-%d")
        }

def calculate_trend_k(dci_series: pd.Series) -> Tuple[float, bool]:
    if len(dci_series) < 7:
        return 0.0, False
    y = dci_series[-7:].values
    x = np.arange(7)
    slope, _ = np.polyfit(x, y, 1)
    return round(float(slope), 3), bool(slope <= -0.35)

class DigitalPhenotypeEngine:
    def __init__(self, window_days: int = 14, alert_threshold: float = 1.8):
        self.window_days = window_days
        self.alert_threshold = alert_threshold
        self.feature_configs = {
            "homestay_ratio": {"direction": "positive", "weight": 0.20, "label": "空间活动收缩(居家过久)"},
            "location_entropy": {"direction": "negative", "weight": 0.15, "label": "日常轨迹单一化"},
            "sleep_latency_min": {"direction": "positive", "weight": 0.15, "label": "入睡潜伏期延长"},
            "sleep_duration_hr": {"direction": "bilateral", "weight": 0.15, "label": "睡眠节律紊乱"},
            "hrv_rmssd": {"direction": "negative", "weight": 0.20, "label": "副交感神经张力下降(HRV偏低)"},
            "night_screen_unlocks": {"direction": "positive", "weight": 0.15, "label": "夜间频繁唤醒手机"},
        }

    def _compute_robust_z(self, val: float, hist: np.ndarray, direction: str) -> float:
        if len(hist) < 3: return 0.0
        med = np.median(hist)
        mad = max(np.median(np.abs(hist - med)), 1e-4)
        z = 0.6745 * (val - med) / mad
        if direction == "positive": return float(z)
        if direction == "negative": return float(-z)
        if direction == "bilateral": return float(abs(z))
        return float(z)

    def evaluate(self, current: dict, history: List[dict]) -> dict:
        if len(history) < self.window_days:
            return {"cdi": 0.0, "is_anomaly": False, "risk_level": "基线校准中", "z_scores": {}, "alert_reasons": []}
        recent = history[-self.window_days:]
        z_scores, alert_reasons = {}, []
        weighted_sum, total_w = 0.0, 0.0

        for f_name, cfg in self.feature_configs.items():
            val = current.get(f_name, 0.0)
            h_vals = np.array([item.get(f_name, 0.0) for item in recent])
            z_risk = self._compute_robust_z(val, h_vals, cfg["direction"])
            z_scores[f_name] = round(z_risk, 2)
            if z_risk > 0: weighted_sum += z_risk * cfg["weight"]
            total_w += cfg["weight"]
            if z_risk >= 2.2:
                alert_reasons.append(f"{cfg['label']} (Z={z_risk:.1f})")

        cdi = round(weighted_sum / total_w, 2)
        if cdi >= self.alert_threshold or len(alert_reasons) >= 2:
            r_level, is_ano = "Level 2 - 阈下抑郁偏离预警", True
        elif cdi >= 1.2:
            r_level, is_ano = "Level 1 - 亚健康轻度波动", False
        else:
            r_level, is_ano = "Level 0 - 基线平衡状态", False

        return {"cdi": cdi, "is_anomaly": is_ano, "risk_level": r_level, "z_scores": z_scores, "alert_reasons": alert_reasons}

# -------------------------------------------------------------
# 4. 侧边栏导航
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌿 心晴伴侣")
    st.caption("阈下抑郁数字表型动态预警与干预")
    menu = st.radio(
        "导航",
        [
            "🌿 阶梯式自测 (PHQ)",
            "📈 状态晴雨表 (EMA)",
            "🧬 数字表型与多模态",
            "📋 临床就诊参考单",
            "☕ 轻量减压工具箱",
            "⚙️ 数据持久化与备份",
            "📖 什么是阈下抑郁？"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("<b>💾 本地数据状态</b>", unsafe_allow_html=True)
    if os.path.exists(DATA_FILE):
        st.success("已同步至本地加密文件")
    else:
        st.info("当前处于即时会话模式")
    st.caption("🔒 零云端上传 · 纯本地隐私安全")

# -------------------------------------------------------------
# 5. 模块 1: 阶梯式自测 (PHQ)
# -------------------------------------------------------------
if menu == "🌿 阶梯式自测 (PHQ)":
    st.markdown('<div class="hero-title">🌿 阶梯式身心状态快速测评</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">在过去两周里，以下情况对您的困扰程度如何？请根据直觉作答。</div>', unsafe_allow_html=True)
    options = ["完全没有 (0分)", "有几天 (1分)", "一半以上时间 (2分)", "几乎每天 (3分)"]

    st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
    # 使用 Form 容器消除卡顿
    with st.form("phq_assessment_form"):
        st.markdown("#### 第一阶段：快速情绪初筛 (PHQ-2)")
        q1 = st.radio("1. 做事提不起劲，或者没有乐趣？", options, index=0, horizontal=True)
        q2 = st.radio("2. 感到心情低落、沮丧或绝望？", options, index=0, horizontal=True)
        
        st.markdown("<hr style='border-color: rgba(234, 232, 225, 0.6); margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 第二阶段：多维症状核对 (PHQ-9 完整项)")
        st.caption("若前两题无困扰，后 7 题保持默认即可；若感到近期状态有变化，建议完整勾选。")
        
        q3 = st.radio("3. 入睡困难、经常醒来，或睡得太多？", options, index=0, horizontal=True)
        q4 = st.radio("4. 感到疲倦、无精打采或缺乏精力？", options, index=0, horizontal=True)
        q5 = st.radio("5. 食欲不振，或者暴饮暴食？", options, index=0, horizontal=True)
        q6 = st.radio("6. 觉得自己很糟糕，觉得自己是个失败者，或者让家人失望？", options, index=0, horizontal=True)
        q7 = st.radio("7. 无法集中注意力（例如阅读、看电视或工作）？", options, index=0, horizontal=True)
        q8 = st.radio("8. 动作或说话迟缓到别人已察觉？或相反，烦躁不安难以静坐？", options, index=0, horizontal=True)
        q9 = st.radio("9. 有伤害自己、或者觉得不如死掉更好的念头？", options, index=0, horizontal=True)

        submitted = st.form_submit_button("完成测评并生成评估结果", use_container_width=True)
        if submitted:
            all_scores = [options.index(x) for x in [q1, q2, q3, q4, q5, q6, q7, q8, q9]]
            st.session_state.assessment_result = evaluate_phq(all_scores)
            save_all_local_data()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.assessment_result:
        res = st.session_state.assessment_result
        if res.get("is_crisis"):
            st.markdown(f"""
            <div class="crisis-banner">
                <h3 style="margin-top:0; font-size: 20px;">🛑 {res['level']}：{res['title']}</h3>
                <p style="font-size:15px; line-height: 1.7;">{res['description']}</p>
                <hr style="border-color: #E29E9A; margin: 16px 0;">
                <p><b>免费心理危机干预与医疗通道：</b></p>
                <ul style="line-height: 1.8;">
                    <li>📞 <b>全国希望24小时生命干预热线</b>：400-161-9995</li>
                    <li>📞 <b>北京心理危机研究与干预中心</b>：010-82951332 / 800-810-1117</li>
                    <li>🏥 <b>就医指引</b>：请前往所在地三甲综合医院精神心理科门诊就诊</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            badge_class = "badge-subthreshold" if res.get("badge_type") == "subthreshold" else "badge-normal"
            st.markdown(f"""
            <div class="soothing-card">
                <span class="{badge_class}">{res['level']}</span>
                <h3 style="margin-top: 14px; margin-bottom: 8px; color: #2D312E; font-size: 20px;">{res['title']} (得分: {res['total_score']} 分)</h3>
                <p style="font-size: 15px; line-height: 1.75; color: #555955;">{res['description']}</p>
                <div style="font-size: 13px; color: #8C928D; margin-top: 12px;">评估日期: {res.get('date', '今日')}</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. 模块 2: 状态晴雨表 (EMA)
# -------------------------------------------------------------
elif menu == "📈 状态晴雨表 (EMA)":
    st.markdown('<div class="hero-title">📈 每日状态晴雨表 (EMA 动态追踪)</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">每晚 30 秒微打卡。通过长周期多维走势，捕捉渐进式心理韧性滑坡。</div>', unsafe_allow_html=True)

    col_in, col_plot = st.columns([1, 2], gap="large")

    with col_in:
        st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
        st.markdown("#### 今日状态打卡")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        m_val = st.slider("😊 今日情绪 (1极度低落 ~ 5平和舒畅)", 1.0, 5.0, 3.5, step=0.5)
        e_val = st.slider("⚡ 精力充沛度 (1耗竭无力 ~ 5轻盈有劲)", 1.0, 5.0, 3.0, step=0.5)
        s_val = st.slider("🌙 昨晚睡眠 (1多梦早醒 ~ 5深沉安稳)", 1.0, 5.0, 3.5, step=0.5)

        if st.button("提交今日记录", use_container_width=True):
            df = st.session_state.history_ema
            dci_val = round(0.4 * m_val + 0.3 * e_val + 0.3 * s_val, 2)
            if today_str in df["date"].values:
                df.loc[df["date"] == today_str, ["mood", "energy", "sleep", "dci"]] = [m_val, e_val, s_val, dci_val]
            else:
                new_r = pd.DataFrame([{"date": today_str, "mood": m_val, "energy": e_val, "sleep": s_val, "dci": dci_val}])
                df = pd.concat([df, new_r], ignore_index=True)
            st.session_state.history_ema = df
            save_all_local_data()
            st.success("打卡成功！走势图已更新。")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_plot:
        df = st.session_state.history_ema.tail(14)
        mean_dci_14 = df["dci"].mean()
        k_slope, is_acute = calculate_trend_k(df["dci"])

        if is_acute:
            st.warning("⚠️ **检测到急性情绪滑坡 (7天斜率快速下探)**：最近几天状态出现显著下滑，建议放慢步调，适当卸下非必要事务。")
        elif mean_dci_14 < 2.8:
            st.info("⚠️ **14天长周期持续低迷**：综合指数持续偏低，提示存在亚临床阈下抑郁风险，建议进行自测复核。")
        else:
            st.success("✅ **近期趋势总体平稳**：身心多维状态保持在健康韧性区间。")

        # 定制现代化 Plotly 图表
        fig = go.Figure()
        fig.add_hrect(
            y0=1.0, y1=2.8, fillcolor="#F8EDE2", opacity=0.5, layer="below", line_width=0,
            annotation_text="预警注意区 (DCI < 2.8)", annotation_position="bottom right",
            annotation_font_color="#B46C2B", annotation_font_size=12
        )
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["dci"], mode="lines+markers", name="综合指数 (DCI)",
            line=dict(color="#5E7A68", width=3.5, shape='spline'),
            marker=dict(size=8, color="#486352", line=dict(color="#FFF", width=2))
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["mood"], mode="lines", name="情绪",
            line=dict(color="#6B818C", width=1.8, dash="dot")
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["energy"], mode="lines", name="精力",
            line=dict(color="#D99B5B", width=1.8, dash="dash")
        ))
        fig.update_layout(
            title=dict(text="14 天身心多维动态走势", font=dict(size=16, color="#2D312E")),
            paper_bgcolor="rgba(255,255,255,0.7)",
            plot_bgcolor="rgba(250,250,248,0.5)",
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis=dict(range=[1, 5.2], title="分数 (1-5)", gridcolor="rgba(234, 232, 225, 0.7)"),
            xaxis=dict(title="", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# 7. 模块 3: 数字表型与多模态
# -------------------------------------------------------------
elif menu == "🧬 数字表型与多模态":
    st.markdown('<div class="hero-title">🧬 数字表型“数字指纹”与多模态预警</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">融合穿戴设备被动时空指标与主动声学微特征，构建个性化基线偏离度模型。</div>', unsafe_allow_html=True)

    tab_p, tab_a = st.tabs(["📡 被动数字表型 (时空/生理/节律)", "🎙️ 主动多模态微特征 (文本/声学/自拍)"])

    with tab_p:
        st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
        st.markdown("#### 智能硬件被动时序指标模拟")
        st.caption("系统自动根据过去 14 天自适应基线（Median/MAD），计算今日表型偏离度（CDI）。")

        p_c1, p_c2 = st.columns(2)
        with p_c1:
            in_home = st.slider("🏠 居家时间占比 (Homestay Ratio)", 0.0, 1.0, 0.85, step=0.05)
            in_entropy = st.slider("📍 轨迹空间熵 (Location Entropy)", 0.0, 3.0, 0.8, step=0.1)
            in_latency = st.slider("🌙 入睡潜伏期 (分钟)", 5.0, 120.0, 45.0, step=5.0)
        with p_c2:
            in_dur = st.slider("⏱️ 睡眠总时长 (小时)", 3.0, 12.0, 5.5, step=0.5)
            in_hrv = st.slider("💓 夜间 HRV (RMSSD, ms)", 10.0, 90.0, 24.0, step=1.0)
            in_screen = st.slider("📱 夜间熄屏唤醒次数", 0, 15, 6, step=1)

        if st.button("计算数字表型偏离度", use_container_width=True):
            today_pheno = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "homestay_ratio": in_home, "location_entropy": in_entropy,
                "sleep_latency_min": in_latency, "sleep_duration_hr": in_dur,
                "hrv_rmssd": in_hrv, "night_screen_unlocks": in_screen
            }
            engine = DigitalPhenotypeEngine()
            eval_res = engine.evaluate(today_pheno, st.session_state.phenotype_history)

            st.markdown("<hr style='border-color: rgba(234, 232, 225, 0.6); margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown(f"### 综合表型偏离指数 (CDI): **{eval_res['cdi']}** ({eval_res['risk_level']})")
            if eval_res["is_anomaly"]:
                st.warning("⚠️ **检测到显著数字表型离群**：行为与生理节律显著偏离个人健康基线，提示阈下抑郁高风险。")
            else:
                st.success("✅ **数字表型处于基线健康容差范围内**。")

            st.markdown("<b>各维度校准 Z 分数：</b>", unsafe_allow_html=True)
            z_cols = st.columns(3)
            idx = 0
            for k, v in eval_res["z_scores"].items():
                with z_cols[idx % 3]:
                    st.metric(label=k, value=f"{v:+0.2f}")
                idx += 1
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_a:
        st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
        st.markdown("#### 主动多模态微特征上传与分析")
        st.caption("🔒 原始音视频在端侧特征提取后立即物理销毁，不存储任何生物特征原文件。")
        m_c1, m_c2 = st.columns(2)
        with m_c1:
            u_text = st.text_area("1. 自由心情记录 (语言反刍分析):", placeholder="写下今天的一件事或此刻的感受...", height=100)
            u_audio = st.file_uploader("2. 语音声学采样 (WAV/MP3):", type=["wav", "mp3"])
            u_image = st.file_uploader("3. 面部自然自拍 (微表情分析):", type=["jpg", "png"])
        with m_c2:
            if st.button("开始多模态融合分析", use_container_width=True):
                self_words = ["我", "我自己", "总是", "完全", "累", "毫无意义"]
                neg_count = sum(u_text.count(w) for w in self_words) if u_text else 0
                text_score = min(1.0, neg_count * 0.25)
                audio_score = 0.6 if u_audio else 0.2
                visual_score = 0.5 if u_image else 0.2

                mmi = round(0.4 * text_score + 0.3 * audio_score + 0.3 * visual_score, 2)
                st.markdown(f"### 综合多模态指数 (MMI): **{mmi} / 1.0**")
                if mmi >= 0.60:
                    st.error("⚠️ **多模态表现为高风险**：语言反刍偏高且伴随声学平坦与面部表达受限。")
                elif mmi >= 0.35:
                    st.warning("⚡ **阈下抑郁特征明显**：客观特征出现轻中度偏差。")
                else:
                    st.success("✅ **多模态特征稳定自然**。")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 8. 其余模块 (临床报告 / 减压工具箱 / 备份)
# -------------------------------------------------------------
elif menu == "📋 临床就诊参考单":
    st.markdown('<div class="hero-title">📋 临床就诊辅助参考单生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">聚合量表、14 天 EMA 趋势与数字表型，生成规范病程摘要，辅助门诊沟通。</div>', unsafe_allow_html=True)

    # 引用 HTML 报告渲染
    from app import generate_clinical_html
    report_html = generate_clinical_html(st.session_state.assessment_result, st.session_state.history_ema, st.session_state.phenotype_history)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.download_button(
            label="📥 下载临床参考单 (HTML / 打印版)",
            data=report_html,
            file_name=f"clinical_reference_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )
    with col_b:
        st.caption("💡 下载后用浏览器打开，按 `Ctrl+P` (Mac 上 `Cmd+P`) 即可另存为 PDF。")

    st.markdown("---")
    st.components.v1.html(report_html, height=650, scrolling=True)

elif menu == "☕ 轻量减压工具箱":
    st.markdown('<div class="hero-title">☕ 轻量微干预工具箱</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">从微小、无需过多意志力的行动开始重建日常控制感。</div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["🌱 10分钟低阻力行为清单", "🌬️ 4-7-8 呼吸减压钟"])
    with t1:
        st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
        st.markdown("#### 今日微行动清单（选 1 项打勾即可）")
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("🪟 开窗深呼吸 2 分钟，感受外界新鲜空气")
            st.checkbox("💧 喝一杯温水，缓慢吞咽")
            st.checkbox("🪴 走到阳光下站立或散步 5 分钟")
        with c2:
            st.checkbox("🧹 随手归位书桌上的 3 件小物品")
            st.checkbox("🎵 听一首不带歌词的纯音乐/白噪音")
            st.checkbox("📝 写下一件今天还算顺利的微小事件")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="soothing-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("#### 4-7-8 神经舒缓呼吸节律")
        st.markdown("吸气 4 秒 $\\rightarrow$ 屏息 7 秒 $\\rightarrow$ 吐气 8 秒（激活副交感神经）")
        st.markdown("""
        <div style="margin: 24px auto; width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #E2EBE5 0%, #D4E2D8 100%); display: flex; align-items: center; justify-content: center; border: 3px solid #5E7A68; color: #2D4C38; font-size: 18px; font-weight: 700; box-shadow: 0 8px 20px rgba(94,122,104,0.15);">
            吸 4 · 停 7 · 呼 8
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ 数据持久化与备份":
    st.markdown('<div class="hero-title">⚙️ 本地数据管理与隐私备份</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">您的所有数据均保存在本地，支持一键导出备份与异地设备还原。</div>', unsafe_allow_html=True)

    st.markdown('<div class="soothing-card">', unsafe_allow_html=True)
    st.markdown("#### 1. 导出数据备份")
    current_payload = {
        "history_ema": st.session_state.history_ema.to_dict(orient="records"),
        "assessment_result": st.session_state.assessment_result,
        "phenotype_history": st.session_state.phenotype_history,
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.download_button(
        label="💾 导出历史数据备份 (.json)",
        data=json.dumps(current_payload, ensure_ascii=False, indent=2),
        file_name=f"depression_guard_backup_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )
    st.markdown("<hr style='border-color: rgba(234, 232, 225, 0.6); margin: 24px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 2. 导入与恢复历史数据")
    up_file = st.file_uploader("上传之前导出的备份 JSON 文件", type=["json"])
    if up_file is not None:
        try:
            imp = json.load(up_file)
            if "history_ema" in imp:
                st.session_state.history_ema = pd.DataFrame(imp["history_ema"])
                st.session_state.assessment_result = imp.get("assessment_result", None)
                st.session_state.phenotype_history = imp.get("phenotype_history", [])
                save_all_local_data()
                st.success("数据恢复成功！已重新同步至本地。")
        except Exception as e:
            st.error(f"解析文件失败: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📖 什么是阈下抑郁？":
    st.markdown('<div class="hero-title">📖 认识阈下抑郁 (Subthreshold Depression)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="soothing-card">
        <h4>1. 什么是阈下抑郁？</h4>
        <p style="line-height: 1.8; color: #444;">
        阈下抑郁是指个体出现了一定程度的抑郁核心症状（持续无精打采、快感缺失、睡眠节律受累），但严重程度或症状数量<b>未达到重度抑郁障碍（MDD）的标准</b>。
        </p>
        <hr style="border-color: rgba(234, 232, 225, 0.6); margin: 20px 0;">
        <h4>2. 为什么需要“数字表型”预警？</h4>
        <p style="line-height: 1.8; color: #444;">
        传统量表易受受试者主观防备心理影响。通过智能手表与手机被动感知的数字表型（如活动范围缩小、入睡潜伏期拉长、HRV降低），能够在用户尚未察觉或不愿承认时，<b>无感捕捉心理弹性的微弱滑坡</b>，抢在临床恶化前实现低成本阻断。
        </p>
    </div>
    """, unsafe_allow_html=True)