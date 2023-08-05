import sys

sys.path.append('D:\code\python\component-template\\template')

from streamlit_rightly_component import rightly_component, set_debug, init_component, modal
import streamlit as st

init_component()
set_debug()

def get_url():
    # 获取当前页面 url
    url = rightly_component(component_name='getUrl')
    return url

def render_dagre():
    col1, col2 = st.columns([2, 10])
    with col1:
        plan_info = {
            "name": "测试方案名称001",
            "start_date": "2022-04-25",
            "end_date": "2022-05-01",
            "shop_count": 4,
            "fee_cost": 123456,
            "predict_gmv": 123456,
        }
        plan_info_click = rightly_component(component_name='plan-ui/plan-info', data=plan_info)
    with col2:
        nodes = {
            'id': 'final',
            'name': 'final',
            'type': 'final',
            "value": 100,
            'children': [{
                "id": '5.pay_amt|item_id|biz_date|channel2:allchn',
                "name": "tb",
                "type": "platform",
                "value": 100,
                "children": [{
                    "id": "5.pay_amt|item_id|biz_date|channel2:allchn__190043425",
                    "name": "190043425",
                    "type": "shop",
                    "value": 100,
                    "children": [
                        {'id': '5.tb_adv_strategy__190043425','type': 'input'},
                        {'id': '5.tb_price_strategy__190043425','type': 'input'},
                        {'id': '5.pay_amt|item_id|biz_date|channel2:allchn__190043425', 'type': 'output'}
                    ]
                }]
            }]
        }

        edges = [
            {'source': '5.pay_amt|item_id|biz_date|channel2:allchn',
            'target': '5.pay_amt|item_id|biz_date|channel2:allchn__190043425'},
            {'source': '5.tb_adv_strategy__190043425',
            'target': '5.pay_amt|item_id|biz_date|channel2:allchn__190043425'},
            {'source': '5.tb_price_strategy__190043425',
            'target': '5.pay_amt|item_id|biz_date|channel2:allchn__190043425'},
            {'source': '5.pay_amt|item_id|biz_date|channel2:allchn', 'target': 'final'}
        ]

        dagre_click = rightly_component(component_name='Dag',
            data={"nodes": nodes, "edges": edges},
            default=None
        )

        if dagre_click and dagre_click["action"] == "shopClick":
            st.session_state['show_shop'] = dagre_click["data"]["node_id"]
        if dagre_click and dagre_click["action"] == "inputNodeClick" and dagre_click["value_is_change"]:
            st.session_state['open_modal'] = {
                "node": dagre_click["data"]["node_id"]
            }

        if st.session_state.get('show_shop'):
            darge_dag = rightly_component(component_name='dagre',
                data={"nodes":[{"id":"npc|item_id|biz_date|channel2:allchn__190043425","label":"客均件数"},{"id":"tb_price_strategy__190043425","label":"天猫商品定价策略"},{"id":"tb_adv_strategy__190043425","label":"天猫广告策略"},{"id":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","label":"天猫商品定价策略"},{"id":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","label":"天猫广告策略"},{"id":"ztc_upc__190043425","label":"ztcupc"},{"id":"pay_conv_rate|item_id|biz_date|channel:mtbsearch__190043425","label":"搜索支付转化率"},{"id":"mtbrecomm_uv__190043425","label":"推荐uv"},{"id":"ylmf_upc__190043425","label":"ylmfupc"},{"id":"mtbsearch_uv__190043425","label":"搜索uv"},{"id":"wxt_upc__190043425","label":"wxtupc"},{"id":"pay_conv_rate|item_id|biz_date|channel:cart__190043425","label":"购物车支付转化率"},{"id":"pay_conv_rate|item_id|biz_date|channel:mtbrecomm__190043425","label":"推荐支付转化率"},{"id":"ztc_uv__190043425","label":"ztc uv"},{"id":"ylmf_uv__190043425","label":"ylmf uv"},{"id":"wxt_uv__190043425","label":"wxt uv"},{"id":"allchn_cart_byr_cnt__190043425","label":"全渠道加购买家数"},{"id":"allchn_clt_byr_cnt__190043425","label":"全渠道加购买家数"},{"id":"cart_uv__190043425","label":"购物车引导UV"},{"id":"mytb_uv__190043425","label":"我的淘宝引导UV"},{"id":"uv|item_id|biz_date|channel2:allchn__190043425","label":"全渠道去重UV"},{"id":"pay_conv_rate|item_id|biz_date|channel2:allchn__190043425","label":"全渠道支付转化率"},{"id":"pay_conv_rate_allchn_lr__190043425","label":"全渠道去重转化率"},{"id":"pay_byr_cnt|item_id|biz_date|channel2:allchn__190043425","label":"全渠道买家数"},{"id":"pay_amt|item_id|biz_date|channel2:allchn__190043425","label":"成交金额"}],"edges":[{"source":"npc|item_id|biz_date|channel2:allchn__190043425","target":"pay_amt|item_id|biz_date|channel2:allchn__190043425"},{"source":"tb_price_strategy__190043425","target":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425"},{"source":"tb_adv_strategy__190043425","target":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ztc_upc__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:mtbsearch__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mtbrecomm_uv__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ylmf_upc__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mtbsearch_uv__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel2:allchn__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"wxt_upc__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:cart__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_amt|item_id|biz_date|channel2:allchn__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"cart_uv__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mytb_uv__190043425"},{"source":"tb_price_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:mtbrecomm__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ztc_upc__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ztc_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:mtbsearch__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mtbrecomm_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ylmf_upc__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mtbsearch_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel2:allchn__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"wxt_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"ylmf_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"wxt_upc__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:cart__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"cart_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"mytb_uv__190043425"},{"source":"tb_adv_strategy__shop_id_cate_spu_item_id_act_name_biz_date__190043425","target":"pay_conv_rate|item_id|biz_date|channel:mtbrecomm__190043425"},{"source":"ztc_upc__190043425","target":"ztc_uv__190043425"},{"source":"pay_conv_rate|item_id|biz_date|channel:mtbsearch__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"mtbrecomm_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"mtbrecomm_uv__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"mtbrecomm_uv__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"mtbrecomm_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"ylmf_upc__190043425","target":"ylmf_uv__190043425"},{"source":"mtbsearch_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"mtbsearch_uv__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"mtbsearch_uv__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"mtbsearch_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"wxt_upc__190043425","target":"wxt_uv__190043425"},{"source":"ztc_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"ztc_uv__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"ztc_uv__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"ztc_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"ylmf_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"ylmf_uv__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"ylmf_uv__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"ylmf_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"wxt_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"wxt_uv__190043425","target":"allchn_cart_byr_cnt__190043425"},{"source":"wxt_uv__190043425","target":"allchn_clt_byr_cnt__190043425"},{"source":"wxt_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"allchn_cart_byr_cnt__190043425","target":"cart_uv__190043425"},{"source":"allchn_clt_byr_cnt__190043425","target":"mytb_uv__190043425"},{"source":"cart_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"cart_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"mytb_uv__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"mytb_uv__190043425","target":"uv|item_id|biz_date|channel2:allchn__190043425"},{"source":"uv|item_id|biz_date|channel2:allchn__190043425","target":"pay_conv_rate|item_id|biz_date|channel2:allchn__190043425"},{"source":"uv|item_id|biz_date|channel2:allchn__190043425","target":"pay_conv_rate_allchn_lr__190043425"},{"source":"uv|item_id|biz_date|channel2:allchn__190043425","target":"pay_byr_cnt|item_id|biz_date|channel2:allchn__190043425"},{"source":"pay_conv_rate_allchn_lr__190043425","target":"pay_byr_cnt|item_id|biz_date|channel2:allchn__190043425"},{"source":"pay_byr_cnt|item_id|biz_date|channel2:allchn__190043425","target":"pay_amt|item_id|biz_date|channel2:allchn__190043425"}]},
                key="dagre2")
            if darge_dag and darge_dag["value_is_change"]:
                st.session_state['open_modal'] = {
                    "node": darge_dag["data"]["node_id"]
                }
        
    if st.session_state.get('open_modal', None):
        # 展示弹窗
        def close_fn():
            del st.session_state['open_modal']
            # widget_id = ctx.session_state._state._get_widget_id('dagre2')
            # ctx.session_state._state[widget_id] = None
            # print(ctx.session_state._state[widget_id])

        with modal(close_fn=close_fn) as container:
            with container:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(st.session_state['open_modal']["node"])
                with col2:
                    st.write('col 2')

render_dagre()