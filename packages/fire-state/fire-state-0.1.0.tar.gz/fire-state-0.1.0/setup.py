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
    'version': '0.1.0',
    'description': '',
    'long_description': '# Streamlit fire state\n\n[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mr-milk-streamlit-state-demohome-mqsp3p.streamlitapp.com/)\n![pypi version](https://img.shields.io/pypi/v/fire-state?color=black&logo=python&logoColor=white&style=flat)\n\nIn multipage streamlit app, one of the most headache issues\nis your state will not preserve if you switch between pages.\n\nThat\'s why fire-state is here for you.\n\n## Installation\n\n```shell\npip install fire-state\n```\n\n## Quick Start\n\n### Persist state in Form\n\n```python\nimport streamlit as st\nfrom fire_state import create_store, form_update\n\n# register your state with initiate values\n# the slot is an identifier for your state\nslot = "home_page"\nkey1, key2 = create_store(slot, [\n    ("state1", 5),\n    ("state2", 12),\n])\n\n# Now create a form using the generated keys\nwith st.form("my form"):\n    st.slider("State 1", 1, 10, step=1, key=key1)\n    st.slider("State 1", 10, 20, step=1, key=key2)\n    st.form_submit_button(label="Submit", on_click=form_update, args=(slot,))\n\n```\n\nGreat, just create a store and the pass the keys to your form, and you are good to go.\n\nIn production, it\'s recommended that you warp the `create_store` in a `@st.cache`\n\n```python\nimport streamlit as st\nfrom fire_state import create_store\n\nslot = "page"\n\n\n@st.cache\ndef init_state():\n    return create_store(slot, [\n        ("state1", 5),\n        ("state2", 12),\n    ])\n\n\nkey1, key2 = init_state()\n```\n\n### Persist state after form submission\n\nNow you get the idea of preserving state in form, how to preserve state \nof the action happen after the submission.\n\nFor example, you control how your line chart is drawn using a form.\n\nLet\'s do some set up first\n\n```python\nimport numpy as np\nimport pandas as pd\nimport streamlit as st\n\nnp.random.seed(0)\n\n@st.cache\ndef chart_data(line_count, data_size):\n    return pd.DataFrame(\n        np.random.randn(data_size, line_count),\n        columns=np.random.choice(list(\'abcdefghijlkmn\'), line_count))\n\n```\n\nThis is very similar to the first example, except we add other state\nfor the run button.\n\n```python\nfrom fire_state import create_store, get_state, set_state, form_update\n\nPAGE_SLOT = "Home_Page"\nkey1, key2, key3 = create_store(PAGE_SLOT, [\n    ("line_count", 2),\n    ("data_size", 13),\n    ("run", 0)\n])\n\nwith st.form(key="a form"):\n    line_count = st.slider("Line Count", 1, 10, step=1, key=key1)\n    data_size = st.slider("Data Size", 10, 20, step=1, key=key2)\n    run = st.form_submit_button(label="Run", on_click=form_update, args=(PAGE_SLOT,))\n\nprev_run_state = get_state(PAGE_SLOT, \'run\')\nif (prev_run_state != 0) or run:\n    data = chart_data(line_count, data_size)\n    st.line_chart(data)\n    # increase by 1 every time user click it\n    set_state(PAGE_SLOT, ("run", prev_run_state + 1))\n```\n\nThe idea is that the first time user open the page, they never click the run button,\nso it\'s value is 0, the number of time they click it. \nWhen it no longer is 0, that means user clicked it. The plot will always be rendering.\n\n\n### Working with non-form widget\n\nIt\'s strongly recommended that you work with form for user input.\nIt batches user events and won\'t refresh\nthe page at every `on_change` event.\n\nIf you are not working with user input. You need to update the state manually.\n\n```python\nfrom fire_state import create_store, \\\n    get_store, set_store, \\\n    get_state, set_state\n\nslot = "page"\ncreate_store(slot, [\n    ("state1", 1),\n    ("state2", 2),\n    ("state3", 3),\n    ("state4", 4)\n])\n```\n\nTo change a state value\n```python\nset_state(slot, ("state2", 3))\n```\n\nTo read a state value\n```python\nget_state(slot, "state2") # return 3\n```\n\nOr you can change and read in batch\n```python\nset_store(slot, [\n    ("state3", 13),\n    ("state4", 14)\n])\n\nget_store(slot) # return a dict\n```\n\n\n\n',
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
