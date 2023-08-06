# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fire_state']

package_data = \
{'': ['*']}

install_requires = \
['streamlit>=1.10.0,<2.0.0']

setup_kwargs = {
    'name': 'fire-state',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Streamlit fire state\n\n[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mr-milk-streamlit-state-demohome-mqsp3p.streamlitapp.com/)\n![pypi version](https://img.shields.io/pypi/v/fire-state?color=black&logo=python&logoColor=white&style=flat)\n\nIn a multipage streamlit app, one of the most headache issues \nis that your state is not preserved if you switch between pages.\n\nThat\'s why fire-state is here for you.\n\n## Installation\n\n```shell\npip install fire-state\n```\n\n## Quick Start\n\n### Persist state in Form\n\n```python\nimport streamlit as st\nfrom fire_state import create_store, form_update\n\n# Register state with initiate values in a slot\nslot = "home_page"\nkey1, key2 = create_store(slot, [\n    ("state1", 5),\n    ("state2", 12),\n])\n\n# Now create a form using the generated keys\nwith st.form("my form"):\n    st.slider("State 1", 1, 10, step=1, key=key1)\n    st.slider("State 1", 10, 20, step=1, key=key2)\n    st.form_submit_button(label="Submit", on_click=form_update, args=(slot,))\n\n```\n\nWhen you switch between pages, the states are preserved.\n\n### Persist state in any place\n\nYou need to control the state by yourself, using the `set_state` function.\n\n```python\nimport streamlit as st\nfrom fire_state import create_store, get_state, set_state\n\n\nslot = "home_page"\ncreate_store(slot, [\n    ("state1", 0),\n])\n\ndef increment():\n    prev = get_state(slot, "state1")\n    set_state(slot, ("state1", prev + 1))\n\n\nst.button("+1", on_click=increment)\nst.text(f"Value: {get_state(slot, \'state1\')}")\n```\n\n## Advanced Usage\n\n### Persist state after form submission\n\nIn this example, we have a form to control \nhow the line chart is drawn.\n\nLet\'s do some setup first\n\n```python\nimport numpy as np\nimport pandas as pd\nimport streamlit as st\n\nnp.random.seed(0)\n\n@st.cache\ndef chart_data(line_count, data_size):\n    return pd.DataFrame(\n        np.random.randn(data_size, line_count),\n        columns=np.random.choice(list(\'abcdefghijlkmn\'), line_count))\n\n```\n\nNow we can use fire state to record the user action.\n\nThe idea is that the first time user opens the page, they never click the run button,\nso the number of times they click a button is 0. When it no longer is 0, which means user clicked it. \nTherefore, the plot is rendered or updated (if chart data is changed).\n\n\n```python\nfrom fire_state import create_store, get_state, set_state, form_update\n\nPAGE_SLOT = "Home_Page"\nkey1, key2, key3 = create_store(PAGE_SLOT, [\n    ("line_count", 2),\n    ("data_size", 13),\n    ("run", 0)\n])\n\nwith st.form(key="a form"):\n    line_count = st.slider("Line Count", 1, 10, step=1, key=key1)\n    data_size = st.slider("Data Size", 10, 20, step=1, key=key2)\n    run = st.form_submit_button(label="Run", on_click=form_update, args=(PAGE_SLOT,))\n\nprev_run_state = get_state(PAGE_SLOT, \'run\')\nif (prev_run_state != 0) or run:\n    data = chart_data(line_count, data_size)\n    st.line_chart(data)\n    # increase by 1 every time user click it\n    set_state(PAGE_SLOT, ("run", prev_run_state + 1))\n```\n\n\n### Reset the state\n\nUse the `set_store` function to update states in a batch:\n\n```python\nimport streamlit as st\nfrom fire_state import create_store, \\\n    get_store, set_store, \\\n    get_state, set_state\n\nslot = "page"\ninit_state = [\n    ("state1", 1),\n    ("state2", 2),\n    ("state3", 3),\n]\ncreate_store(slot, init_state)\n\ndef reset():\n    set_store(slot, init_state)\n\nst.button("Reset", on_click=reset)\n```\n\nThe `set_store` and `get_store` functions allow you to\nmodify and get your state in a batch.\n\n\n## The Life Cycle of State\n\nThe state persists if you don\'t close or refresh the page. The state instance\nis only destroyed if you stop your app.\n',
    'author': 'Mr-Milk',
    'author_email': 'yb97643@um.edu.mo',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Mr-Milk/streamlit-state',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
