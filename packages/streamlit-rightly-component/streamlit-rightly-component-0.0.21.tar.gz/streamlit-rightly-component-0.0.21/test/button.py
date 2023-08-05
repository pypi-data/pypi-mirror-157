import sys

sys.path.append('D:\code\python\component-template\\template')

from streamlit_rightly_component import rightly_component, set_debug, init_component, modal
import streamlit as st

set_debug()

res = st.button('点击展示浮层')
st.write(res)

# if st.button('点击展示浮层2') is True:
#   print('2222')

value = rightly_component(component_name='ClickDemo', data={"name": "hello", "value": 1})
st.write(value)

# print(ctx.session_state._state)