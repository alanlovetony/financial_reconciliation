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
    
    /* Streamlit 默认顶部留白极大，强制去除 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
    .main > div { 
        padding: 0 2rem; 
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* 顶部标题区 */
    /* 顶部标题区 */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .header-title {
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 0.3rem;
        font-weight: 500;
        text-align: center;
    }
    
    /* 上传区域 */
    .upload-container {
        background: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eef2f7;
        margin-bottom: 0.5rem;
    }
    
    .upload-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* 统计卡片 */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.6rem;
        margin: 0.8rem 0;
    }
    
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 0.8rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
    
    /* 自定义 Tab 按钮样式 */
    div[data-testid="column"] button {
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    div[data-testid="column"] button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    div[data-testid="column"] button[kind="secondary"] {
        background: white;
        color: #64748b;
        border-color: #e2e8f0;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover {
        border-color: #667eea;
        color: #667eea;
        transform: translateY(-1px);
    }
    
    /* Form 样式优化 */
    .stForm {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    /* 日期输入框样式 */
    .stDateInput > div > div {
        border-radius: 8px;
    }
    
    /* 表格工具栏按钮始终显示 */
    div[data-testid="stDataFrameResizable"] div[data-testid="stElementToolbar"] {
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }
    
    div[data-testid="stDataFrameResizable"] div[data-testid="stElementToolbar"] button {
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* 确保工具栏容器始终可见 */
    div[data-testid="stElementToolbarContainer"] {
        opacity: 1 !important;
        visibility: visible !important;
    }
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
    """核心对账逻辑 - 逐笔银行流水核对，增加交易笔数，支持月捐968结尾特殊匹配，并追踪明细ID"""
    
    # 处理有益云数据 - 添加唯一ID用于追踪
    df_yiyun = df_yiyun.copy()
    df_yiyun['_yiyun_id'] = range(len(df_yiyun))  # 添加唯一ID
    df_yiyun['捐赠时间'] = pd.to_datetime(df_yiyun['捐赠时间'], errors='coerce')
    df_yiyun['业务日期'] = df_yiyun['捐赠时间'].dt.date
    
    # 区分T+1和T+N
    is_gfyh = df_yiyun['捐赠说明'].astype(str).str.contains('GFYH', na=False)
    df_t1 = df_yiyun[~is_gfyh].copy()
    df_tn = df_yiyun[is_gfyh].copy()
    
    # 在T+1中识别月捐
    df_t1['是否月捐'] = df_t1['捐赠说明'].astype(str).str.contains('月捐', na=False)
    df_t1_monthly = df_t1[df_t1['是否月捐']].copy()
    df_t1_regular = df_t1[~df_t1['是否月捐']].copy()
    
    # T+1 月捐按日期汇总 - 保存ID列表
    t1_monthly_dict = {}
    for biz_date, group in df_t1_monthly.groupby('业务日期'):
        t1_monthly_dict[biz_date] = {
            '金额': round(group['捐赠金额'].sum(), 2),
            '笔数': len(group),
            '已匹配': False,
            'ids': group['_yiyun_id'].tolist()
        }
    
    # T+1 常规按日期汇总 - 保存ID列表
    t1_regular_dict = {}
    for biz_date, group in df_t1_regular.groupby('业务日期'):
        t1_regular_dict[biz_date] = {
            '金额': round(group['捐赠金额'].sum(), 2),
            '笔数': len(group),
            '已匹配': False,
            'ids': group['_yiyun_id'].tolist()
        }
    
    # T+1 总汇总 - 保存ID列表
    t1_dict = {}
    for biz_date, group in df_t1.groupby('业务日期'):
        t1_dict[biz_date] = {
            '金额': round(group['捐赠金额'].sum(), 2),
            '笔数': len(group),
            '已匹配': False,
            'ids': group['_yiyun_id'].tolist()
        }
    
    # T+N 按日期汇总 - 保存ID列表
    tn_dict = {}
    for biz_date, group in df_tn.groupby('业务日期'):
        tn_dict[biz_date] = {
            '金额': round(group['捐赠金额'].sum(), 2),
            '笔数': len(group),
            '已匹配': False,
            'ids': group['_yiyun_id'].tolist()
        }
    
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
        bank_fuyan = str(bank_row.get('附言', ''))
        
        row_data = {
            '序号': idx + 1,
            '到账日期': bank_date,
            '银行金额': bank_amount,
            '银行备注': bank_remark[:40] + '...' if len(bank_remark) > 40 else bank_remark,
            '匹配类型': '-',
            '交易笔数': 0,
            '匹配业务日期': None,
            '系统金额': 0,
            '状态': '❌ 未匹配',
            '_matched_ids': []  # 新增：记录匹配的有益云ID列表
        }
        
        matched = False
        
        # 第一步：尝试匹配 T+1
        t1_biz_date = (pd.to_datetime(bank_date) - timedelta(days=1)).date()
        
        # 检查是否968结尾（月捐汇总）
        is_monthly_968 = re.search(r'968\s*$', bank_fuyan.strip())
        
        if is_monthly_968:
            # 优先匹配月捐
            if t1_biz_date in t1_monthly_dict and not t1_monthly_dict[t1_biz_date]['已匹配']:
                monthly_info = t1_monthly_dict[t1_biz_date]
                if bank_amount == monthly_info['金额']:
                    row_data['匹配类型'] = 'T+1(月捐)'
                    row_data['交易笔数'] = monthly_info['笔数']
                    row_data['匹配业务日期'] = t1_biz_date
                    row_data['系统金额'] = monthly_info['金额']
                    row_data['状态'] = '✅ 匹配'
                    row_data['_matched_ids'] = monthly_info['ids']  # 记录ID
                    t1_monthly_dict[t1_biz_date]['已匹配'] = True
                    # 同时标记总汇总已匹配
                    if t1_biz_date in t1_dict:
                        # 如果只有月捐，标记整体已匹配
                        if t1_biz_date not in t1_regular_dict or t1_regular_dict.get(t1_biz_date, {}).get('金额', 0) == 0:
                            t1_dict[t1_biz_date]['已匹配'] = True
                    matched = True
        else:
            # 非968结尾，匹配常规T+1
            if t1_biz_date in t1_regular_dict and not t1_regular_dict[t1_biz_date]['已匹配']:
                regular_info = t1_regular_dict[t1_biz_date]
                if bank_amount == regular_info['金额']:
                    row_data['匹配类型'] = 'T+1'
                    row_data['交易笔数'] = regular_info['笔数']
                    row_data['匹配业务日期'] = t1_biz_date
                    row_data['系统金额'] = regular_info['金额']
                    row_data['状态'] = '✅ 匹配'
                    row_data['_matched_ids'] = regular_info['ids']  # 记录ID
                    t1_regular_dict[t1_biz_date]['已匹配'] = True
                    # 检查该日期的月捐是否也已匹配
                    if t1_biz_date in t1_dict:
                        monthly_matched = t1_monthly_dict.get(t1_biz_date, {}).get('已匹配', True)
                        if monthly_matched or t1_biz_date not in t1_monthly_dict:
                            t1_dict[t1_biz_date]['已匹配'] = True
                    matched = True
        
        # 如果上面的细分匹配失败，尝试用总金额匹配（向后兼容）
        if not matched and t1_biz_date in t1_dict and not t1_dict[t1_biz_date]['已匹配']:
            t1_info = t1_dict[t1_biz_date]
            if bank_amount == t1_info['金额']:
                row_data['匹配类型'] = 'T+1'
                row_data['交易笔数'] = t1_info['笔数']
                row_data['匹配业务日期'] = t1_biz_date
                row_data['系统金额'] = t1_info['金额']
                row_data['状态'] = '✅ 匹配'
                row_data['_matched_ids'] = t1_info['ids']  # 记录ID
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
                    row_data['_matched_ids'] = tn_info['ids']  # 记录ID
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
                            row_data['_matched_ids'] = tn_info['ids']  # 记录ID
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
    
    # 返回时也返回带ID的有益云数据
    return df_result, df_unmatched, df_project, df_bank, len(df_t1), len(df_tn), df_yiyun


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
            t1_count = (~is_gfyh).sum()
            tn_count = is_gfyh.sum()
            # 统计T+1中的月捐数量
            is_monthly = df_yiyun_preview[~is_gfyh]['捐赠说明'].astype(str).str.contains('月捐', na=False)
            monthly_count = is_monthly.sum()
            st.success(f"✅ 共 {len(df_yiyun_preview)} 条 | T+1: {t1_count} 条 (月捐: {monthly_count} 条) | T+N: {tn_count} 条")

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
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        run_btn = st.button("🔍 开始对账", use_container_width=True, type="primary")
    
    if run_btn:
        with st.spinner("正在逐笔核对中..."):
            df_yiyun = load_yiyun_file(file_yiyun)
            df_bank = load_bank_file(file_bank)
            
            df_result, df_unmatched, df_project, df_bank_processed, t1_count, tn_count, df_yiyun_with_id = reconcile_each_bank_row(df_yiyun, df_bank)
            pivot_df = create_project_pivot(df_project)
            
            # 保存到 session_state
            st.session_state.reconcile_done = True
            st.session_state.df_result = df_result
            st.session_state.df_unmatched = df_unmatched
            st.session_state.df_project = df_project
            st.session_state.df_bank_processed = df_bank_processed
            st.session_state.pivot_df = pivot_df
            st.session_state.t1_count = t1_count
            st.session_state.tn_count = tn_count
            st.session_state.df_yiyun = df_yiyun
            st.session_state.df_yiyun_with_id = df_yiyun_with_id  # 保存带ID的版本
            st.session_state.df_bank = df_bank
            
            # 对账完成后跳转到第一个页签
            st.query_params["tab"] = "0"
            st.rerun()

# 显示对账结果（从 session_state 读取）
if st.session_state.get('reconcile_done', False):
    df_result = st.session_state.df_result
    df_unmatched = st.session_state.df_unmatched
    df_project = st.session_state.df_project
    df_bank_processed = st.session_state.df_bank_processed
    pivot_df = st.session_state.pivot_df
    t1_count = st.session_state.t1_count
    tn_count = st.session_state.tn_count
    df_yiyun = st.session_state.df_yiyun
    df_bank = st.session_state.df_bank
    
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
    
    # Tab展示 - 使用 query params 记住当前选中的 tab
    # 从 URL 参数获取当前 tab，如果没有则默认为 0
    query_params = st.query_params
    default_tab = int(query_params.get("tab", 0))
    
    tab_names = [
        f"📋 逐笔核对 ({total_bank_rows})", 
        f"❌ 未匹配 ({unmatched_bank_rows})", 
        f"⚠️ 未到账 ({unmatched_biz_count})",
        "📊 项目明细",
        "📅 每日汇总"
    ]
    
    # 为每个 tab 创建一个按钮来切换
    tab_cols = st.columns(5)
    selected_tab = default_tab
    
    for idx, (col, name) in enumerate(zip(tab_cols, tab_names)):
        with col:
            if st.button(name, key=f"tab_btn_{idx}", use_container_width=True, 
                        type="primary" if idx == default_tab else "secondary"):
                selected_tab = idx
                st.query_params["tab"] = str(idx)
                st.rerun()
    
    st.markdown("---")
    
    # 根据选中的 tab 显示内容
    if selected_tab == 0:
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
    
    elif selected_tab == 1:
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
    
    elif selected_tab == 2:
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
    
    elif selected_tab == 3:
        st.markdown("""
        <div class="table-title">项目每日捐赠明细</div>
        <div class="table-subtitle">按项目分组，展示每天的捐赠金额</div>
        """, unsafe_allow_html=True)
        
        st.dataframe(pivot_df.style.format('{:,.2f}'), use_container_width=True, height=500)
        
        st.info(f"📌 共 **{len(pivot_df)}** 个项目，总金额 **¥{pivot_df['合计'].sum():,.2f}**")
    
    elif selected_tab == 4:
        st.markdown("""
        <div class="table-title">📅 每日对账匹配汇总</div>
        <div class="table-subtitle">按银行到账日期筛选，查看该日到账的所有匹配业务明细</div>
        """, unsafe_allow_html=True)
        
        # 准备数据 - 使用对账结果，只显示匹配成功的记录
        df_matched = df_result[df_result['状态'].str.contains('✅')].copy()
        
        if len(df_matched) == 0:
            st.warning("⚠️ 没有匹配成功的记录")
        else:
            # 确保到账日期是日期类型
            df_matched['到账日期'] = pd.to_datetime(df_matched['到账日期'], errors='coerce').dt.date
            
            # 获取日期范围（基于银行到账日期）
            min_date = df_matched['到账日期'].min()
            max_date = df_matched['到账日期'].max()
            
            # 初始化 session_state
            if 'daily_start_date' not in st.session_state:
                st.session_state.daily_start_date = min_date
            if 'daily_end_date' not in st.session_state:
                st.session_state.daily_end_date = max_date
            
            # 使用 form 来避免每次输入都刷新
            with st.form(key='date_filter_form'):
                st.markdown("##### 📆 选择银行到账日期范围")
                col_date1, col_date2, col_date3 = st.columns([3, 3, 2])
                with col_date1:
                    start_date = st.date_input(
                        "开始日期", 
                        value=st.session_state.daily_start_date, 
                        min_value=min_date, 
                        max_value=max_date
                    )
                    
                with col_date2:
                    end_date = st.date_input(
                        "结束日期", 
                        value=st.session_state.daily_end_date, 
                        min_value=min_date, 
                        max_value=max_date
                    )
                
                with col_date3:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    submit_button = st.form_submit_button("🔍 查询统计", use_container_width=True, type="primary")
                
                if submit_button:
                    st.session_state.daily_start_date = start_date
                    st.session_state.daily_end_date = end_date
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 使用 session_state 中的日期进行筛选
            start_date = st.session_state.daily_start_date
            end_date = st.session_state.daily_end_date
            
            # 筛选数据 - 按银行到账日期
            df_filtered = df_matched[(df_matched['到账日期'] >= start_date) & (df_matched['到账日期'] <= end_date)]
            
            if len(df_filtered) == 0:
                st.warning("⚠️ 所选日期范围内没有匹配成功的记录")
            else:
                # 获取所有匹配的有益云ID
                all_matched_ids = []
                for ids_list in df_filtered['_matched_ids']:
                    if isinstance(ids_list, list):
                        all_matched_ids.extend(ids_list)
                
                # 从带ID的有益云数据中精确提取匹配的记录
                df_yiyun_with_id = st.session_state.get('df_yiyun_with_id', df_yiyun)
                df_yiyun_matched = df_yiyun_with_id[df_yiyun_with_id['_yiyun_id'].isin(all_matched_ids)].copy()
                
                # 显示统计信息 - 使用银行流水记录的准确数据
                total_amount = df_filtered['银行金额'].sum()
                total_count = df_filtered['交易笔数'].sum()  # 使用交易笔数总和
                total_days = (end_date - start_date).days + 1
                bank_records = len(df_filtered)  # 银行流水笔数
                
                st.markdown("##### 📊 统计概览")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("💰 匹配金额", f"¥{total_amount:,.2f}")
                with col_stat2:
                    st.metric("📝 交易笔数", f"{int(total_count):,}")
                with col_stat3:
                    st.metric("🏦 银行流水", f"{bank_records}")
                with col_stat4:
                    st.metric("📅 天数", f"{total_days}")
                
                st.markdown("---")
                
                # 按项目汇总
                if len(df_yiyun_matched) > 0:
                    project_summary = df_yiyun_matched.groupby('捐赠项目').agg({
                        '捐赠金额': 'sum',
                        '捐赠时间': 'count'
                    }).reset_index()
                    project_summary.columns = ['捐赠项目', '捐赠金额', '笔数']
                    project_summary = project_summary.sort_values('捐赠金额', ascending=False)
                    
                    # 添加合计行
                    total_row = pd.DataFrame([{
                        '捐赠项目': '总计',
                        '捐赠金额': project_summary['捐赠金额'].sum(),
                        '笔数': project_summary['笔数'].sum()
                    }])
                    project_summary_with_total = pd.concat([project_summary, total_row], ignore_index=True)
                    
                    # 显示项目汇总表
                    st.markdown("##### 📋 项目汇总明细")
                    
                    # 设置表格样式，所有列左对齐
                    styled_table = project_summary_with_total.style.format({
                        '捐赠金额': '¥{:,.2f}',
                        '笔数': '{:.0f}'
                    }).set_properties(**{
                        'text-align': 'left'
                    }).set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'left')]},
                        {'selector': 'td', 'props': [('text-align', 'left')]}
                    ]).apply(lambda row: ['background-color: #f0f9ff; font-weight: bold;'] * len(row) 
                            if row['捐赠项目'] == '总计' else [''] * len(row), axis=1)
                    
                    st.dataframe(
                        styled_table,
                        use_container_width=True,
                        height=min(600, (len(project_summary_with_total) + 1) * 35 + 38)
                    )
                    
                    # 显示有益云匹配明细清单（保持有益云原始字段）
                    st.markdown("---")
                    st.markdown(f"##### 📝 捐赠明细清单（共 {int(total_count)} 笔）")
                    
                    # 准备明细数据 - 显示有益云的原始字段，移除内部ID列
                    detail_df = df_yiyun_matched.drop(columns=['_yiyun_id', '业务日期'], errors='ignore').copy()
                    detail_df = detail_df.sort_values('捐赠时间', ascending=False)
                    
                    # 格式化显示
                    detail_display = detail_df.copy()
                    detail_display['捐赠时间'] = pd.to_datetime(detail_display['捐赠时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 设置明细表格样式，所有列左对齐
                    styled_detail = detail_display.style.format({
                        '捐赠金额': '¥{:,.2f}'
                    }).set_properties(**{
                        'text-align': 'left'
                    }).set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'left')]},
                        {'selector': 'td', 'props': [('text-align', 'left')]}
                    ])
                    
                    st.dataframe(
                        styled_detail,
                        use_container_width=True,
                        height=500
                    )
                    
                    # 导出功能 - 按日期分sheet
                    st.markdown("---")
                    st.markdown("##### 📥 导出数据")
                    
                    # 生成按日期分sheet的Excel
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # 获取日期范围内的所有日期
                        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
                        
                        for single_date in date_range:
                            single_date_obj = single_date.date()
                            
                            # 筛选该日期的匹配记录
                            df_date_matched = df_matched[df_matched['到账日期'] == single_date_obj]
                            
                            if len(df_date_matched) > 0:
                                # 获取该日期所有匹配的有益云ID
                                date_matched_ids = []
                                for ids_list in df_date_matched['_matched_ids']:
                                    if isinstance(ids_list, list):
                                        date_matched_ids.extend(ids_list)
                                
                                # 从带ID的有益云数据中精确提取该日期匹配的记录
                                df_yiyun_with_id = st.session_state.get('df_yiyun_with_id', df_yiyun)
                                df_date_yiyun = df_yiyun_with_id[df_yiyun_with_id['_yiyun_id'].isin(date_matched_ids)].copy()
                                
                                if len(df_date_yiyun) > 0:
                                    # 按项目汇总
                                    date_project_summary = df_date_yiyun.groupby('捐赠项目').agg({
                                        '捐赠金额': 'sum',
                                        '捐赠时间': 'count'
                                    }).reset_index()
                                    date_project_summary.columns = ['项目名称', '金额', '笔数']
                                    date_project_summary = date_project_summary.sort_values('金额', ascending=False)
                                    
                                    # 添加合计行
                                    date_total = pd.DataFrame([{
                                        '项目名称': '合计',
                                        '金额': date_project_summary['金额'].sum(),
                                        '笔数': date_project_summary['笔数'].sum()
                                    }])
                                    date_project_with_total = pd.concat([date_project_summary, date_total], ignore_index=True)
                                    
                                    # Sheet名称：使用日期格式 MM-DD
                                    sheet_name = single_date.strftime('%m-%d')
                                    
                                    # 写入项目透视表（放在前面）
                                    date_project_with_total.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                                    
                                    # 获取worksheet对象
                                    worksheet = writer.sheets[sheet_name]
                                    start_row = len(date_project_with_total) + 2  # 透视表后空一行
                                    
                                    # 写入明细数据（移除_yiyun_id列）
                                    df_date_yiyun_export = df_date_yiyun.drop(columns=['_yiyun_id'], errors='ignore').sort_values('捐赠时间', ascending=False)
                                    
                                    # 将可能被识别为数字的列转换为字符串（避免科学计数法）
                                    text_columns = ['组织ID', '捐赠人', '联系电话', '捐赠说明', '捐赠id', '订单id', '发票号码', '商户号', '一起捐Id']
                                    for col in text_columns:
                                        if col in df_date_yiyun_export.columns:
                                            # 处理NaN和数字格式
                                            def format_text_value(x):
                                                if pd.isna(x):
                                                    return ''
                                                # 转换为字符串
                                                x_str = str(x)
                                                if x_str.lower() == 'nan':
                                                    return ''
                                                # 如果包含科学计数法标记
                                                if 'e+' in x_str.lower() or 'e-' in x_str.lower():
                                                    try:
                                                        # 转换为浮点数再转为整数字符串
                                                        return format(int(float(x)), 'd')
                                                    except:
                                                        return x_str
                                                # 如果是浮点数格式（如 8000081582.0），转换为整数字符串
                                                if '.' in x_str:
                                                    try:
                                                        float_val = float(x_str)
                                                        if float_val == int(float_val):
                                                            return str(int(float_val))
                                                    except:
                                                        pass
                                                return x_str
                                            
                                            df_date_yiyun_export[col] = df_date_yiyun_export[col].apply(format_text_value)
                                    
                                    df_date_yiyun_export.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
                                    
                                    # 设置文本列格式为文本（防止科学计数法）
                                    from openpyxl.styles import numbers
                                    for col_idx, col_name in enumerate(df_date_yiyun_export.columns, start=1):
                                        if col_name in text_columns:
                                            col_letter = chr(64 + col_idx)  # A=65, B=66, etc.
                                            for row_idx in range(start_row + 2, start_row + 2 + len(df_date_yiyun_export)):
                                                cell = worksheet[f'{col_letter}{row_idx}']
                                                cell.number_format = '@'  # @ 表示文本格式
                    
                    output.seek(0)
                    
                    # 下载按钮
                    file_name = f"每日汇总_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.xlsx"
                    st.download_button(
                        label="📥 下载按日期分sheet的Excel",
                        data=output.getvalue(),
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    st.info(f"💡 导出文件包含 {len([d for d in date_range if d.date() in df_matched['到账日期'].values])} 个日期的数据，每个日期一个sheet页签")
                    
                else:
                    st.warning("⚠️ 没有找到匹配的有益云数据")

