import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import SendHbjson from "./SendHbjson"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <SendHbjson />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
