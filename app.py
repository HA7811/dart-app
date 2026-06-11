import streamlit as st
import OpenDartReader
import pandas as pd

# 1. 웹앱 제목 설정
st.title("📊 기업 영업이익 추이 검색기")
st.markdown("Open DART API를 활용해 최근 3개년 영업이익을 보여줍니다.")

# 2. 사이드바에서 API 키 입력받기 (보안을 위해 비밀번호 형태로 입력)
api_key = st.sidebar.text_input("Open DART API Key를 입력하세요", type="password")

# 3. 메인 화면: 기업명 입력창
company_name = st.text_input("조회할 기업명을 입력하세요 (예: 삼성전자, 현대자동차)")

# 4. 조회 버튼을 누르면 실행
if st.button("영업이익 추이 조회하기"):
    if not api_key:
        st.error("왼쪽 사이드바에 Open DART API Key를 입력해주세요!")
    elif not company_name:
        st.warning("기업명을 입력해주세요.")
    else:
        with st.spinner("DART에서 데이터를 가져오는 중입니다..."):
            try:
                # OpenDartReader 실행
                dart = OpenDartReader(api_key)
                
                # 최근 3개년도 설정 (2023, 2024, 2025)
                years = [2023, 2024, 2025]
                results = []
                
                for year in years:
                    # 정기재무제표 데이터 가져오기
                    df = dart.finstate(company_name, year)
                    
                    if df is not None and not df.empty:
                        # '영업이익' 항목만 필터링 (연결재무제표(CFS) 우선, 없으면 별도(OFS))
                        op_df = df[(df['account_nm'] == '영업이익') & (df['fs_div'] == 'CFS')]
                        if op_df.empty:
                            op_df = df[(df['account_nm'] == '영업이익') & (df['fs_div'] == 'OFS')]
                        
                        if not op_df.empty:
                            # 금액 추출 및 숫자로 변환
                            amount_str = op_df.iloc[0]['thstrm_amount']
                            amount = int(amount_str.replace(',', ''))
                            
                            # 보기 좋게 '억 원' 단위로 변환
                            amount_hundred_mil = round(amount / 100000000, 1)
                            
                            results.append({
                                "연도": f"{year}년",
                                "영업이익(억 원)": amount_hundred_mil
                            })
                
                # 결과 화면에 출력
                if results:
                    chart_df = pd.DataFrame(results)
                    
                    # 표 그리기
                    st.success(f"🎉 {company_name}의 데이터를 성공적으로 가져왔습니다!")
                    st.dataframe(chart_df, use_container_width=True)
                    
                    # 막대 그래프 그리기
                    st.bar_chart(data=chart_df, x="연도", y="영업이익(억 원)")
                else:
                    st.error("해당 기업의 영업이익 데이터를 찾을 수 없습니다. 상장 기업이 맞는지 확인해주세요.")
                    
            except Exception as e:
                st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
