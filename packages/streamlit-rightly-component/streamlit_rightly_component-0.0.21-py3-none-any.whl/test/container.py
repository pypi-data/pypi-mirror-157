from streamlit_rightly_component import rightly_component, modal
import streamlit as st

def render_dagre():
    nodes = []
    edges = []

    nodes.append({
        "id": "Test1",
        "label": "Test1" 
    })

    nodes.append({
        "id": "Test2",
        "label": "Test2" 
    })

    nodes.append({
        "id": "Test3",
        "label": "Test3" 
    })

    edges.append({
        "source": "Test1",
        "target": "Test2", 
    })

    edges.append({
        "source": "Test1",
        "target": "Test3", 
    })

    rightly_component(component_name='dagre', data={ "nodes": nodes, "edges": edges })

def render_click_demo():
    # 渲染样式有问题
    st.subheader("Component with constant args")
    num_clicks = rightly_component(component_name="ClickDemo", data={'name': 'click-demo'},  default=0)
    st.markdown("You've clicked %s times!" % int(num_clicks))

def render_modal():
    open = st.button('点击展示浮层')
    st.button('点击展示浮层2')

    if 'open_modal' in st.session_state:
        open = st.session_state['open_modal']

    if open:
      st.session_state['open_modal'] = True

      def close_fn():
        del st.session_state['open_modal']

      with modal(close_fn=close_fn) as container:
          container.markdown('这是一个浮动')
          with container:
            col1, col2 = st.columns(2)
            with col1:
              render_click_demo()
            with col2:
              render_dagre()

render_modal()
