import streamlit as st
import yaml
from yaml.loader import SafeLoader


def initialize_session_state():
    if 'username' not in st.session_state:
        st.session_state.username = None


def login(config_file):
    initialize_session_state()
    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)

    st.title('User Login')

    # Check if the user is already logged in
    if st.session_state.username and config['credentials']['usernames'].get(st.session_state.username, {}).get(
            'logged_in', False):
        st.success(f"Welcome back, {st.session_state.username}!")
        return True

    form_name = st.text_input('Username')
    form_password = st.text_input('Password', type='password')
    form_action = st.selectbox('Action', ['Login', 'Register'])

    if form_action == 'Login':
        if st.button('Login'):
            if form_name in config['credentials']['usernames']:
                if form_password == config['credentials']['usernames'][form_name]['password']:
                    st.success('Login successful!')
                    config['credentials']['usernames'][form_name]['logged_in'] = True
                    with open(config_file, 'w') as file:
                        yaml.dump(config, file)
                    st.session_state.username = form_name
                    return True
                else:
                    st.error('Incorrect password!')
            else:
                st.error('Username not found!')

    elif form_action == 'Register':
        new_username = st.text_input('New Username')
        new_password = st.text_input('New Password', type='password')
        email = st.text_input('Email')

        if st.button('Register'):
            if new_username in config['credentials']['usernames']:
                st.error('Username already exists!')
            else:
                config['credentials']['usernames'][new_username] = {
                    'email': email,
                    'logged_in': False,
                    'name': new_username,
                    'password': new_password
                }
                with open(config_file, 'w') as file:
                    yaml.dump(config, file)
                st.success('Registration successful! Please log in.')
