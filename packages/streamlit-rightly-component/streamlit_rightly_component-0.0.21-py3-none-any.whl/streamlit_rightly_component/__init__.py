import os
import streamlit.components.v1 as components
import streamlit as st

class RightlyComponent:
    def __init__(self):
        self._RELEASE = True
        self.url = 'http://localhost:3001'
        self._component_func = self.get_component_func()
    
    def set_debug(self, release = False, url = 'http://localhost:3001'):
        self._RELEASE = release
        self.url = url
        self._component_func = self.get_component_func()

    def get_component_func(self):
        if not self._RELEASE:
            _component_func = components.declare_component(
                # We give the component a simple, descriptive name ("my_component"
                # does not fit this bill, so please choose something better for your
                # own component :)
                "rightly_component",
                # Pass `url` here to tell Streamlit that the component will be served
                # by the local dev server that you run via `npm run start`.
                # (This is useful while your component is in development.)
                url=self.url,
            )
        else:
            # When we're distributing a production version of the component, we'll
            # replace the `url` param with `path`, and point it to to the component's
            # build directory:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            build_dir = os.path.join(parent_dir, "frontend/build")
            _component_func = components.declare_component("rightly_component", path=build_dir)
        return _component_func

    def init_event(self):
        components.html('''
            <script>
                // hide-iframe
                let listerens = [];
                window.parent.addEventListener('message', (event) => {
                    const { type } = event.data;
                    console.log('[event]', event);
                    if (type === 'component-message-dispatch') {
                        // 广播
                        listerens.forEach(listeren => listeren.postMessage(event.data, '*'))
                    }
                    if (type === 'component-message-listeren') {
                        listerens.push(event.source);
                    }
                });
                const iframes = window.parent.document.getElementsByTagName('iframe');
                Array.from(iframes).forEach(iframe => {
                    const srcdoc = iframe.srcdoc;
                    if (srcdoc.includes('hide-iframe')) {
                        iframe.parentNode.style.display = 'none';
                    }
                })
            </script>
        ''')

    def init_style(self):
        components.html('''
            <script>
                // hide-iframe
                const d = window.parent.document;
                d.getElementsByClassName('main')[0].style.overflow = 'hidden';
                d.getElementsByTagName('header')[0].style.display = 'none';
                d.getElementsByTagName('footer')[0].style.display = 'none';
                d.body.style.height = '100%';
                d.body.parentElement.style.height = '100%';
                const container = d.getElementsByClassName('block-container')[0];
                container.style.maxWidth = '100%';
                container.style.padding = '0';
                
                const iframes = window.parent.document.getElementsByTagName('iframe');
                Array.from(iframes).forEach(iframe => {
                    const srcdoc = iframe.srcdoc;
                    if (srcdoc.includes('hide-iframe')) {
                        iframe.parentNode.style.display = 'none';
                    }
                })

                window.parent.addEventListener('message', (event) => {
                    const { type } = event.data;
                    if (type === 'get_client_height') {
                        // 广播
                        event.source.postMessage({
                            type: 'set_height',
                            data: window.parent.document.body.clientHeight,
                        }, '*')
                    }
                    if (type === 'get_iframe') {
                        const iframes = window.parent.document.getElementsByTagName('iframe');
                        const filter = Array.from(iframes).filter(iframe => {
                            return iframe.contentWindow == event.source
                        });
                        if (filter[0]) {
                            const doc = filter[0];
                            const fn = new Function('doc', event.data.data);
                            fn(doc);
                        }
                    }
                });
            </script>
        ''')

    def rightly_component(self, component_name, data = {}, default = {}, key = None, events = None, once=False):
        component_value = self._component_func(componentName=component_name, data=data, key=key or component_name, default=default, events=events)
        # We could modify the value returned from the component if we wanted.
        # There's no need to do this in our simple example - but it's an option.
        if once is True and 'time' in component_value:
            # 只返回一次结果
            t = st.session_state.get(f'_component_value_{key}', None)
            if t and t == component_value['time']:
                return None
            else:
                st.session_state[f'_component_value_{key}'] = component_value["time"]
                return component_value

        return component_value


instance = RightlyComponent()

def rightly_component(component_name, data = {}, default = None, key = None, events=None, once=False):
    """ 渲染自定义组件

    Args:
        component_name (string): 组件名称
        data (dict, optional): 传给组件的参数. Defaults to {}.
        default (dict, optional): 默认返回值. Defaults to None.
        key (string, optional): 别名，默认与组件名称一致. Defaults to None.
        events (dict, optional): 事件订阅，组件间数据传递. Defaults to None.
        once (bool, optional): 只触发一次返回通知，适用于提交等操作. Defaults to False.

    Returns:
        dict: 组件操作返回结果
    """
    return instance.rightly_component(component_name, data, default, key, events, once)

def set_debug(release = False, url = 'http://localhost:3001'):
    return instance.set_debug(release, url)

def init_component():
    instance.init_event()
    instance.init_style()

class modal:
    def __init__(self, close_fn = None):
        self.action = None
        self.container = None
        self.content_container = None
        self.close_fn = close_fn

    def __enter__(self):
        self.container = st.container()
        self.container.markdown('<div id="modal-mask"></div>', unsafe_allow_html=True)
        with self.container:
          components.html('''
              <script>
                  var d = window.parent.document;
                  var b = d.getElementById('modal-mask');
                  var c = b.parentNode.parentNode.parentNode.parentNode;
                  c.id += 'modal';
                  console.log(c.className)
              </script>
          ''')
        self.container.write('''<style>
            .appview-container > section > div > div > div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
                display: none;
            }
            
            #modal {
                display: block;
                position: absolute;
                left: 0;
                top: 0;
                z-index: 900;
                width: 100%;
                height: 100%;
            }

            #modal > div:nth-child(-n + 3) {
                display: none;
            }

            #modal > div:first-child {
                display: block;
                width: 100%;
                height: 100%;
                background: rgba(333, 333, 333, 0.5);
            }

            #modal > .element-container:last-child {
                display: block;
                position: absolute;
                left: calc(50% + 200px);
                top: 50%;
                z-index: 2;
            }

            #modal > div:nth-child(4) > div > div {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div > div {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div > iframe {
              width: 100%;
            }

            #modal > div:nth-child(4) > div > div:last-child {
              position: absolute;
              left: calc(100% - 42px);
              top: 6px;
            }

            #modal > div:nth-child(4) > div {
                display: block;
                position: absolute;
                width: 100%;
                left: 0;
                height: 80%;
                bottom: 0;
                z-index: 1;
                background: #fff;
                padding: 20px;
                overflow-x: hidden;
                overflow-y: auto;
            }
            
            </style>''', unsafe_allow_html=True)
        self.content_container = self.container.container()
        return self.content_container

    def __exit__(self, exc_type, exc_val, exc_tb):
        close = self.content_container.button('X', kwargs={"id": "close"})
        if close:
            self.container.write('''<style>#modal {
                    display: none;
                }</style>''', unsafe_allow_html=True)
            if self.close_fn:
                self.close_fn()

            return {"action": "close"}
        return None
