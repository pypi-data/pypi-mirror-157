.PHONY: upgrade-pollination-react

.PHONY: generate-frontend

.PHONY: dev-install-package

upgrade-pollination-react:
	yarn --cwd pollination_streamlit_io/get_geometry/frontend add pollination-react-io@latest
	yarn --cwd pollination_streamlit_io/get_hbjson/frontend add pollination-react-io@latest
	yarn --cwd pollination_streamlit_io/get_host/frontend add pollination-react-io@latest
	yarn --cwd pollination_streamlit_io/send_geometry/frontend add pollination-react-io@latest
	yarn --cwd pollination_streamlit_io/send_hbjson/frontend add pollination-react-io@latest
	yarn --cwd pollination_streamlit_io/send_results/frontend add pollination-react-io@latest

generate-frontend:
	yarn --cwd pollination_streamlit_io/get_geometry/frontend build
	yarn --cwd pollination_streamlit_io/get_hbjson/frontend build
	yarn --cwd pollination_streamlit_io/get_host/frontend build
	yarn --cwd pollination_streamlit_io/send_geometry/frontend build
	yarn --cwd pollination_streamlit_io/send_hbjson/frontend build
	yarn --cwd pollination_streamlit_io/send_results/frontend build
