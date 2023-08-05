from streamlit_rightly_component import rightly_component, set_debug, instance
import pandas as pd
import streamlit as st
from inspect import signature

MAX_SIZE = 128
CUSTOM_SESSION_CACHE = '_custom_session_cache'

def session_cache(fn):
  """ session 缓存，单次会话有效

  Args:
      fn (function): 要进行缓存的函数

  Returns:
      new_fn (function): 返回装饰后的新函数
  """
  if CUSTOM_SESSION_CACHE not in st.session_state:
    st.session_state[CUSTOM_SESSION_CACHE] = {
      "cache": {},
      "lst": []
    }

  sig = signature(fn)
  def wrapTheFunction(*args, **kwargs):
    bound_values = sig.bind(*args, **kwargs)
    key = bound_values.__str__()
    value = st.session_state[CUSTOM_SESSION_CACHE]['cache'].get(key)

    # 命中缓存
    if value is not None:
      return value

    # 最多缓存 128 个函数结果，包括不同入参
    if len(st.session_state[CUSTOM_SESSION_CACHE]['lst']) >= MAX_SIZE:
      oldkey = st.session_state[CUSTOM_SESSION_CACHE]['lst'].pop(0)
      if oldkey in st.session_state[CUSTOM_SESSION_CACHE]['cache']:
        st.session_state[CUSTOM_SESSION_CACHE]['cache'].pop(oldkey)

    result = fn(*args, **kwargs)
    st.session_state[CUSTOM_SESSION_CACHE]['lst'].append(key)
    st.session_state[CUSTOM_SESSION_CACHE]['cache'][key] = result
    return result

  return wrapTheFunction


def clear_session_cache():
  """ 清空所有缓存
  """
  st.session_state[CUSTOM_SESSION_CACHE] = {
    "cache": {},
    "lst": []
  }


@session_cache
def get_data(client_id):
  print('get_data]', client_id)
  return { "id": client_id }


if st.button('clear'):
  st.write('clear')
  # clear_session_cache()

st.write(get_data(1))

st.write(get_data(1))
st.write(get_data(2))