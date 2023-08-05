from streamlit_rightly_component import rightly_component, set_debug, instance
import pandas as pd
import streamlit as st

set_debug(False, 'http://127.0.0.1:3001')

d = {'id': [1, 2], 'value': [3, 4]}
if 'df' in st.session_state:
  df = pd.DataFrame(data=st.session_state['df'])
else:
  df = pd.DataFrame(data=d)
# df = pd.DataFrame(data=d)

result = rightly_component(component_name="LuckSheet", data={
  "data": df.to_json(),
})

rightly_component(component_name="LuckSheet", data={
  "data": df.to_json(),
}, key='sheet2')

if result and result['action'] == 'onSave':
  df2 = pd.DataFrame(data=result['data']['data'])
  st.session_state['df'] = result['data']['data']