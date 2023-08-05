import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import SendGeometry from "./SendGeometry"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <SendGeometry />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
