import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import GetGeometry from "./SendResults"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <GetGeometry />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
