import streamlit as st
import opendartreader
import pandas as pd
import plotly.express as px

st.title("📊 기업 영업이익 추이 조회")

DART_API_KEY = st.secrets["DART_API_KEY"]  # Streamlit secrets에 저장
dart = OpenDartReader(DART_API_KEY)

company_name = st.text_input("기업명을 입력하세요", placeholder="예: 삼성전자")

if company_name:
    with st.spinner("데이터 조회 중..."):
        try:
            # 기업 코드 검색
            corp_code = dart.find_corp_code(company_name)
            
            # 최근 5년 재무 데이터
            results = []
            for year in range(2020, 2025):
                try:
                    fin = dart.finstate(corp_code, year, reprt_code='11011')
                    if fin is not None:
                        op = fin[fin['account_nm'] == '영업이익']
                        if not op.empty:
                            val = int(op['thstrm_amount'].values[0].replace(',', ''))
                            results.append({'연도': year, '영업이익(억원)': val // 100000000})
                except:
                    continue
            
            if results:
                df = pd.DataFrame(results)
                fig = px.line(df, x='연도', y='영업이익(억원)', 
                              title=f"{company_name} 영업이익 추이",
                              markers=True)
                st.plotly_chart(fig)
                st.dataframe(df)
            else:
                st.warning("데이터를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
