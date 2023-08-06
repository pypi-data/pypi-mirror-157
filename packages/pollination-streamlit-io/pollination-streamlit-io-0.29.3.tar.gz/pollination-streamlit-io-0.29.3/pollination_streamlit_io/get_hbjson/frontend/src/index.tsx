import React from "react"
import ReactDOM from "react-dom"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks"
import GetHbjson from "./GetHbjson"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <GetHbjson />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
