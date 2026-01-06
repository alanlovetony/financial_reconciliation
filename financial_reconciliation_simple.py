"""
财务对账工具 - 银行流水逐笔核对版 v2
以每笔银行流水为主线，逐笔核对是否匹配业务系统

优化：
1. 增加交易笔数列
2. 现代化UI设计
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="财务对账工具",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 现代化CSS样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main > div { 
        padding: 1.5rem 2rem; 
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* 顶部标题区 */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.85);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* 上传区域 */
    .upload-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #eef2f7;
        margin-bottom: 1.5rem;
    }
    
    .upload-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 统计卡片 */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border: 1px solid #eef2f7;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .stat-card.success {
        border-top: 4px solid #10b981;
        background: linear-gradient(to bottom, #ecfdf5, white);
    }
    
    .stat-card.danger {
        border-top: 4px solid #ef4444;
        background: linear-gradient(to bottom, #fef2f2, white);
    }
    
    .stat-card.warning {
        border-top: 4px solid #f59e0b;
        background: linear-gradient(to bottom, #fffbeb, white);
    }
    
    .stat-card.info {
        border-top: 4px solid #3b82f6;
        background: linear-gradient(to bottom, #eff6ff, white);
    }
    
    .stat-card.purple {
        border-top: 4px solid #8b5cf6;
        background: linear-gradient(to bottom, #f5f3ff, white);
    }
    
    .stat-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a202c;
        line-height: 1.2;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.4rem;
        font-weight: 500;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 表格容器 */
    .table-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin-top: 1rem;
    }
    
    .table-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    .table-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    
    /* 下载按钮 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        width: 100%;
    }
    
    /* 提示信息 */
    .info-banner {
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }
    
    .info-banner p {
        margin: 0;
        color: #1e40af;
        font-weight: 500;
    }
    
    /* 成功/错误提示 */
    .success-banner {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .success-banner .icon { font-size: 2rem; }
    .success-banner .text { 
        font-size: 1.1rem; 
        font-weight: 600; 
        color: #065f46;
        margin-top: 0.5rem;
    }
    
    .error-banner {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# 顶部标题
st.markdown("""
<div class="header-container">
    <h1 class="header-title">💰 财务对账工具</h1>
    <p class="header-subtitle">银行流水逐笔核对 · 每笔流水单独对账 · 一目了然</p>
</div>
""", unsafe_allow_html=True)


def load_yiyun_file(file):
    """加载有益云文件"""
    if file is None:
        return None
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, skiprows=1)
        else:
            df = pd.read_excel(file, skiprows=1)
        return df
    except Exception as e:
        st.error(f"有益云文件读取失败: {str(e)}")
        return None


def load_bank_file(file):
    """加载银行流水文件"""
    if file is None:
        return None
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"银行流水文件读取失败: {str(e)}")
        return None


def extract_biz_date_from_remark(remark, bank_date):
    """从银行附言/用途中提取业务日期"""
    remark = str(remark) if pd.notna(remark) else ''
    
    pattern1 = r'^(\d{2})(\d{2})_'
    match1 = re.search(pattern1, remark.strip())
    if match1:
        month, day = int(match1.group(1)), int(match1.group(2))
        bank_dt = pd.to_datetime(bank_date)
        year = bank_dt.year
        if month == 12 and bank_dt.month == 1:
            year -= 1
        elif month == 1 and bank_dt.month == 12:
            year += 1
        try:
            return pd.to_datetime(f"{year}-{month:02d}-{day:02d}").date()
        except:
            pass
    
    pattern2 = r'(\d{4})(\d{2})(\d{2})至'
    match2 = re.search(pattern2, remark)
    if match2:
        try:
            return pd.to_datetime(f"{match2.group(1)}-{match2.group(2)}-{match2.group(3)}").date()
        except:
            pass
    
    return None


def reconcile_each_bank_row(df_yiyun, df_bank):
    """核心对账逻辑 - 逐笔银行流水核对，增加交易笔数"""
    
    # 处理有益云数据
    df_yiyun = df_yiyun.copy()
    df_yiyun['捐赠时间'] = pd.to_datetime(df_yiyun['捐赠时间'], errors='coerce')
    df_yiyun['业务日期'] = df_yiyun['捐赠时间'].dt.date
    
    # 区分T+1和T+N
    is_gfyh = df_yiyun['捐赠说明'].astype(str).str.contains('GFYH', na=False)
    df_t1 = df_yiyun[~is_gfyh].copy()
    df_tn = df_yiyun[is_gfyh].copy()
    
    # T+1 按日期汇总（包含笔数）
    t1_daily = df_t1.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    t1_daily.columns = ['业务日期', '金额', '笔数']
    t1_dict = {row['业务日期']: {'金额': round(row['金额'], 2), '笔数': int(row['笔数']), '已匹配': False}
               for _, row in t1_daily.iterrows()}
    
    # T+N 按日期汇总（包含笔数）
    tn_daily = df_tn.groupby('业务日期').agg({
        '捐赠金额': 'sum',
        '捐赠项目': 'count'
    }).reset_index()
    tn_daily.columns = ['业务日期', '金额', '笔数']
    tn_dict = {row['业务日期']: {'金额': round(row['金额'], 2), '笔数': int(row['笔数']), '已匹配': False}
               for _, row in tn_daily.iterrows()}
    
    # 处理银行流水
    df_bank = df_bank.copy()
    df_bank['收入'] = pd.to_numeric(df_bank['收入'], errors='coerce').fillna(0)
    df_bank = df_bank[df_bank['收入'] > 0].copy().reset_index(drop=True)
    df_bank['发生时间'] = pd.to_datetime(df_bank['发生时间'], errors='coerce')
    df_bank['到账日期'] = df_bank['发生时间'].dt.date
    df_bank['备注'] = df_bank.apply(
        lambda row: f"{row.get('用途', '')} {row.get('附言', '')}", axis=1
    )
    
    # 逐笔银行流水核对
    results = []
    
    for idx, bank_row in df_bank.iterrows():
        bank_date = bank_row['到账日期']
        bank_amount = round(bank_row['收入'], 2)
        bank_remark = str(bank_row['备注'])
        
        row_data = {
            '序号': idx + 1,
            '到账日期': bank_date,
            '银行金额': bank_amount,
            '银行备注': bank_remark[:40] + '...' if len(bank_remark) > 40 else bank_remark,
            '匹配类型': '-',
            '交易笔数': 0,
            '匹配业务日期': None,
            '系统金额': 0,
            '状态': '❌ 未匹配'
        }
        
        matched = False
        
        # 第一步：尝试匹配 T+1
        t1_biz_date = (pd.to_datetime(bank_date) - timedelta(days=1)).date()
        
        if t1_biz_date in t1_dict and not t1_dict[t1_biz_date]['已匹配']:
            t1_info = t1_dict[t1_biz_date]
            if bank_amount == t1_info['金额']:
                row_data['匹配类型'] = 'T+1'
                row_data['交易笔数'] = t1_info['笔数']
                row_data['匹配业务日期'] = t1_biz_date
                row_data['系统金额'] = t1_info['金额']
                row_data['状态'] = '✅ 匹配'
                t1_dict[t1_biz_date]['已匹配'] = True
                matched = True
        
        # 第二步：尝试匹配 T+N
        if not matched:
            biz_date_from_remark = extract_biz_date_from_remark(bank_remark, bank_date)
            
            if biz_date_from_remark and biz_date_from_remark in tn_dict and not tn_dict[biz_date_from_remark]['已匹配']:
                tn_info = tn_dict[biz_date_from_remark]
                if bank_amount == tn_info['金额']:
                    days_diff = (pd.to_datetime(bank_date) - pd.to_datetime(biz_date_from_remark)).days
                    row_data['匹配类型'] = f'T+{days_diff}'
                    row_data['交易笔数'] = tn_info['笔数']
                    row_data['匹配业务日期'] = biz_date_from_remark
                    row_data['系统金额'] = tn_info['金额']
                    row_data['状态'] = '✅ 匹配'
                    tn_dict[biz_date_from_remark]['已匹配'] = True
                    matched = True
            
            if not matched:
                for days_back in range(2, 31):
                    tn_biz_date = (pd.to_datetime(bank_date) - timedelta(days=days_back)).date()
                    
                    if tn_biz_date in tn_dict and not tn_dict[tn_biz_date]['已匹配']:
                        tn_info = tn_dict[tn_biz_date]
                        if bank_amount == tn_info['金额']:
                            row_data['匹配类型'] = f'T+{days_back}'
                            row_data['交易笔数'] = tn_info['笔数']
                            row_data['匹配业务日期'] = tn_biz_date
                            row_data['系统金额'] = tn_info['金额']
                            row_data['状态'] = '✅ 匹配'
                            tn_dict[tn_biz_date]['已匹配'] = True
                            matched = True
                            break
        
        results.append(row_data)
    
    df_result = pd.DataFrame(results)
    
    # 检查未匹配的业务
    unmatched_biz = []
    
    for biz_date, info in t1_dict.items():
        if not info['已匹配']:
            unmatched_biz.append({
                '类型': 'T+1',
                '业务日期': biz_date,
                '预计到账日期': (pd.to_datetime(biz_date) + timedelta(days=1)).date(),
                '系统金额': info['金额'],
                '交易笔数': info['笔数'],
                '状态': '❌ 银行未到账'
            })
    
    for biz_date, info in tn_dict.items():
        if not info['已匹配']:
            unmatched_biz.append({
                '类型': 'T+N',
                '业务日期': biz_date,
                '预计到账日期': '-',
                '系统金额': info['金额'],
                '交易笔数': info['笔数'],
                '状态': '❌ 银行未到账'
            })
    
    df_unmatched = pd.DataFrame(unmatched_biz)
    
    # 按项目汇总
    df_project = df_yiyun.groupby(['捐赠项目', '业务日期']).agg({
        '捐赠金额': 'sum'
    }).reset_index()
    df_project.columns = ['项目', '日期', '金额']
    
    return df_result, df_unmatched, df_project, df_bank, len(df_t1), len(df_tn)


def create_project_pivot(df_project):
    """创建项目透视表"""
    df_project = df_project.copy()
    df_project['日期'] = pd.to_datetime(df_project['日期'])
    df_project['日期显示'] = df_project['日期'].dt.strftime('%m/%d')
    
    pivot = df_project.pivot_table(
        index='项目',
        columns='日期显示',
        values='金额',
        aggfunc='sum',
        fill_value=0
    )
    
    pivot['合计'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('合计', ascending=False)
    
    return pivot


def to_excel(df_result, df_unmatched, df_project_pivot, df_yiyun, df_bank):
    """导出Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name='银行流水逐笔对账')
        
        df_unmatched_bank = df_result[df_result['状态'].str.contains('未匹配')]
        if len(df_unmatched_bank) > 0:
            df_unmatched_bank.to_excel(writer, index=False, sheet_name='未匹配银行流水')
        
        if len(df_unmatched) > 0:
            df_unmatched.to_excel(writer, index=False, sheet_name='未到账业务')
        
        df_project_pivot.to_excel(writer, sheet_name='项目明细')
        df_yiyun.to_excel(writer, index=False, sheet_name='有益云原始数据')
        df_bank.to_excel(writer, index=False, sheet_name='银行流水原始数据')
    
    return output.getvalue()


# ==================== 主界面 ====================

# 上传区域
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="upload-container">
        <div class="upload-title">📄 有益云数据</div>
    </div>
    """, unsafe_allow_html=True)
    file_yiyun = st.file_uploader("上传有益云文件", type=['csv', 'xlsx', 'xls'], key='yiyun', label_visibility="collapsed")
    if file_yiyun:
        df_yiyun_preview = load_yiyun_file(file_yiyun)
        file_yiyun.seek(0)
        if df_yiyun_preview is not None:
            is_gfyh = df_yiyun_preview['捐赠说明'].astype(str).str.contains('GFYH', na=False)
            st.success(f"✅ 共 {len(df_yiyun_preview)} 条 | T+1: {(~is_gfyh).sum()} 条 | T+N: {is_gfyh.sum()} 条")

with col2:
    st.markdown("""
    <div class="upload-container">
        <div class="upload-title">🏦 银行流水</div>
    </div>
    """, unsafe_allow_html=True)
    file_bank = st.file_uploader("上传银行流水", type=['csv', 'xlsx', 'xls'], key='bank', label_visibility="collapsed")
    if file_bank:
        df_bank_preview = load_bank_file(file_bank)
        file_bank.seek(0)
        if df_bank_preview is not None:
            income_count = (pd.to_numeric(df_bank_preview['收入'], errors='coerce').fillna(0) > 0).sum()
            st.success(f"✅ 共 {income_count} 笔收入记录")

# 对账规则
with st.expander("📖 查看对账规则", expanded=False):
    st.markdown("""
    **匹配规则：**
    - **T+1**（不带GFYH）：银行到账日期 - 1天 = 业务日期
    - **T+N**（带GFYH）：从银行附言提取业务日期，或倒查过去30天
    - **匹配条件**：金额必须 **完全相等** 才算匹配成功
    """)

# 开始对账
if file_yiyun and file_bank:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        run_btn = st.button("🔍 开始对账", use_container_width=True, type="primary")
    
    if run_btn:
        with st.spinner("正在逐笔核对中..."):
            df_yiyun = load_yiyun_file(file_yiyun)
            df_bank = load_bank_file(file_bank)
            
            df_result, df_unmatched, df_project, df_bank_processed, t1_count, tn_count = reconcile_each_bank_row(df_yiyun, df_bank)
            pivot_df = create_project_pivot(df_project)
            
            # 统计
            total_bank_rows = len(df_result)
            matched_rows = len(df_result[df_result['状态'].str.contains('✅')])
            unmatched_bank_rows = total_bank_rows - matched_rows
            unmatched_biz_count = len(df_unmatched)
            
            total_bank_amount = df_result['银行金额'].sum()
            matched_amount = df_result[df_result['状态'].str.contains('✅')]['银行金额'].sum()
            unmatched_bank_amount = total_bank_amount - matched_amount
            unmatched_biz_amount = df_unmatched['系统金额'].sum() if len(df_unmatched) > 0 else 0
            
            # 统计卡片
            st.markdown("### 📊 对账结果")
            
            st.markdown(f"""
            <div class="stats-grid">
                <div class="stat-card success">
                    <div class="stat-icon">✅</div>
                    <div class="stat-value">{matched_rows}</div>
                    <div class="stat-label">匹配成功</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-icon">❌</div>
                    <div class="stat-value">{unmatched_bank_rows}</div>
                    <div class="stat-label">未匹配流水</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-value">{unmatched_biz_count}</div>
                    <div class="stat-label">未到账业务</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-icon">💰</div>
                    <div class="stat-value">¥{matched_amount:,.0f}</div>
                    <div class="stat-label">已匹配金额</div>
                </div>
                <div class="stat-card purple">
                    <div class="stat-icon">🏦</div>
                    <div class="stat-value">¥{unmatched_bank_amount:,.0f}</div>
                    <div class="stat-label">未匹配金额</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-icon">📋</div>
                    <div class="stat-value">¥{unmatched_biz_amount:,.0f}</div>
                    <div class="stat-label">未到账金额</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tab展示
            tab1, tab2, tab3, tab4 = st.tabs([
                f"📋 逐笔核对 ({total_bank_rows})", 
                f"❌ 未匹配 ({unmatched_bank_rows})", 
                f"⚠️ 未到账 ({unmatched_biz_count})",
                "📊 项目明细"
            ])
            
            with tab1:
                st.markdown("""
                <div class="table-title">银行流水逐笔对账结果</div>
                <div class="table-subtitle">每笔银行流水一行，包含匹配类型和对应的业务交易笔数</div>
                """, unsafe_allow_html=True)
                
                display_df = df_result.copy()
                display_df['到账日期'] = pd.to_datetime(display_df['到账日期']).dt.strftime('%Y-%m-%d')
                display_df['匹配业务日期'] = pd.to_datetime(display_df['匹配业务日期']).dt.strftime('%Y-%m-%d')
                display_df['匹配业务日期'] = display_df['匹配业务日期'].fillna('-')
                
                def highlight_status(row):
                    if '✅' in str(row['状态']):
                        return ['background-color: #dcfce7; color: #166534;'] * len(row)
                    else:
                        return ['background-color: #fee2e2; color: #991b1b;'] * len(row)
                
                styled_df = display_df.style.apply(highlight_status, axis=1).format({
                    '银行金额': '¥{:,.2f}',
                    '系统金额': '¥{:,.2f}'
                })
                
                st.dataframe(styled_df, use_container_width=True, height=500)
            
            with tab2:
                df_unmatched_bank = df_result[df_result['状态'].str.contains('未匹配')].copy()
                
                if len(df_unmatched_bank) == 0:
                    st.markdown("""
                    <div class="success-banner">
                        <div class="icon">🎉</div>
                        <div class="text">太棒了！所有银行流水都已匹配成功！</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-banner">
                        <p>❌ 共有 <strong>{len(df_unmatched_bank)}</strong> 笔银行流水未匹配，合计 <strong>¥{df_unmatched_bank['银行金额'].sum():,.2f}</strong></p>
                        <p style="font-size: 0.9rem; color: #7f1d1d; margin-top: 0.5rem;">这些银行收款在有益云系统中没有找到对应的业务记录</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    df_unmatched_bank['到账日期'] = pd.to_datetime(df_unmatched_bank['到账日期']).dt.strftime('%Y-%m-%d')
                    st.dataframe(df_unmatched_bank.style.format({
                        '银行金额': '¥{:,.2f}',
                        '系统金额': '¥{:,.2f}'
                    }), use_container_width=True)
            
            with tab3:
                if len(df_unmatched) == 0:
                    st.markdown("""
                    <div class="success-banner">
                        <div class="icon">🎉</div>
                        <div class="text">太棒了！所有业务都已到账！</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ 共有 {len(df_unmatched)} 条业务未到账，合计 ¥{unmatched_biz_amount:,.2f}")
                    
                    display_unmatched = df_unmatched.copy()
                    display_unmatched['业务日期'] = pd.to_datetime(display_unmatched['业务日期']).dt.strftime('%Y-%m-%d')
                    display_unmatched['预计到账日期'] = display_unmatched['预计到账日期'].apply(
                        lambda x: pd.to_datetime(x).strftime('%Y-%m-%d') if x != '-' else '-'
                    )
                    
                    st.dataframe(display_unmatched.style.format({
                        '系统金额': '¥{:,.2f}'
                    }), use_container_width=True)
            
            with tab4:
                st.markdown("""
                <div class="table-title">项目每日捐赠明细</div>
                <div class="table-subtitle">按项目分组，展示每天的捐赠金额</div>
                """, unsafe_allow_html=True)
                
                st.dataframe(pivot_df.style.format('{:,.2f}'), use_container_width=True, height=500)
                
                st.info(f"📌 共 **{len(pivot_df)}** 个项目，总金额 **¥{pivot_df['合计'].sum():,.2f}**")
            
            # 下载按钮
            st.markdown("---")
            
            col_dl = st.columns([1, 2, 1])
            with col_dl[1]:
                excel_data = to_excel(df_result, df_unmatched, pivot_df, df_yiyun, df_bank_processed)
                
                st.download_button(
                    label="📥 下载完整对账报告 (Excel)",
                    data=excel_data,
                    file_name=f"对账报告_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
