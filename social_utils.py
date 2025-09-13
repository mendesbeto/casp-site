import streamlit as st

def display_social_media_links():
    st.markdown("""
        <div style="text-align: center;">
            <a href="https://www.instagram.com/caspparana?utm_source=qr&igsh=ZzR4YTA2ajRjaDQw" target="_blank">
                <img src="https://img.shields.io/badge/Instagram-%23E4405F.svg?style=for-the-badge&logo=Instagram&logoColor=white" alt="Instagram">
            </a>
            <a href="https://www.facebook.com/your_facebook_page" target="_blank">
                <img src="https://img.shields.io/badge/Facebook-%231877F2.svg?style=for-the-badge&logo=Facebook&logoColor=white" alt="Facebook">
            </a>
            <a href="https://www.twitter.com/your_twitter_handle" target="_blank">
                <img src="https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white" alt="Twitter">
            </a>
        </div>
    """, unsafe_allow_html=True)
