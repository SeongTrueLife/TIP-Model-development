"""
[Model 5] LangGraph Builder

이 모듈은 개별적으로 구현된 7개의 노드를 하나의 Workflow로 조립합니다.
순차적 실행(Sequential Execution)을 통해 데이터의 의존성을 관리합니다.

Flow:
START -> [N1: Visual] -> [N2: Query] -> [N3: Retriever] -> [N0: Calibrator] 
      -> [N4: Judge] -> [N5: Weights] -> [N6: Calculator] -> END
"""

from langgraph.graph import StateGraph, END
from .state import AgentState

# Nodes Import
from .nodes.node_0_calibrator import score_calibrator
from .nodes.node_1_visual import node_1_visual
from .nodes.node_2_query_gen import node_2_query_gen
from .nodes.node_3_retriever import node_3_retriever
from .nodes.node_4_judge import node_4_judge
from .nodes.node_5_weight_mapper import weight_mapper
from .nodes.node_6_calculator import final_calculator

def create_model5_graph():
    """
    Model 5 LangGraph를 생성하고 컴파일합니다.
    """
    
    # 1. 그래프 초기화
    workflow = StateGraph(AgentState)

    # 2. 노드 등록 (Add Nodes)
    # Node names are used for edge definitions
    workflow.add_node("visual_describer", node_1_visual)       # N1
    workflow.add_node("query_generator", node_2_query_gen)     # N2
    workflow.add_node("legal_retriever", node_3_retriever)     # N3
    workflow.add_node("score_calibrator", score_calibrator)    # N0 (Moved here for better flow)
    workflow.add_node("legal_judge", node_4_judge)             # N4
    workflow.add_node("weight_mapper", weight_mapper)          # N5
    workflow.add_node("final_calculator", final_calculator)    # N6

    # 3. 엣지 연결 (Sequential Flow)
    # Start Point
    workflow.set_entry_point("visual_describer") 

    # Linear Pipeline
    workflow.add_edge("visual_describer", "query_generator")
    workflow.add_edge("query_generator", "legal_retriever")
    workflow.add_edge("legal_retriever", "score_calibrator") 
    
    # N0 -> N4: 모든 정보(이미지, 관념, 판례, 점수)가 모이는 시점
    workflow.add_edge("score_calibrator", "legal_judge")     
    
    workflow.add_edge("legal_judge", "weight_mapper")
    workflow.add_edge("weight_mapper", "final_calculator")
    
    # End Point
    workflow.add_edge("final_calculator", END)

    # 4. 컴파일 (Compile)
    app = workflow.compile()
    return app

# 외부 사용을 위한 싱글톤 객체 노출
app = create_model5_graph()
